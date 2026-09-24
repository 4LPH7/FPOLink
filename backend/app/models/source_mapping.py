"""External Source-to-Canonical Entity Mappings.

Eliminates pure fuzzy matching by providing deterministic mapping of government
and academic feed identifiers (OGD, Agmarknet, CEDA) to canonical FPOLink entities.
"""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class CropSourceMapping(Base, TimestampMixin):
    __tablename__ = "crop_source_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)
    source_code = Column(String(50), nullable=False, index=True)  # ogd, agmarknet, ceda, tn_agrinet
    external_code = Column(String(100), nullable=False, index=True)
    external_name = Column(String(200), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

    crop = relationship("Crop")
    source = relationship("DataSource")

    __table_args__ = (
        UniqueConstraint("source_code", "external_code", name="uix_crop_source_mapping_code"),
    )

    def __repr__(self):
        return f"<CropSourceMapping {self.source_code}:{self.external_code} -> crop_id={self.crop_id}>"


class MarketSourceMapping(Base, TimestampMixin):
    __tablename__ = "market_source_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)
    source_code = Column(String(50), nullable=False, index=True)  # ogd, agmarknet, ceda, tn_agrinet
    external_code = Column(String(100), nullable=False, index=True)
    external_name = Column(String(200), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

    market = relationship("Market")
    source = relationship("DataSource")

    __table_args__ = (
        UniqueConstraint("source_code", "external_code", name="uix_market_source_mapping_code"),
    )

    def __repr__(self):
        return f"<MarketSourceMapping {self.source_code}:{self.external_code} -> market_id={self.market_id}>"


class VarietySourceMapping(Base, TimestampMixin):
    __tablename__ = "variety_source_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variety_id = Column(UUID(as_uuid=True), ForeignKey("varieties.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)
    source_code = Column(String(50), nullable=False, index=True)  # ogd, agmarknet, ceda, tn_agrinet
    external_code = Column(String(100), nullable=False, index=True)
    external_name = Column(String(200), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

    variety = relationship("Variety")
    source = relationship("DataSource")

    __table_args__ = (
        UniqueConstraint("source_code", "external_code", name="uix_variety_source_mapping_code"),
    )

    def __repr__(self):
        return f"<VarietySourceMapping {self.source_code}:{self.external_code} -> variety_id={self.variety_id}>"
