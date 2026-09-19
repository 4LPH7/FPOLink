"""Variety model — crop varieties with grades."""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Variety(Base, TimestampMixin):
    __tablename__ = "varieties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    name = Column(String(100), nullable=False)  # finger, bulb, Nendran, Poovan
    tamil_name = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)

    crop = relationship("Crop", back_populates="varieties")

    def __repr__(self):
        return f"<Variety {self.name} of crop_id={self.crop_id}>"
