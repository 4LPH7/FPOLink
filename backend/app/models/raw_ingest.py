"""Raw ingest model — stores raw JSONB payloads for replay."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class RawIngest(Base):
    __tablename__ = "raw_ingest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    payload = Column(JSONB, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
