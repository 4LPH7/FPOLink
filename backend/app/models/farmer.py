import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Farmer(Base, TimestampMixin):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=False)
    phone = Column(String(10), unique=True, index=True, nullable=True)
    village = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    district = Column(String(100), default="Erode")
    farm_area_acres = Column(Float, nullable=False)
    lang = Column(String(10), nullable=False, default="ta")
    alerts_opt_in = Column(Boolean, nullable=False, default=False)
    alerts_opt_in_at = Column(DateTime(timezone=True), nullable=True)
    alerts_opt_out_at = Column(DateTime(timezone=True), nullable=True)
    notice_sent_at = Column(DateTime(timezone=True), nullable=True)
    is_unreachable = Column(Boolean, nullable=False, default=False)

    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)
    taluk_id = Column(UUID(as_uuid=True), ForeignKey("taluks.id"), nullable=True)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)

    user = relationship("User")
    fpo = relationship("FPO", back_populates="farmers")
    farms = relationship("Farm", back_populates="farmer")
    harvests = relationship("Harvest", back_populates="farmer")
