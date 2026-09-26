"""Farm plot model — discrete agricultural plots per farmer."""

import uuid

from sqlalchemy import Column, Date, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    plot_name = Column(String(100), nullable=True)
    area_acres = Column(Float, nullable=False)
    village = Column(String(100), nullable=True)
    soil_type = Column(String(50), nullable=True)  # Red Loam, Clay Loam, Black Cotton, Alluvial, Sandy
    irrigation_type = Column(String(50), nullable=True)  # Drip, Canal, Borewell, Rainfed, Sprinkler
    sowing_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    expected_yield_kg = Column(Float, nullable=True)
    actual_yield_kg = Column(Float, nullable=True)
    status = Column(String(20), default="active")  # active, harvested, fallow, abandoned

    # Multi-tier administrative geography
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    taluk_id = Column(UUID(as_uuid=True), ForeignKey("taluks.id"), nullable=True)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)

    farmer = relationship("Farmer", back_populates="farms")
    crop = relationship("Crop")
    district = relationship("District")
    taluk = relationship("Taluk")
