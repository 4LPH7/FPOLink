"""Crop model."""
import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    tamil_name = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    unit = Column(String(20), default='kg')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    varieties = relationship("Variety", back_populates="crop")
