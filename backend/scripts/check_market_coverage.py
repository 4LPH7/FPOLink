"""Market price data coverage analyzer for FPOLink TN.

Checks monthly price record density per market for a given crop and district.
Answers whether Erode-area markets report regularly or sparsely for ML forecasting.

Usage:
    python backend/scripts/check_market_coverage.py [--crop CROP] [--district DISTRICT]
"""

import argparse
import logging
import os
import sys
from typing import List, Tuple

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text

from app.database import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def check_coverage(crop: str = "turmeric", district: str = "Erode", db=None) -> List[Tuple]:
    """Execute monthly coverage query across markets."""
    query = text(
        """
        SELECT
            date_trunc('month', p.price_date)::date AS month,
            m.name AS market_name,
            COUNT(DISTINCT p.price_date) AS record_count
        FROM market_prices p
        JOIN markets m ON m.id = p.market_id
        JOIN crops c ON c.id = p.crop_id
        WHERE c.name ILIKE :crop_pattern
          AND m.district ILIKE :district_pattern
          AND p.source IN ('ceda', 'ogd', 'agmarknet')
        GROUP BY 1, 2
        ORDER BY 1, 2;
        """
    )

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        results = db.execute(
            query,
            {
                "crop_pattern": f"{crop}%",
                "district_pattern": f"{district}%",
            },
        ).fetchall()
        return results
    finally:
        if should_close:
            db.close()


def print_coverage_report(results: List[Tuple], crop: str, district: str):
    """Format and print coverage statistics and advisory."""
    print("=" * 70)
    print("FPOLink TN — Market Price Coverage Audit")
    print(f"Crop: {crop} | District: {district}")
    print("=" * 70)

    if not results:
        print(f"\n[WARNING] No records found for '{crop}' in '{district}'.")
        print("  - If this is a fresh setup, run data backfill:")
        print(f"    python backend/scripts/backfill_ceda.py --crop {crop} --district {district}")
        print("  - Or verify data ingestion status in 'ingestion_logs'.\n")
        return

    # Header
    print(f"{'Month':<12} | {'Market Name':<35} | {'Count':<8}")
    print("-" * 70)

    total_records = 0
    markets = set()
    months = set()
    sparse_months = 0

    for row in results:
        month_str = str(row[0])[:7] if row[0] else "N/A"
        market_name = str(row[1])
        count = int(row[2])

        total_records += count
        markets.add(market_name)
        months.add(month_str)
        if count < 5:
            sparse_months += 1

        print(f"{month_str:<12} | {market_name:<35} | {count:<8}")

    print("-" * 70)
    print("Summary:")
    print(f"  Total records:      {total_records}")
    print(f"  Distinct markets:   {len(markets)} ({', '.join(sorted(markets))})")
    print(f"  Distinct months:    {len(months)} (from {min(months)} to {max(months)})")
    avg_per_month = total_records / max(len(months), 1)
    print(f"  Avg records/month:  {avg_per_month:.1f}")

    if sparse_months > 0:
        print(f"\n[ADVISORY] {sparse_months} market-month periods have fewer than 5 records.")
        print("  Recommendation for ML: Use global LightGBM model pooling across related")
        print("  mandis rather than standalone per-market ARIMA/Prophet models.")
    else:
        print("\n[OK] Data frequency is sufficient for regular time-series forecasting.")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Check market price coverage and reporting frequency"
    )
    parser.add_argument(
        "--crop", type=str, default="turmeric", help="Crop name (default: turmeric)"
    )
    parser.add_argument(
        "--district", type=str, default="Erode", help="District name (default: Erode)"
    )
    args = parser.parse_args()

    try:
        results = check_coverage(crop=args.crop, district=args.district)
        print_coverage_report(results, crop=args.crop, district=args.district)
    except Exception as e:
        logger.error(f"Error querying market coverage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
