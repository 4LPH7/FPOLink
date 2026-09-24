"""Data Quality and Ingestion Telemetry Models."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base, TimestampMixin


class DataSource(Base, TimestampMixin):
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # ogd, ceda, agmarknet, tn_agrinet, manual
    priority = Column(Integer, nullable=False, default=1)  # lower number = higher priority
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<DataSource {self.name} ({self.code})>"


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_code = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="running")  # running, success, partial, failed
    district = Column(String(100), nullable=True)
    records_fetched = Column(Integer, nullable=False, default=0)
    records_ingested = Column(Integer, nullable=False, default=0)
    errors = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<IngestionRun {self.source_code} ({self.status}) - {self.records_ingested} ingested>"


class DataQualityEvent(Base):
    __tablename__ = "data_quality_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_type = Column(String(50), nullable=False)  # market_price, weather
    record_id = Column(String(100), nullable=False)
    issue_type = Column(String(50), nullable=False)  # stale_price, price_spike, missing_arrival, fuzzy_market
    penalty = Column(Float, nullable=False, default=0.0)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DataQualityEvent {self.issue_type} on {self.record_type}:{self.record_id} (-{self.penalty})>"
