"""Market model — normalized market locations."""

import uuid

from sqlalchemy import Column, Float, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin


class Market(Base, TimestampMixin):
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default="Tamil Nadu")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    market_type = Column(String(50), nullable=False, default="mandi")  # mandi / uzhavar_sandhai

    def __repr__(self):
        return f"<Market {self.name} ({self.district})>"
