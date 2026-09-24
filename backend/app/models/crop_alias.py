"""CropAlias model — maps raw, regional, and provider strings to canonical crops."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class CropAlias(Base, TimestampMixin):
    __tablename__ = "crop_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String(100), unique=True, nullable=False)
    source = Column(String(50), nullable=True)  # agmarknet, ceda, general, tamil
    confidence = Column(Float, nullable=False, default=1.0)

    crop = relationship("Crop", back_populates="aliases")

    def __repr__(self):
        return f"<CropAlias '{self.alias}' -> crop_id={self.crop_id}>"
