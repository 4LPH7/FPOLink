"""Market model — normalized market locations."""

import uuid

from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin


class Market(Base, TimestampMixin):
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default="Tamil Nadu")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    market_type = Column(String(50), nullable=False, default="mandi")  # regulated_market / uzhavar_sandhai / private_mandi
    is_active = Column(Boolean, nullable=False, default=True)

    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    taluk_id = Column(UUID(as_uuid=True), ForeignKey("taluks.id"), nullable=True)

    def __repr__(self):
        return f"<Market {self.name} ({self.district})>"
