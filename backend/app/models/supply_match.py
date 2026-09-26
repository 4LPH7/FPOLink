"""SupplyMatch model — audit ledger linking commercial demand to farmer plots or harvests."""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class SupplyMatch(Base, TimestampMixin):
    __tablename__ = "supply_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_requirement_id = Column(
        UUID(as_uuid=True), ForeignKey("buyer_requirements.id", ondelete="CASCADE"), nullable=False
    )
    farm_id = Column(
        UUID(as_uuid=True), ForeignKey("farms.id", ondelete="SET NULL"), nullable=True
    )
    harvest_id = Column(
        UUID(as_uuid=True), ForeignKey("harvests.id", ondelete="SET NULL"), nullable=True
    )
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=False)
    matched_quantity_kg = Column(Float, nullable=False)
    offered_price_per_kg = Column(Numeric(12, 2), nullable=True)
    match_score = Column(Float, nullable=False)  # 0.0 to 100.0 composite ranking score
    match_breakdown = Column(JSONB, nullable=True)  # distance_km, qty_fit, timing_days, price_fit
    status = Column(
        String(30), nullable=False, default="suggested"
    )  # suggested, confirmed_by_staff, notified_farmer, farmer_accepted, farmer_declined, fulfilled, cancelled, rejected
    staff_notes = Column(Text, nullable=True)
    confirmed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    farmer_responded_at = Column(DateTime(timezone=True), nullable=True)

    buyer_requirement = relationship("BuyerRequirement", back_populates="matches")
    farm = relationship("Farm")
    harvest = relationship("Harvest")
    fpo = relationship("FPO")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])

    def __repr__(self):
        return f"<SupplyMatch {self.id} score={self.match_score} status={self.status}>"
