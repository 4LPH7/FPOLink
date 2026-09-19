"""Market price model — daily commodity prices from various sources."""
import uuid
from sqlalchemy import Column, String, Float, Date, Numeric, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    variety_id = Column(UUID(as_uuid=True), ForeignKey("varieties.id"), nullable=True)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    district = Column(String(100), nullable=False)
    min_price = Column(Numeric(12, 2), nullable=False)
    max_price = Column(Numeric(12, 2), nullable=False)
    modal_price = Column(Numeric(12, 2), nullable=False)
    raw_price = Column(Numeric(12, 2), nullable=True)  # Original value before unit conversion
    raw_unit = Column(String(20), nullable=True)  # Original unit (quintal, kg, etc.)
    arrival_quantity = Column(Float, nullable=True)
    price_date = Column(Date, index=True, nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    crop = relationship("Crop")
    variety = relationship("Variety")
    market = relationship("Market")

    __table_args__ = (
        UniqueConstraint('crop_id', 'market_id', 'price_date', 'source', name='uix_market_price_details'),
    )
