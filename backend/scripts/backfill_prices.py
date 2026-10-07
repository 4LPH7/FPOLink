"""Price Backfill & Calendar Gap Report CLI.

Backfills historical price observations for key commodities (Turmeric, Banana, etc.)
from verified CSV datasets, CEDA, or OGD sources, and produces a gap analysis report.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path so app imports resolve
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.data_sources.base import PriceRecord  # noqa: E402
from app.data_sources.manual import ManualProvider  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.services.ingestion import IngestionService  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backfill_prices")

DEFAULT_DATASET = backend_dir.parent / "ml" / "datasets" / "erode_agmarknet_historical_2026.csv"


def generate_gap_report(
    records: List[PriceRecord],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    """Analyze date continuity and print a mandi observation gap report."""
    if not records:
        print("\n[Gap Report] No records available for gap analysis.")
        return

    dates_present = [r.price_date for r in records]
    actual_start = start_date or min(dates_present)
    actual_end = end_date or max(dates_present)

    # Group observations by (crop, market) -> set of dates
    series_dates: Dict[Tuple[str, str], Set[date]] = defaultdict(set)
    for r in records:
        if actual_start <= r.price_date <= actual_end:
            series_dates[(r.crop_name.lower(), r.market_name.lower())].add(r.price_date)

    # Generate full expected trading calendar (Mon-Sat, skipping Sunday)
    all_days: List[date] = []
    trading_days: List[date] = []
    curr = actual_start
    while curr <= actual_end:
        all_days.append(curr)
        if curr.weekday() != 6:  # 6 is Sunday
            trading_days.append(curr)
        curr += timedelta(days=1)

    print("\n" + "=" * 70)
    print(" MANDI HISTORICAL OBSERVATION GAP REPORT")
    print("=" * 70)
    print(f"Date Range Analysed : {actual_start} to {actual_end}")
    print(f"Total Calendar Days : {len(all_days)} days")
    print(f"Expected Trading Days: {len(trading_days)} days (Mon-Sat, excluding Sundays)")
    print(f"Total Records Parsed: {len(records)}")
    print("-" * 70)

    for (crop, market), observed in sorted(series_dates.items()):
        obs_trading = observed.intersection(set(trading_days))
        coverage_pct = (len(obs_trading) / len(trading_days) * 100) if trading_days else 0
        missing = sorted(set(trading_days) - observed)

        print(f"\nSeries: {crop.capitalize()} @ {market.capitalize()}")
        print(
            f"  - Observed Trading Days: {len(obs_trading)} / {len(trading_days)} ({coverage_pct:.1f}% coverage)"
        )
        print(
            f"  - Total Observations   : {len(observed)} (incl. {len(observed - set(trading_days))} weekend records)"
        )
        if missing:
            if len(missing) <= 10:
                print(
                    f"  - Missing Dates ({len(missing)}): {', '.join(d.isoformat() for d in missing)}"
                )
            else:
                first_few = ", ".join(d.isoformat() for d in missing[:6])
                last_few = ", ".join(d.isoformat() for d in missing[-2:])
                print(f"  - Missing Dates ({len(missing)}): {first_few} ... {last_few}")
        else:
            print("  - Missing Dates: None! 100% complete coverage.")

    print("=" * 70 + "\n")


def run_backfill(
    source: str = "csv",
    csv_path: Optional[str] = None,
    crops: Optional[List[str]] = None,
    district: str = "Erode",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    dry_run: bool = False,
) -> int:
    """Execute backfill and print gap report."""
    target_crops = [c.strip().lower() for c in crops] if crops else ["turmeric", "banana"]
    records: List[PriceRecord] = []

    print(f"\nStarting price backfill [Source: {source}]")
    print(f"Target Crops   : {', '.join(target_crops)}")
    print(f"Target District: {district}")

    if source.lower() == "csv":
        file_to_load = Path(csv_path) if csv_path else DEFAULT_DATASET
        if not file_to_load.is_absolute():
            file_to_load = backend_dir.parent / file_to_load
        if not file_to_load.exists():
            print(f"Error: CSV dataset not found at {file_to_load}")
            return 1
        print(f"Loading from CSV: {file_to_load}")
        all_csv_records = ManualProvider.load_csv_file(file_to_load, default_district=district)
        # Filter by requested crops and dates
        for r in all_csv_records:
            if r.crop_name.lower() in target_crops or any(
                c in r.crop_name.lower() for c in target_crops
            ):
                if start_date and r.price_date < start_date:
                    continue
                if end_date and r.price_date > end_date:
                    continue
                records.append(r)

    elif source.lower() == "ceda":
        from app.data_sources.ceda_api import CEDAAPIProvider

        provider = CEDAAPIProvider()
        if not provider.is_available():
            print("Error: CEDA_API_KEY is not set.")
            return 1
        for crop_name in target_crops:
            fetched = provider.fetch_prices(
                crop=crop_name,
                district=district,
                start_date=start_date,
                end_date=end_date,
            )
            records.extend(fetched)

    elif source.lower() == "ogd":
        from app.data_sources.ogd import OGDProvider

        provider = OGDProvider()
        if not provider.is_available():
            print("Error: OGD_API_KEY is not set.")
            return 1
        for crop_name in target_crops:
            fetched = provider.fetch_prices(
                crop=crop_name,
                district=district,
                start_date=start_date,
                end_date=end_date,
            )
            records.extend(fetched)

    else:
        print(f"Unknown source '{source}'. Choose 'csv', 'ceda', or 'ogd'.")
        return 1

    print(f"Loaded {len(records)} records.")

    # Generate Mandi Price Gap Report
    generate_gap_report(records, start_date=start_date, end_date=end_date)

    if dry_run:
        print("Dry run complete. No changes were committed to database.")
        return 0

    if not records:
        print("No records to persist.")
        return 0

    db = SessionLocal()
    try:
        service = IngestionService(db)
        stored_count = service._store_records(records)
        print(
            f"Database Ingestion: Successfully stored/updated {stored_count} records through 8-stage pipeline."
        )
    finally:
        db.close()

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="FPOLink Mandi Price Backfill & Gap Analysis CLI")
    parser.add_argument(
        "--source", default="csv", choices=["csv", "ceda", "ogd"], help="Data source provider"
    )
    parser.add_argument(
        "--csv-file", default=None, help="Path to CSV file (defaults to erode historical dataset)"
    )
    parser.add_argument(
        "--crops",
        default="turmeric,banana",
        help="Comma-separated crops (default: turmeric,banana)",
    )
    parser.add_argument("--district", default="Erode", help="District name (default: Erode)")
    parser.add_argument("--start-date", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse and analyze gaps without persisting to DB"
    )

    args = parser.parse_args()

    s_date = datetime.strptime(args.start_date, "%Y-%m-%d").date() if args.start_date else None
    e_date = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else None
    crop_list = [c.strip() for c in args.crops.split(",") if c.strip()]

    code = run_backfill(
        source=args.source,
        csv_path=args.csv_file,
        crops=crop_list,
        district=args.district,
        start_date=s_date,
        end_date=e_date,
        dry_run=args.dry_run,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
