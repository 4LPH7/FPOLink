"""VarietyAlias model — maps variety names and codes to canonical varieties."""

import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class VarietyAlias(Base, TimestampMixin):
    __tablename__ = "variety_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variety_id = Column(UUID(as_uuid=True), ForeignKey("varieties.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String(100), index=True, nullable=False)
    source = Column(String(50), nullable=True)

    variety = relationship("Variety", back_populates="aliases")

    def __repr__(self):
        return f"<VarietyAlias '{self.alias}' -> variety_id={self.variety_id}>"
