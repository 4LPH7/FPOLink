"""Open Government Data (data.gov.in) Ingestion CLI Harness.

Provides programmatic interaction with the data.gov.in Agmarknet API:
1. Check key configuration and API endpoint availability
2. Ingest live price data for Tamil Nadu / Erode markets
3. Support local JSON fixture ingestion for CI and offline testing
4. Store price records via IngestionService with SHA-256 deduplication
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path so app imports resolve
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings  # noqa: E402
from app.data_sources.base import PriceRecord  # noqa: E402
from app.data_sources.ogd import OGD_BASE_URL, OGDProvider  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.services.ingestion import IngestionService  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ogd_ingest")


def check_status(api_key: Optional[str] = None, resource_id: Optional[str] = None) -> bool:
    """Check configuration and connectivity for OGD."""
    key = api_key if api_key is not None else settings.OGD_API_KEY
    res_id = resource_id if resource_id is not None else settings.OGD_RESOURCE_ID

    print("\n" + "=" * 60)
    print(" OPEN GOVERNMENT DATA (DATA.GOV.IN) STATUS CHECK")
    print("=" * 60)
    print(f"Base URL: {OGD_BASE_URL}")
    print(f"Resource ID: {res_id}")
    print(
        f"API Key Configured: {'Yes' if key else 'No'} ({key[:8]}... if present)"
        if key
        else "API Key Configured: No"
    )

    if not key:
        print("\nNote: OGD API key is missing. You can:")
        print("1. Obtain a free API key at: https://data.gov.in")
        print("2. Set OGD_API_KEY in your .env or pass via --api-key")
        print(
            "3. Test ingestion using synthetic fixture with --fixture tests/fixtures/ogd_turmeric_response_synthetic.json"
        )
        return False

    return True


def load_fixture_records(fixture_path: Path, crop: str, district: str) -> List[PriceRecord]:
    """Parse records from a local JSON fixture using OGDProvider's record parser."""
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    provider = OGDProvider(api_key="test-fixture-key")
    records: List[PriceRecord] = []
    for item in data.get("records", []):
        parsed = provider._parse_record(item, crop, district)
        if parsed:
            records.append(parsed)
    return records


def run_ingest(
    crop: str = "Turmeric",
    district: str = "Erode",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    api_key: Optional[str] = None,
    resource_id: Optional[str] = None,
    fixture_path: Optional[str] = None,
    dry_run: bool = False,
) -> int:
    """Fetch/load records and store them in the database."""
    print(f"\nIngesting OGD price data for {crop} in {district}...")

    records: List[PriceRecord] = []
    if fixture_path:
        path = Path(fixture_path)
        if not path.is_absolute():
            path = backend_dir / path
        if not path.exists():
            print(f"Error: Fixture file not found: {path}")
            return 1
        print(f"Loading from synthetic fixture: {path.name}")
        records = load_fixture_records(path, crop, district)
    else:
        provider = OGDProvider(api_key=api_key, resource_id=resource_id)
        if not provider.is_available():
            print(
                "Error: OGD_API_KEY is not set. Use --fixture to ingest synthetic data or set OGD_API_KEY."
            )
            return 1
        records = provider.fetch_prices(
            crop=crop,
            district=district,
            start_date=start_date,
            end_date=end_date,
        )

    print(f"Parsed {len(records)} price records.")
    for r in records[:5]:
        print(
            f"  - [{r.price_date}] {r.crop_name} ({r.variety_name or 'std'}) @ {r.market_name}: "
            f"Modal=₹{r.modal_price} (raw: {r.raw_price} {r.raw_unit})"
        )
    if len(records) > 5:
        print(f"  ... and {len(records) - 5} more records")

    if dry_run:
        print("\nDry-run active. Records were parsed but not saved to database.")
        return 0

    if not records:
        print("No records to persist.")
        return 0

    db = SessionLocal()
    try:
        service = IngestionService(db)
        stored_count = service._store_records(records)
        print(f"\nSuccessfully stored {stored_count} records through the 8-stage pipeline.")
    finally:
        db.close()

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="OGD Mandi Ingestion CLI Harness")
    parser.add_argument(
        "--check-status", action="store_true", help="Check OGD API key and endpoint status"
    )
    parser.add_argument(
        "--crop", default="Turmeric", help="Crop commodity name (default: Turmeric)"
    )
    parser.add_argument("--district", default="Erode", help="District name (default: Erode)")
    parser.add_argument("--api-key", default=None, help="Override OGD API key")
    parser.add_argument("--resource-id", default=None, help="Override OGD resource ID")
    parser.add_argument(
        "--fixture", default=None, help="Path to JSON fixture file for offline ingestion"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse records without saving to database"
    )
    parser.add_argument("--start-date", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.check_status:
        check_status(api_key=args.api_key, resource_id=args.resource_id)
        sys.exit(0)

    s_date = datetime.strptime(args.start_date, "%Y-%m-%d").date() if args.start_date else None
    e_date = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else None

    exit_code = run_ingest(
        crop=args.crop,
        district=args.district,
        start_date=s_date,
        end_date=e_date,
        api_key=args.api_key,
        resource_id=args.resource_id,
        fixture_path=args.fixture,
        dry_run=args.dry_run,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
