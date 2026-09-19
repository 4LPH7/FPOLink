"""Price prediction model."""

import uuid

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    predicted_price = Column(Numeric(12, 2), nullable=False)
    lower_bound = Column(Numeric(12, 2), nullable=False)
    upper_bound = Column(Numeric(12, 2), nullable=False)
    confidence = Column(Float, nullable=True)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True)
    prediction_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    signal = Column(String(20), nullable=True)  # hold / sell / neutral
    created_at = Column(DateTime(timezone=True), server_default=func.now())
