"""Daily digest worker service: sends approved price digest template at ~07:30 IST (T4.2)."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.messaging.base import mask
from app.messaging.whatsapp_cloud import WhatsAppCloudChannel
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.whatsapp import OutboundMessage
from app.services.db_bot_services import DbBotServices
from app.services.whatsapp_status import WhatsAppStatusService
from app.services.whatsapp_usage import WhatsAppUsageService
from app.utils.phone import normalise_phone

log = logging.getLogger("whatsapp.digest")

# Tamil translations for crop names in digest
CROP_TAMIL = {
    "turmeric": "மஞ்சள்",
    "banana": "வாழை",
    "coconut": "தென்னை",
    "paddy": "நெல்",
    "onion": "வெங்காயம்",
    "tomato": "தக்காளி",
}


class DailyDigestService:
    """Executes the daily 07:30 IST price digest to opted-in farmers with strict idempotency."""

    def __init__(
        self,
        db_factory=SessionLocal,
        bot_services: DbBotServices | None = None,
        usage_service: WhatsAppUsageService | None = None,
        status_service: WhatsAppStatusService | None = None,
    ) -> None:
        self.db_factory = db_factory
        self.bot_services = bot_services or DbBotServices(db_factory=db_factory)
        self.usage_service = usage_service or WhatsAppUsageService(db_factory=db_factory)
        self.status_service = status_service or WhatsAppStatusService(db_factory=db_factory)

    async def run_digest(
        self,
        channel: WhatsAppCloudChannel,
        target_date: date | None = None,
    ) -> dict[str, int]:
        """Run daily price digest for all eligible farmers.

        Guarantees:
        1. Checks circuit breaker before sending.
        2. Targets only opted-in, reachable farmers.
        3. Matches crops from farmer's farms.
        4. Sends ONLY if fresh price data exists (never sends stale).
        5. Strictly idempotent on (wa_id, template, target_date).
        """
        run_date = target_date or date.today()
        metrics = {
            "opted_in": 0,
            "sent": 0,
            "skipped_stale": 0,
            "skipped_duplicate": 0,
            "skipped_unreachable": 0,
            "skipped_no_crop": 0,
            "errors": 0,
        }

        # 1. Circuit breaker gate
        if self.usage_service.is_circuit_breaker_tripped():
            log.warning("Daily digest aborted: circuit breaker is tripped")
            return metrics

        with self.db_factory() as db:
            # 2. Query eligible farmers
            farmers = (
                db.query(Farmer)
                .filter(
                    Farmer.alerts_opt_in == True,  # noqa: E712
                    Farmer.is_unreachable == False,  # noqa: E712
                    Farmer.phone.isnot(None),
                )
                .all()
            )
            metrics["opted_in"] = len(farmers)

            for farmer in farmers:
                p10 = normalise_phone(farmer.phone or "")
                if not p10:
                    continue
                wa_id = f"91{p10}" if not p10.startswith("91") and len(p10) == 10 else p10

                # Check recipient reputation
                if not self.status_service.is_recipient_reachable(wa_id):
                    metrics["skipped_unreachable"] += 1
                    continue

                # Idempotency check: has digest already been sent to this farmer today?
                if self._already_sent_today(db, wa_id, "daily_price_digest", run_date):
                    metrics["skipped_duplicate"] += 1
                    continue

                # Circuit breaker check per message
                if self.usage_service.is_circuit_breaker_tripped():
                    log.warning("Daily digest halted mid-run: circuit breaker tripped")
                    break

                # 3. Match crops grown by farmer
                crops = self._get_farmer_crops(db, farmer)
                if not crops:
                    metrics["skipped_no_crop"] += 1
                    continue

                # Select primary crop with fresh price
                primary_crop = crops[0]
                price_info = await self.bot_services.latest_price(
                    primary_crop, district=farmer.district
                )

                # 4. Strict Freshness Gate
                if not price_info or self.bot_services.is_price_stale(price_info):
                    metrics["skipped_stale"] += 1
                    continue

                # 5. Format approved template: daily_price_digest
                lang = farmer.lang if farmer.lang in ("ta", "en") else "ta"
                crop_label = (
                    CROP_TAMIL.get(primary_crop.lower(), primary_crop)
                    if lang == "ta"
                    else primary_crop.capitalize()
                )
                quintal_price = str(int(price_info.modal_per_kg * Decimal("100")))
                market_label = price_info.market or farmer.district or "Erode"

                params = [crop_label, quintal_price, market_label]

                try:
                    success, meta_id = await channel.send_template_with_id(
                        to=wa_id,
                        name="daily_price_digest",
                        lang=lang,
                        params=params,
                    )
                    if success:
                        outbound = OutboundMessage(
                            wa_id=wa_id,
                            meta_message_id=meta_id,
                            category="utility",
                            template="daily_price_digest",
                            status="sent",
                            created_at=datetime.now(timezone.utc),
                        )
                        db.add(outbound)
                        db.commit()
                        metrics["sent"] += 1
                        log.info(
                            "Digest sent to %s for %s: ₹%s/q",
                            mask(wa_id),
                            primary_crop,
                            quintal_price,
                        )
                    else:
                        metrics["errors"] += 1
                except Exception:
                    log.exception("Digest send error to %s", mask(wa_id))
                    metrics["errors"] += 1

        return metrics

    def _already_sent_today(
        self, db: Session, wa_id: str, template: str, target_date: date
    ) -> bool:
        """Check if an outbound message of template has already been logged today."""
        count = (
            db.query(func.count(OutboundMessage.id))
            .filter(
                OutboundMessage.wa_id == wa_id,
                OutboundMessage.template == template,
                extract("year", OutboundMessage.created_at) == target_date.year,
                extract("month", OutboundMessage.created_at) == target_date.month,
                extract("day", OutboundMessage.created_at) == target_date.day,
            )
            .scalar()
            or 0
        )
        return count > 0

    def _get_farmer_crops(self, db: Session, farmer: Farmer) -> list[str]:
        """Fetch distinct active crop names for farmer, falling back to default crops."""
        farms = (
            db.query(Farm)
            .join(Crop, Farm.crop_id == Crop.id)
            .filter(
                Farm.farmer_id == farmer.id,
                Farm.status == "active",
            )
            .all()
        )
        crops = [farm.crop.name for farm in farms if farm.crop and farm.crop.name]
        if not crops:
            crops = list(settings.DEFAULT_CROPS)
        return crops
