"""Crop model — agricultural crop ontology."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    canonical_name = Column(String(100), unique=True, nullable=True)
    tamil_name = Column(String(100), nullable=True)
    scientific_name = Column(String(150), nullable=True)
    category = Column(String(50), nullable=True)  # Cereals, Pulses, Oilseeds, Commercial, Horticulture, Plantation
    subcategory = Column(String(50), nullable=True)
    unit = Column(String(20), default="kg")
    default_unit = Column(String(20), default="kg")
    market_unit = Column(String(20), default="quintal")
    season_type = Column(String(50), nullable=True)  # Kharif, Rabi, Zaid, Kuruvai, Samba, Navarai, Perennial
    water_requirement = Column(String(20), nullable=True)  # Low, Medium, High
    perishability = Column(String(20), nullable=True)  # Low, Medium, High
    storage_days = Column(Integer, nullable=True)
    is_horticulture = Column(Boolean, nullable=False, default=False)
    is_commercial = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    varieties = relationship("Variety", back_populates="crop", cascade="all, delete-orphan")
    aliases = relationship("CropAlias", back_populates="crop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Crop {self.name} ({self.tamil_name})>"
