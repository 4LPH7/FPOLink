"""Ingest live Agmarknet mandi market data from MandiPrices portal into FPOLink.

Sources verified Government of India Agmarknet data across 461 Tamil Nadu markets.
Supports Western Tamil Nadu focus (Erode, Coimbatore, Salem, Namakkal, etc.) or statewide ingestion.

Usage:
    python backend/scripts/ingest_mandiprices_live.py [--crops turmeric,banana,coconut] [--districts Erode] [--statewide]
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data_sources.mandiprices import MandiPricesProvider
from app.database import SessionLocal
from app.models.data_quality import IngestionRun
from app.models.ingestion_log import IngestionLog
from app.services.ingestion import IngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mandiprices_ingest")

DEFAULT_WESTERN_TN_DISTRICTS = [
    "Erode",
    "Coimbatore",
    "Salem",
    "Namakkal",
    "Dharmapuri",
    "Thirupur",
    "Dindigul",
    "Karur",
]

DEFAULT_PILOT_CROPS = [
    "turmeric",
    "banana",
    "coconut",
    "tomato",
    "tapioca",
    "maize",
    "onion",
    "green chilli",
    "ladies finger",
    "brinjal",
    "paddy",
]


def ingest_mandiprices(
    crops: Optional[List[str]] = None,
    districts: Optional[List[str]] = None,
    statewide: bool = False,
    source_name: str = "agmarknet",
) -> dict:
    """Run MandiPrices Agmarknet ingestion pipeline."""
    db = SessionLocal()
    provider = MandiPricesProvider()
    provider.source_name = source_name
    service = IngestionService(db)

    selected_crops = crops or DEFAULT_PILOT_CROPS
    target_districts = ["all"] if statewide else (districts or DEFAULT_WESTERN_TN_DISTRICTS)

    start_time = datetime.now(timezone.utc)
    district_label = "statewide" if statewide else ", ".join(target_districts[:3])

    ingestion_run = IngestionRun(
        source_code=source_name,
        status="running",
        district=district_label,
        records_fetched=0,
        records_ingested=0,
        started_at=start_time,
    )
    db.add(ingestion_run)
    db.commit()

    total_fetched = 0
    total_stored = 0
    crop_stats = {}

    print("=" * 75)
    print(" FPOLINK AGMARKNET LIVE MANDI PRICE INGESTION")
    print(f" Source:      {source_name} (data.gov.in / Agmarknet)")
    print(f" Coverage:    {'All Tamil Nadu Mandis' if statewide else ', '.join(target_districts)}")
    print(f" Crops:       {', '.join(selected_crops)}")
    print("=" * 75)

    try:
        for crop_name in selected_crops:
            crop_records = []
            if statewide:
                records = provider.fetch_prices(crop=crop_name, district="all")
                crop_records.extend(records)
            else:
                for dist in target_districts:
                    records = provider.fetch_prices(crop=crop_name, district=dist)
                    crop_records.extend(records)

            total_fetched += len(crop_records)

            # Store records through 8-stage IngestionService pipeline
            stored_count = service._store_records(crop_records, ingestion_run_id=ingestion_run.id)
            total_stored += stored_count

            if crop_records:
                prices = [r.modal_price for r in crop_records]
                crop_stats[crop_name] = {
                    "fetched": len(crop_records),
                    "stored": stored_count,
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices),
                    "dates": sorted(list({r.price_date.isoformat() for r in crop_records})),
                }

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Update IngestionRun
        ingestion_run.records_fetched = total_fetched
        ingestion_run.records_ingested = total_stored
        ingestion_run.status = "success" if total_stored > 0 else "failed"
        ingestion_run.completed_at = datetime.now(timezone.utc)

        # Legacy IngestionLog
        log_entry = IngestionLog(
            source=source_name,
            records_fetched=total_fetched,
            records_stored=total_stored,
            errors=0,
            duration_seconds=duration,
        )
        db.add(log_entry)
        db.commit()

        # Print detailed report
        print(
            f"\n{'Crop':<16} | {'Fetched':<8} | {'Stored/Updated':<15} | {'Price Range (₹/kg)':<20} | {'Dates'}"
        )
        print("-" * 75)
        for cname, s in crop_stats.items():
            price_range = f"₹{s['min']:.2f} - ₹{s['max']:.2f}"
            dates_str = ", ".join(s["dates"][-2:])
            print(
                f"{cname:<16} | {s['fetched']:<8} | {s['stored']:<15} | {price_range:<20} | {dates_str}"
            )

        print("-" * 75)
        print(f"Total Records Fetched:   {total_fetched}")
        print(f"Total Records Ingested:  {total_stored}")
        print(f"Duration:                {duration:.2f}s")
        print(f"Ingestion Run UUID:      {ingestion_run.id}")
        print("=" * 75)

        return {
            "status": "success",
            "records_fetched": total_fetched,
            "records_stored": total_stored,
            "duration": duration,
            "run_id": str(ingestion_run.id),
        }

    except Exception as e:
        db.rollback()
        logger.exception("Ingestion failed")
        ingestion_run.status = "failed"
        ingestion_run.errors = [str(e)]
        ingestion_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Agmarknet / MandiPrices live commodity prices"
    )
    parser.add_argument(
        "--crops",
        type=str,
        default=None,
        help="Comma-separated crops (e.g. turmeric,banana,coconut,tomato)",
    )
    parser.add_argument(
        "--districts",
        type=str,
        default=None,
        help="Comma-separated districts (e.g. Erode,Coimbatore,Salem)",
    )
    parser.add_argument(
        "--statewide",
        action="store_true",
        help="Ingest all mandis across all Tamil Nadu districts",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="agmarknet",
        help="Source tag to record (default: agmarknet)",
    )
    args = parser.parse_args()

    crop_list = [c.strip() for c in args.crops.split(",")] if args.crops else None
    district_list = [d.strip() for d in args.districts.split(",")] if args.districts else None

    ingest_mandiprices(
        crops=crop_list,
        districts=district_list,
        statewide=args.statewide,
        source_name=args.source,
    )


if __name__ == "__main__":
    main()
