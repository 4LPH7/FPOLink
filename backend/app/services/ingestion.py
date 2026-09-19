"""Data ingestion service — fetches, cleans, and stores market price data."""

import json
import logging
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.models.ingestion_log import IngestionLog
from app.data_sources.base import PriceRecord
from app.data_sources.registry import DataSourceRegistry

logger = logging.getLogger(__name__)


class IngestionService:
    """Handles price data ingestion from all configured sources."""

    def __init__(self, db: Session):
        self.db = db
        self.registry = DataSourceRegistry()

    def run_ingestion(
        self,
        crops: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        source: Optional[str] = None,
    ) -> dict:
        """Run price ingestion for configured crops and districts.

        Returns a summary dict with records fetched, stored, errors.
        """
        from app.config import settings

        crops = crops or settings.DEFAULT_CROPS
        districts = districts or [settings.DEFAULT_DISTRICT]

        start_time = datetime.now(timezone.utc)
        total_fetched = 0
        total_stored = 0
        total_errors = 0
        error_details = []

        for crop_name in crops:
            for district in districts:
                try:
                    records = self.registry.fetch_prices(
                        crop=crop_name,
                        district=district,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    total_fetched += len(records)

                    stored = self._store_records(records)
                    total_stored += stored

                except Exception as e:
                    total_errors += 1
                    err_msg = f"Error ingesting {crop_name}/{district}: {e}"
                    error_details.append(err_msg)
                    logger.error(err_msg)

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Log the ingestion run
        log_entry = IngestionLog(
            source=source or "auto",
            records_fetched=total_fetched,
            records_stored=total_stored,
            errors=total_errors,
            error_details="\n".join(error_details) if error_details else None,
            duration_seconds=duration,
        )
        self.db.add(log_entry)
        self.db.commit()

        summary = {
            "records_fetched": total_fetched,
            "records_stored": total_stored,
            "errors": total_errors,
            "duration_seconds": round(duration, 2),
        }
        logger.info(f"Ingestion complete: {summary}")
        return summary

    def _store_records(self, records: List[PriceRecord]) -> int:
        """Store price records in the database, deduplicating by unique constraint."""
        stored = 0
        for record in records:
            try:
                # Store raw payload for replay
                if record.raw_payload:
                    raw = RawIngest(
                        source=record.source,
                        payload=record.raw_payload,
                        processed=True,
                    )
                    self.db.add(raw)

                # Resolve crop
                crop = self.db.query(Crop).filter(
                    Crop.name == record.crop_name
                ).first()
                if not crop:
                    logger.warning(f"Unknown crop: {record.crop_name}, skipping")
                    continue

                # Resolve or create market
                market = self._resolve_market(record)
                if not market:
                    continue

                # Check for existing record (dedup)
                existing = self.db.query(MarketPrice).filter(
                    MarketPrice.crop_id == crop.id,
                    MarketPrice.market_id == market.id,
                    MarketPrice.price_date == record.price_date,
                    MarketPrice.source == record.source,
                ).first()

                if existing:
                    # Update if newer data
                    existing.min_price = record.min_price
                    existing.max_price = record.max_price
                    existing.modal_price = record.modal_price
                    existing.raw_price = record.raw_price
                    existing.raw_unit = record.raw_unit
                    existing.arrival_quantity = record.arrival_quantity
                else:
                    mp = MarketPrice(
                        crop_id=crop.id,
                        market_id=market.id,
                        district=record.district,
                        min_price=record.min_price,
                        max_price=record.max_price,
                        modal_price=record.modal_price,
                        raw_price=record.raw_price,
                        raw_unit=record.raw_unit,
                        arrival_quantity=record.arrival_quantity,
                        price_date=record.price_date,
                        source=record.source,
                    )
                    self.db.add(mp)
                    stored += 1

                self.db.commit()

            except Exception as e:
                logger.error(f"Error storing record: {e}")
                self.db.rollback()

        return stored

    def _resolve_market(self, record: PriceRecord) -> Optional[Market]:
        """Find or create a market entry."""
        market = self.db.query(Market).filter(
            Market.name == record.market_name,
            Market.district == record.district,
        ).first()

        if not market:
            # Auto-create market
            market = Market(
                name=record.market_name,
                district=record.district,
                state=record.state,
                market_type="mandi",
            )
            self.db.add(market)
            self.db.commit()
            self.db.refresh(market)
            logger.info(f"Auto-created market: {record.market_name} in {record.district}")

        return market
