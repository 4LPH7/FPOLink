"""FPO operations to-do list (field visits, procurement follow-ups, farmer calls)."""

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

TASK_STATUSES = ("todo", "in_progress", "done")
TASK_PRIORITIES = ("low", "medium", "high", "urgent")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="todo", index=True)
    priority = Column(String(10), nullable=False, default="medium")
    category = Column(String(30), nullable=False, default="general")
    due_date = Column(Date, nullable=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=True)
    harvest_id = Column(UUID(as_uuid=True), ForeignKey("harvests.id"), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    fpo = relationship("FPO")
    farmer = relationship("Farmer")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
