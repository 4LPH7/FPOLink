import uuid
from sqlalchemy import Column, String, Float, Date, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    market_name = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    modal_price = Column(Float, nullable=False)
    arrival_quantity = Column(Float, nullable=True)
    price_date = Column(Date, index=True, nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('crop_id', 'market_name', 'price_date', 'source', name='uix_market_price_details'),
    )
