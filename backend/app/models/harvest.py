import enum
import uuid
from sqlalchemy import Column, Float, Date, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class HarvestGrade(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"

class HarvestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    AGGREGATED = "aggregated"
    SOLD = "sold"

class Harvest(Base, TimestampMixin):
    __tablename__ = "harvests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    grade = Column(Enum(HarvestGrade), nullable=False)
    harvest_date = Column(Date, nullable=False)
    status = Column(Enum(HarvestStatus), default=HarvestStatus.SUBMITTED)
    notes = Column(Text, nullable=True)

    farmer = relationship("Farmer", back_populates="harvests")
    crop = relationship("Crop")
