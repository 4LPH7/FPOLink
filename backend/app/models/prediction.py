import uuid
from sqlalchemy import Column, String, Float, Date, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    market = Column(String(100), nullable=False)
    predicted_price = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=False)
    prediction_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
