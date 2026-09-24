"""Raw ingest model — stores raw JSONB payloads for replay."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base


class RawIngest(Base):
    __tablename__ = "raw_ingest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    source_record_id = Column(String(100), nullable=True)
    checksum = Column(String(64), nullable=True, index=True)
    payload = Column(JSONB, nullable=False)
    retrieved_at = Column(DateTime(timezone=True), server_default=func.now())
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
