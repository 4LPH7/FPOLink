"""Order model."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=False)
    buyer_requirement_id = Column(
        UUID(as_uuid=True), ForeignKey("buyer_requirements.id"), nullable=False
    )
    batch_id = Column(UUID(as_uuid=True), ForeignKey("aggregation_batches.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default="pending")
    notes = Column(Text, nullable=True)
