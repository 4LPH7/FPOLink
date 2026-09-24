"""Data ingestion service — fetches, cleans, and stores market price data."""

import logging
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.data_sources.base import PriceRecord
from app.data_sources.registry import DataSourceRegistry
from app.models.crop import Crop
from app.models.data_quality import DataQualityEvent, IngestionRun
from app.models.geography import District
from app.models.ingestion_log import IngestionLog
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.services.crop_resolver import resolve_crop, resolve_variety
from app.services.data_quality import calculate_quality_score
from app.services.market_resolver import resolve_market

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

        crops = crops or settings.default_crops_list
        districts = districts or [settings.DEFAULT_DISTRICT]

        start_time = datetime.now(timezone.utc)
        total_fetched = 0
        total_stored = 0
        total_errors = 0
        error_details = []

        # Create IngestionRun telemetry record
        ingestion_run = IngestionRun(
            source_code=source or "auto",
            status="running",
            district=districts[0] if len(districts) == 1 else "statewide",
            records_fetched=0,
            records_ingested=0,
            started_at=start_time,
        )
        self.db.add(ingestion_run)
        self.db.commit()

        for crop_name in crops:
            for district in districts:
                # Select target providers: specific source or all available independent providers
                if source:
                    target_prov = self.registry.get_provider(source)
                    active_providers = (
                        [target_prov] if target_prov and target_prov.is_available() else []
                    )
                else:
                    active_providers = [p for p in self.registry.providers if p.is_available()]

                for provider in active_providers:
                    try:
                        records = provider.fetch_prices(
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
                        err_msg = f"Error ingesting {crop_name}/{district} from {provider.source_name}: {e}"
                        error_details.append(err_msg)
                        logger.error(err_msg)

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Update IngestionRun
        ingestion_run.records_fetched = total_fetched
        ingestion_run.records_ingested = total_stored
        ingestion_run.status = (
            "success" if total_errors == 0 else ("partial" if total_stored > 0 else "failed")
        )
        ingestion_run.errors = error_details if error_details else None
        ingestion_run.completed_at = datetime.now(timezone.utc)

        # Log the legacy ingestion run for backwards compatibility
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

                # Resolve crop via canonical resolver
                crop = resolve_crop(record.crop_name, self.db)
                if not crop:
                    crop = self.db.query(Crop).filter(Crop.name == record.crop_name).first()
                if not crop:
                    logger.warning(f"Unknown crop: {record.crop_name}, skipping")
                    continue

                # Resolve or create market via canonical resolver
                market = self._resolve_market(record)
                if not market:
                    continue

                # Resolve variety if provided
                variety_id = None
                if record.variety_name:
                    variety = resolve_variety(crop.id, record.variety_name, self.db)
                    if not variety:
                        from app.models.variety import Variety

                        variety = (
                            self.db.query(Variety)
                            .filter(
                                Variety.crop_id == crop.id,
                                Variety.name.ilike(record.variety_name.strip()),
                            )
                            .first()
                        )
                    if variety:
                        variety_id = variety.id

                # Calculate data quality score
                quality_score, quality_breakdown = calculate_quality_score(
                    price_date=record.price_date,
                    modal_price=record.modal_price,
                    min_price=record.min_price,
                    max_price=record.max_price,
                    source=record.source,
                    alias_confidence=1.0,
                    arrival_quantity=record.arrival_quantity,
                )

                # Check for existing record (dedup)
                existing_q = self.db.query(MarketPrice).filter(
                    MarketPrice.crop_id == crop.id,
                    MarketPrice.market_id == market.id,
                    MarketPrice.price_date == record.price_date,
                    MarketPrice.source == record.source,
                )
                if variety_id is not None:
                    existing_q = existing_q.filter(MarketPrice.variety_id == variety_id)
                else:
                    existing_q = existing_q.filter(MarketPrice.variety_id.is_(None))
                existing = existing_q.first()

                record_id = None
                if existing:
                    # Update if newer data
                    existing.min_price = record.min_price
                    existing.max_price = record.max_price
                    existing.modal_price = record.modal_price
                    existing.raw_price = record.raw_price
                    existing.raw_unit = record.raw_unit
                    existing.arrival_quantity = record.arrival_quantity
                    existing.quality_score = quality_score
                    existing.quality_breakdown = quality_breakdown
                    record_id = str(existing.id)
                else:
                    mp = MarketPrice(
                        crop_id=crop.id,
                        variety_id=variety_id,
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
                        quality_score=quality_score,
                        quality_breakdown=quality_breakdown,
                    )
                    self.db.add(mp)
                    self.db.flush()
                    stored += 1
                    record_id = str(mp.id)

                if quality_score < 50.0 and record_id:
                    issue_type = (
                        "price_contradiction"
                        if record.min_price > record.max_price
                        else "low_quality_data"
                    )
                    dq_event = DataQualityEvent(
                        record_type="market_price",
                        record_id=record_id,
                        issue_type=issue_type,
                        penalty=round(100.0 - quality_score, 1),
                        details=quality_breakdown,
                    )
                    self.db.add(dq_event)

                self.db.commit()

            except Exception as e:
                logger.error(f"Error storing record: {e}")
                self.db.rollback()

        return stored

    def _resolve_market(self, record: PriceRecord) -> Optional[Market]:
        """Find or create a market entry with canonical resolution."""
        district_id = None
        if record.district:
            district_obj = (
                self.db.query(District)
                .filter(func.lower(District.name) == record.district.strip().lower())
                .first()
            )
            if district_obj:
                district_id = district_obj.id

        # 1. Try canonical resolver
        market = resolve_market(record.market_name, district_id=district_id, db=self.db)
        if market:
            return market

        # 2. Direct name/district query
        market = (
            self.db.query(Market)
            .filter(
                Market.name == record.market_name,
                Market.district == record.district,
            )
            .first()
        )

        if not market:
            # Auto-create market with district linkage if available
            market = Market(
                name=record.market_name,
                district=record.district,
                district_id=district_id,
                state=record.state or "Tamil Nadu",
                market_type="mandi",
                is_active=True,
            )
            self.db.add(market)
            self.db.commit()
            self.db.refresh(market)
            logger.info(f"Auto-created market: {record.market_name} in {record.district}")

        return market
