"""WhatsApp bot models for message idempotency, conversation state, and outbound tracking."""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base


class WhatsAppInbound(Base):
    """Log incoming WhatsApp webhook message IDs for deduplication / idempotency."""

    __tablename__ = "whatsapp_inbound"

    message_id = Column(String(100), primary_key=True)
    received_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(
        String(50), nullable=False, default="received"
    )  # received, processed, ignored, failed
    retry_count = Column(
        Integer, nullable=False, default=0, server_default="0"
    )  # at-least-once sweep counter (T5.4)


class ConversationState(Base):
    """Store active conversation state machines per WhatsApp ID with TTL."""

    __tablename__ = "conversation_state"

    wa_id = Column(String(50), primary_key=True)
    step = Column(String(50), nullable=False, default="IDLE")
    data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class OutboundMessage(Base):
    """Log outbound messages sent via Meta Cloud API for auditing, status updates, and cost control."""

    __tablename__ = "outbound_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wa_id = Column(String(50), nullable=False, index=True)
    meta_message_id = Column(String(100), nullable=True, index=True)
    category = Column(String(50), nullable=False)  # utility, authentication, marketing, service
    template = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="sent")  # sent, delivered, read, failed
    error_details = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class WhatsAppRecipientStatus(Base):
    """Track recipient delivery health and mark unreachable numbers after repeated failures."""

    __tablename__ = "whatsapp_recipient_status"

    wa_id = Column(String(50), primary_key=True)
    consecutive_failures = Column(Integer, nullable=False, default=0)
    is_unreachable = Column(Boolean, nullable=False, default=False)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_reason = Column(String(255), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
