import hashlib
import json
import logging
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

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

                        stored = self._store_records(records, ingestion_run_id=ingestion_run.id)
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
            "ingestion_run_id": str(ingestion_run.id),
        }
        logger.info(f"Ingestion complete: {summary}")
        return summary

    def _store_records(
        self,
        records: List[PriceRecord],
        ingestion_run_id: Optional[UUID] = None,
    ) -> int:
        """Store price records in the database through the 8-stage pipeline."""
        stored = 0
        for record in records:
            try:
                # Stage 1: Immutable Raw Ingest & SHA-256 Checksum Deduplication
                raw_payload = record.raw_payload or {
                    "crop_name": record.crop_name,
                    "variety_name": record.variety_name,
                    "market_name": record.market_name,
                    "district": record.district,
                    "state": record.state,
                    "min_price": str(record.min_price),
                    "max_price": str(record.max_price),
                    "modal_price": str(record.modal_price),
                    "raw_price": str(record.raw_price) if record.raw_price is not None else None,
                    "raw_unit": record.raw_unit,
                    "arrival_quantity": record.arrival_quantity,
                    "price_date": record.price_date.isoformat(),
                    "source": record.source,
                }
                payload_json = json.dumps(raw_payload, sort_keys=True, default=str)
                checksum = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

                existing_raw = (
                    self.db.query(RawIngest)
                    .filter(RawIngest.source == record.source, RawIngest.checksum == checksum)
                    .first()
                )
                if existing_raw:
                    raw_ingest_id = existing_raw.id
                else:
                    raw = RawIngest(
                        source=record.source,
                        source_record_id=str(
                            raw_payload.get("source_record_id") or raw_payload.get("id") or ""
                        ),
                        checksum=checksum,
                        payload=raw_payload,
                        processed=True,
                    )
                    self.db.add(raw)
                    self.db.flush()
                    raw_ingest_id = raw.id

                # Stage 2: Schema Validation (Checked via PriceRecord and numerical ranges)
                if record.modal_price < 0 or record.min_price < 0 or record.max_price < 0:
                    logger.warning(f"Invalid negative price in record: {record}, skipping")
                    continue

                # Stage 3 & 4: External Source Mapping & Canonical Crop Resolution
                crop = resolve_crop(record.crop_name, self.db, source_code=record.source)
                if not crop:
                    crop = self.db.query(Crop).filter(Crop.name == record.crop_name).first()
                if not crop:
                    logger.warning(f"Unknown crop: {record.crop_name}, skipping")
                    continue

                # Resolve Market with Source Mapping & District Scoping
                market = self._resolve_market(record)
                if not market:
                    continue

                # Resolve Variety if provided
                variety_id = None
                if record.variety_name:
                    variety = resolve_variety(
                        crop.id,
                        record.variety_name,
                        self.db,
                        source_code=record.source,
                    )
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

                # Stage 5 & 6: Normalization & Geographic Verification
                geo_penalty = 0.0
                if record.district and market.district:
                    if record.district.strip().lower() != market.district.strip().lower():
                        geo_penalty = 15.0

                # Stage 7 & 8: Anomaly Check, Quality Scoring & Lineage Link
                quality_score, quality_breakdown = calculate_quality_score(
                    price_date=record.price_date,
                    modal_price=record.modal_price,
                    min_price=record.min_price,
                    max_price=record.max_price,
                    source=record.source,
                    alias_confidence=1.0,
                    arrival_quantity=record.arrival_quantity,
                )
                if geo_penalty > 0:
                    quality_score = max(0.0, quality_score - geo_penalty)
                    quality_breakdown["district_mismatch_penalty"] = -geo_penalty

                # Deduplication & Persistence
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
                    # Update with latest observation and record lineage
                    existing.min_price = record.min_price
                    existing.max_price = record.max_price
                    existing.modal_price = record.modal_price
                    existing.raw_price = record.raw_price
                    existing.raw_unit = record.raw_unit
                    existing.arrival_quantity = record.arrival_quantity
                    existing.quality_score = quality_score
                    existing.quality_breakdown = quality_breakdown
                    existing.ingestion_run_id = ingestion_run_id
                    existing.raw_ingest_id = raw_ingest_id
                    record_id = str(existing.id)
                else:
                    mp = MarketPrice(
                        crop_id=crop.id,
                        variety_id=variety_id,
                        market_id=market.id,
                        district=record.district or market.district,
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
                        ingestion_run_id=ingestion_run_id,
                        raw_ingest_id=raw_ingest_id,
                    )
                    self.db.add(mp)
                    self.db.flush()
                    stored += 1
                    record_id = str(mp.id)

                if quality_score < 50.0 and record_id:
                    issue_type = (
                        "price_contradiction"
                        if record.min_price > record.max_price
                        else ("geographic_mismatch" if geo_penalty > 0 else "low_quality_data")
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
        """Find or create a market entry with deterministic source mapping & canonical resolution."""
        district_id = None
        if record.district:
            district_obj = (
                self.db.query(District)
                .filter(func.lower(District.name) == record.district.strip().lower())
                .first()
            )
            if district_obj:
                district_id = district_obj.id

        # 1. Try canonical resolver with source_code
        market = resolve_market(
            record.market_name,
            district_id=district_id,
            db=self.db,
            source_code=record.source,
        )
        if market:
            return market

        # 2. Direct name/district query
        market = (
            self.db.query(Market)
            .filter(
                (func.lower(Market.name) == record.market_name.strip().lower())
                | (func.lower(Market.canonical_name) == record.market_name.strip().lower()),
                Market.district == record.district,
            )
            .first()
        )

        if not market:
            # Auto-create market with district linkage if available
            market = Market(
                name=record.market_name,
                canonical_name=record.market_name.strip().lower(),
                district=record.district,
                district_id=district_id,
                state=record.state or "Tamil Nadu",
                market_type="regulated_market",
                is_regulated=True,
                is_active=True,
            )
            self.db.add(market)
            self.db.commit()
            self.db.refresh(market)
            logger.info(f"Auto-created market: {record.market_name} in {record.district}")

        return market
