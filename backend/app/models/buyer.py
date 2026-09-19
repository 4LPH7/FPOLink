"""Buyer and buyer requirement models."""
import uuid
from sqlalchemy import Column, String, Float, Numeric, Date, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from app.models.harvest import HarvestGrade

class Buyer(Base, TimestampMixin):
    __tablename__ = "buyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    contact_email = Column(String, nullable=True)

class BuyerRequirement(Base, TimestampMixin):
    __tablename__ = "buyer_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    min_grade = Column(Enum(HarvestGrade), nullable=False)
    required_date = Column(Date, nullable=False)
    max_price_per_kg = Column(Numeric(12, 2), nullable=True)
    status = Column(String(20), default='open')
    notes = Column(Text, nullable=True)

    buyer = relationship("Buyer")
    crop = relationship("Crop")
