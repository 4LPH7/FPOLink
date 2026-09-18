import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    records_fetched = Column(Integer, nullable=False)
    records_stored = Column(Integer, nullable=False)
    errors = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=False)
    run_at = Column(DateTime(timezone=True), server_default=func.now())
