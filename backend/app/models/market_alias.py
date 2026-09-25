"""MarketAlias model — maps raw mandi names and government market codes to canonical markets."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class MarketAlias(Base, TimestampMixin):
    __tablename__ = "market_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(
        UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False
    )
    alias = Column(String(200), unique=True, nullable=False)
    source = Column(String(50), nullable=True)  # agmarknet, ceda, enam, general
    confidence = Column(Float, nullable=False, default=1.0)

    market = relationship("Market", back_populates="aliases")

    def __repr__(self):
        return f"<MarketAlias '{self.alias}' -> market_id={self.market_id}>"
