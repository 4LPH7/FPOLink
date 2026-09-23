"""DPDP-compliant data retention purge for WhatsApp tables.

Scheduled daily at 03:00 IST via the worker process.
Retention windows (from 5-CONTEXT.md D3):
  - whatsapp_inbound:    7 days   (dedup only needs recent rows)
  - conversation_state: 24 hours  (abandoned flows)
  - outbound_messages:  12 months (billing audit trail)
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models.whatsapp import ConversationState, OutboundMessage, WhatsAppInbound

logger = logging.getLogger(__name__)

BATCH_SIZE = 500  # cap per-batch to avoid long-running locks


def purge_inbound(retention_days: int = 7, db_factory=None) -> int:
    """Delete whatsapp_inbound rows older than *retention_days*."""
    factory = db_factory or SessionLocal
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    total = 0
    with factory() as db:
        while True:
            ids = (
                db.execute(
                    select(WhatsAppInbound.message_id)
                    .where(WhatsAppInbound.received_at < cutoff)
                    .limit(BATCH_SIZE)
                )
                .scalars()
                .all()
            )
            if not ids:
                break
            db.execute(delete(WhatsAppInbound).where(WhatsAppInbound.message_id.in_(ids)))
            db.commit()
            total += len(ids)
    logger.info("Purged %d inbound rows older than %d days", total, retention_days)
    return total


def purge_conversation_state(ttl_hours: int = 24, db_factory=None) -> int:
    """Delete stale conversation_state rows older than *ttl_hours*."""
    factory = db_factory or SessionLocal
    cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
    with factory() as db:
        result = db.execute(delete(ConversationState).where(ConversationState.updated_at < cutoff))
        db.commit()
        count = result.rowcount  # type: ignore[union-attr]
    logger.info("Purged %d stale conversation states older than %dh", count, ttl_hours)
    return count


def purge_outbound(retention_months: int = 12, db_factory=None) -> int:
    """Delete outbound_messages older than *retention_months*."""
    factory = db_factory or SessionLocal
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_months * 30)
    total = 0
    with factory() as db:
        while True:
            ids = (
                db.execute(
                    select(OutboundMessage.id)
                    .where(OutboundMessage.created_at < cutoff)
                    .limit(BATCH_SIZE)
                )
                .scalars()
                .all()
            )
            if not ids:
                break
            db.execute(delete(OutboundMessage).where(OutboundMessage.id.in_(ids)))
            db.commit()
            total += len(ids)
    logger.info("Purged %d outbound messages older than %d months", total, retention_months)
    return total
