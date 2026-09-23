"""At-least-once sweep: reprocess WhatsApp inbound messages stuck in 'received'.

Runs every 10 minutes via the worker scheduler (T5.4).
Configuration (from 5-CONTEXT.md D4):
  - Interval:       10 minutes
  - Age threshold:  5 minutes (ignore recently received)
  - Max retries:    3 (then mark 'failed')
"""

import logging
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.whatsapp import WhatsAppInbound

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
AGE_THRESHOLD_MINUTES = 5


def sweep_stuck_inbound(db_factory=None) -> dict:
    """Find and increment retry on messages stuck in 'received' status.

    Messages that have been in 'received' for longer than AGE_THRESHOLD_MINUTES
    are either still being processed (unlikely after 5 min) or were lost to a
    crash between dedup insert and completion.  We increment retry_count so
    Meta's webhook retry (which delivers within minutes) can re-trigger
    processing.  After MAX_RETRIES we give up and mark 'failed'.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=AGE_THRESHOLD_MINUTES)
    metrics: dict[str, int] = {"found": 0, "incremented": 0, "marked_failed": 0}
    factory = db_factory or SessionLocal

    with factory() as db:
        stuck = (
            db.query(WhatsAppInbound)
            .filter(
                WhatsAppInbound.status == "received",
                WhatsAppInbound.received_at < cutoff,
            )
            .all()
        )
        metrics["found"] = len(stuck)

        for row in stuck:
            row.retry_count = (row.retry_count or 0) + 1
            if row.retry_count >= MAX_RETRIES:
                row.status = "failed"
                metrics["marked_failed"] += 1
                logger.error(
                    "WhatsApp inbound message %s exhausted %d retries, marking failed",
                    row.message_id,
                    MAX_RETRIES,
                )
                try:
                    import sentry_sdk

                    sentry_sdk.capture_message(
                        f"WhatsApp inbound message {row.message_id} exhausted {MAX_RETRIES} retries and was marked failed",
                        level="error",
                    )
                except Exception:
                    pass
            else:
                metrics["incremented"] += 1
                logger.info(
                    "Message %s retry %d/%d",
                    row.message_id,
                    row.retry_count,
                    MAX_RETRIES,
                )
        db.commit()

    return metrics
