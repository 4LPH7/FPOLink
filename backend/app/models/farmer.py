import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Farmer(Base, TimestampMixin):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=False)
    village = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    district = Column(String(100), default='Erode')
    farm_area_acres = Column(Float, nullable=False)

    user = relationship("User")
    fpo = relationship("FPO", back_populates="farmers")
    farms = relationship("Farm", back_populates="farmer")
    harvests = relationship("Harvest", back_populates="farmer")
