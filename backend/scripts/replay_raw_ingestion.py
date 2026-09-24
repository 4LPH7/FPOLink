"""Raw Ingestion Replay Harness.

Re-processes immutable raw JSON payloads stored in `raw_ingest` through
the normalization and quality pipeline without contacting external APIs.
Guarantees idempotency and data reproducibility.
"""

import argparse
import logging
import os
import sys
from datetime import date
from decimal import Decimal

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.data_sources.base import PriceRecord
from app.models.raw_ingest import RawIngest
from app.services.ingestion import IngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("replay_raw_ingestion")


def replay_raw_records(
    db_session: Session = None,
    source: str = None,
    unprocessed_only: bool = False,
    limit: int = 100,
    dry_run: bool = False,
) -> dict:
    """Replay stored raw ingest payloads."""
    db = db_session or SessionLocal()
    should_close = db_session is None
    try:
        query = db.query(RawIngest)
        if source:
            query = query.filter(RawIngest.source == source)
        if unprocessed_only:
            query = query.filter(RawIngest.processed.is_(False))

        records_to_replay = query.order_by(RawIngest.ingested_at.asc()).limit(limit).all()
        total_found = len(records_to_replay)
        logger.info(f"Found {total_found} raw ingest records to replay (source={source or 'all'}, dry_run={dry_run})")

        if total_found == 0:
            return {"total": 0, "replayed": 0, "stored": 0, "errors": 0}

        ingestion_service = IngestionService(db)
        replayed_count = 0
        stored_count = 0
        error_count = 0

        for raw in records_to_replay:
            payload = raw.payload
            if not isinstance(payload, dict):
                logger.warning(f"RawIngest {raw.id} payload is not a dict, skipping")
                error_count += 1
                continue

            try:
                price_date_str = payload.get("price_date")
                p_date = date.fromisoformat(price_date_str) if price_date_str else date.today()

                record = PriceRecord(
                    crop_name=payload.get("crop_name", ""),
                    variety_name=payload.get("variety_name"),
                    market_name=payload.get("market_name", ""),
                    district=payload.get("district", ""),
                    state=payload.get("state", "Tamil Nadu"),
                    min_price=Decimal(str(payload.get("min_price", 0))),
                    max_price=Decimal(str(payload.get("max_price", 0))),
                    modal_price=Decimal(str(payload.get("modal_price", 0))),
                    raw_price=Decimal(str(payload["raw_price"])) if payload.get("raw_price") is not None else None,
                    raw_unit=payload.get("raw_unit", "kg"),
                    arrival_quantity=payload.get("arrival_quantity"),
                    price_date=p_date,
                    source=raw.source,
                    raw_payload=payload,
                )

                if not dry_run:
                    stored = ingestion_service._store_records([record])
                    stored_count += stored
                    raw.processed = True
                    db.commit()

                replayed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Error replaying raw record {raw.id}: {e}")
                db.rollback()

        summary = {
            "total": total_found,
            "replayed": replayed_count,
            "stored": stored_count,
            "errors": error_count,
            "dry_run": dry_run,
        }
        logger.info(f"Replay completed: {summary}")
        return summary

    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay raw ingested payloads through the pipeline")
    parser.add_argument("--source", type=str, default=None, help="Filter by data source (e.g. ogd, agmarknet)")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of records to replay")
    parser.add_argument("--unprocessed-only", action="store_true", help="Only replay unprocessed records")
    parser.add_argument("--dry-run", action="store_true", help="Parse records without committing changes")
    args = parser.parse_args()

    replay_raw_records(
        source=args.source,
        unprocessed_only=args.unprocessed_only,
        limit=args.limit,
        dry_run=args.dry_run,
    )
