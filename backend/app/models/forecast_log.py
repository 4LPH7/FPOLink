"""Forecast accuracy log — track predictions vs actuals."""
import uuid
from sqlalchemy import Column, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class ForecastLog(Base):
    __tablename__ = "forecast_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=False)
    actual_price = Column(Numeric(12, 2), nullable=True)
    error = Column(Numeric(12, 2), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
