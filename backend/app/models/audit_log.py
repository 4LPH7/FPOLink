"""AuditLog model — enterprise audit trail for operational mutations."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(
        String(100), nullable=False
    )  # CREATE_FARMER, UPDATE_PRICE, TRIGGER_INGESTION, VERIFY_HARVEST, etc.
    target_type = Column(
        String(50), nullable=False
    )  # farmer, fpo, market_price, harvest, user, crop
    target_id = Column(String(100), nullable=False)
    before_state = Column(JSONB, nullable=True)
    after_state = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.target_type}:{self.target_id}>"
