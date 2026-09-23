"""WhatsApp status webhook service: updates outbound status and tracks unreachable numbers (T4.1)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.messaging.base import StatusUpdate, mask
from app.models.farmer import Farmer
from app.models.whatsapp import OutboundMessage, WhatsAppRecipientStatus
from app.utils.phone import normalise_phone

log = logging.getLogger("whatsapp.status")


class WhatsAppStatusService:
    """Processes Meta status callbacks (sent, delivered, read, failed) and updates recipient health."""

    def __init__(self, db_factory=SessionLocal) -> None:
        self.db_factory = db_factory

    def handle_status_update(self, update: StatusUpdate) -> bool:
        """Process a single status callback from Meta.

        Returns True if status update was applied, False otherwise.
        """
        if not update.meta_message_id and not update.recipient_id:
            return False

        with self.db_factory() as db:
            # 1. Update matching outbound message
            outbound = None
            if update.meta_message_id:
                outbound = (
                    db.query(OutboundMessage)
                    .filter(OutboundMessage.meta_message_id == update.meta_message_id)
                    .first()
                )

            # Fallback to latest outbound message for recipient if meta ID didn't match
            if not outbound and update.recipient_id:
                outbound = (
                    db.query(OutboundMessage)
                    .filter(OutboundMessage.wa_id == update.recipient_id)
                    .order_by(OutboundMessage.created_at.desc())
                    .first()
                )

            now = datetime.now(timezone.utc)
            if outbound:
                outbound.status = update.status
                outbound.updated_at = now
                if update.status == "failed" and update.errors:
                    outbound.error_details = update.errors

            # 2. Update recipient status & unreachable protection
            wa_id = update.recipient_id or (outbound.wa_id if outbound else None)
            if wa_id:
                self._update_recipient_reputation(db, wa_id, update.status, update.errors, now)

            db.commit()
            return True

    def _update_recipient_reputation(
        self,
        db: Session,
        wa_id: str,
        status: str,
        errors: list[dict] | None,
        now: datetime,
    ) -> None:
        """Track failure counts and mark dead/unreachable numbers to prevent money waste."""
        recip = (
            db.query(WhatsAppRecipientStatus)
            .filter(WhatsAppRecipientStatus.wa_id == wa_id)
            .first()
        )
        if not recip:
            recip = WhatsAppRecipientStatus(
                wa_id=wa_id,
                consecutive_failures=0,
                is_unreachable=False,
                updated_at=now,
            )
            db.add(recip)

        p10 = normalise_phone(wa_id)
        matching_farmer = db.query(Farmer).filter(Farmer.phone == p10).first() if p10 else None

        if status in ("delivered", "read"):
            recip.consecutive_failures = 0
            recip.is_unreachable = False
            recip.updated_at = now
            if matching_farmer and matching_farmer.is_unreachable:
                matching_farmer.is_unreachable = False

        elif status == "failed":
            recip.consecutive_failures += 1
            recip.last_failure_at = now
            if errors and isinstance(errors, list) and len(errors) > 0:
                first_err = errors[0]
                recip.last_failure_reason = str(
                    first_err.get("title") or first_err.get("message") or first_err.get("code")
                )[:255]
            recip.updated_at = now

            if recip.consecutive_failures >= settings.WHATSAPP_MAX_CONSECUTIVE_FAILURES:
                recip.is_unreachable = True
                log.warning(
                    "Recipient %s marked unreachable after %d consecutive failures",
                    mask(wa_id),
                    recip.consecutive_failures,
                )
                if matching_farmer:
                    matching_farmer.is_unreachable = True

    def is_recipient_reachable(self, wa_id: str) -> bool:
        """Check whether a recipient is reachable or flagged as dead."""
        with self.db_factory() as db:
            recip = (
                db.query(WhatsAppRecipientStatus)
                .filter(WhatsAppRecipientStatus.wa_id == wa_id)
                .first()
            )
            if recip and recip.is_unreachable:
                return False

            p10 = normalise_phone(wa_id)
            if p10:
                farmer = db.query(Farmer).filter(Farmer.phone == p10).first()
                if farmer and farmer.is_unreachable:
                    return False

            return True
