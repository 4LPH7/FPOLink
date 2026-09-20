"""CEDA Historical Data Backfill Script.

Loads historical agricultural market prices from CEDA Agri-Market dataset
(Ashoka University) into the FPOLink database.

Usage:
    python scripts/backfill_ceda.py [--csv-path PATH] [--crop CROP] [--district DISTRICT]

The CEDA dataset provides:
- 300+ commodities across 2,700+ mandis
- Data from 2000 to present (updated monthly)
- Fields: State, District, Market, Commodity, Variety, Grade, Min/Max/Modal Price
- Prices in Rs per quintal

Download the dataset from CEDA's data portal before running this script.
Place the CSV file in ml/datasets/
"""

import argparse
import logging
import os
import sys
from datetime import date

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data_sources.ceda import CEDAProvider
from app.database import SessionLocal, engine
from app.models.base import Base
from app.services.ingestion import IngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Backfill CEDA historical data")
    parser.add_argument(
        "--csv-path", type=str, default="ml/datasets", help="Path to CEDA CSV file or directory"
    )
    parser.add_argument("--crop", type=str, default="turmeric", help="Crop to backfill")
    parser.add_argument("--district", type=str, default="Erode", help="District to filter")
    parser.add_argument("--start-date", type=str, default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Source tag for records (default: auto-detect 'ceda' or 'ceda_synthetic')",
    )
    args = parser.parse_args()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("FPOLink TN — CEDA Historical Data Backfill")
    print("=" * 60)
    print(f"Crop: {args.crop}")
    print(f"District: {args.district}")
    print(f"Data path: {args.csv_path}")

    # Parse dates
    start = date.fromisoformat(args.start_date) if args.start_date else None
    end = date.fromisoformat(args.end_date) if args.end_date else None

    # Fetch from CEDA
    provider = CEDAProvider(data_dir=args.csv_path, source_name=args.source)
    records = provider.fetch_prices(
        crop=args.crop,
        district=args.district,
        start_date=start,
        end_date=end,
    )

    if not records:
        print("\nNo records found. Make sure:")
        print(f"  1. CEDA CSV file exists in {args.csv_path}/")
        print(f"  2. The CSV contains data for '{args.crop}' in '{args.district}'")
        print("  3. Download from: https://agrimarket.ceda.ashoka.edu.in/")
        return

    print(f"\nFound {len(records)} records from CEDA")
    print(f"Date range: {records[-1].price_date} to {records[0].price_date}")

    # Store in database
    db = SessionLocal()
    try:
        service = IngestionService(db)
        stored = service._store_records(records)
        print(f"\n✓ Stored {stored} new records in database")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("✓ CEDA backfill complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
