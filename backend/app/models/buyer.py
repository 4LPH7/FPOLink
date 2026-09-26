"""Buyer and buyer requirement models — staff-mediated commercial demand."""

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.harvest import HarvestGrade


class Buyer(Base, TimestampMixin):
    __tablename__ = "buyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=True)
    company_name = Column(String(200), nullable=False)
    buyer_type = Column(
        String(50), nullable=False, default="wholesaler"
    )  # wholesaler, processor, exporter, retailer, trader
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(15), nullable=False)
    contact_email = Column(String, nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True)
    gstin = Column(String(20), nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    fpo = relationship("FPO")
    district_rel = relationship("District")
    requirements = relationship(
        "BuyerRequirement", back_populates="buyer", cascade="all, delete-orphan"
    )


class BuyerRequirement(Base, TimestampMixin):
    __tablename__ = "buyer_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id"), nullable=False)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=True)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    variety_id = Column(UUID(as_uuid=True), ForeignKey("varieties.id"), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    quantity_kg = Column(Float, nullable=False)
    fulfilled_quantity_kg = Column(Float, nullable=False, default=0.0)
    min_grade = Column(Enum(HarvestGrade), nullable=False)
    required_date = Column(Date, nullable=False)
    delivery_window_days = Column(Integer, nullable=False, default=7)
    max_price_per_kg = Column(Numeric(12, 2), nullable=True)
    delivery_location = Column(String(200), nullable=True)
    status = Column(
        String(20), default="open"
    )  # open, matched, partially_fulfilled, fulfilled, cancelled
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    buyer = relationship("Buyer", back_populates="requirements")
    crop = relationship("Crop")
    variety = relationship("Variety")
    fpo = relationship("FPO")
    district_rel = relationship("District")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    matches = relationship(
        "SupplyMatch", back_populates="buyer_requirement", cascade="all, delete-orphan"
    )
