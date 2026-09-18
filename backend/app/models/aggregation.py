import enum
import uuid
from sqlalchemy import Column, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from app.models.harvest import HarvestGrade

class BatchStatus(str, enum.Enum):
    OPEN = "open"
    FILLING = "filling"
    READY = "ready"
    SOLD = "sold"
    COMPLETED = "completed"

class AggregationBatch(Base, TimestampMixin):
    __tablename__ = "aggregation_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    total_quantity_kg = Column(Float, default=0.0)
    target_quantity_kg = Column(Float, nullable=True)
    grade = Column(Enum(HarvestGrade), nullable=False)
    status = Column(Enum(BatchStatus), default=BatchStatus.OPEN)

    fpo = relationship("FPO")
    crop = relationship("Crop")

class BatchItem(Base):
    __tablename__ = "batch_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("aggregation_batches.id"), nullable=False)
    harvest_id = Column(UUID(as_uuid=True), ForeignKey("harvests.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("AggregationBatch")
    harvest = relationship("Harvest")
