"""Price-move alert service: sends alerts when modal prices swing >= 5% (T4.3)."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.config import settings
from app.core.sources import REAL_PRICE_SOURCES
from app.database import SessionLocal
from app.messaging.base import mask
from app.messaging.whatsapp_cloud import WhatsAppCloudChannel
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.whatsapp import OutboundMessage
from app.services.whatsapp_status import WhatsAppStatusService
from app.services.whatsapp_usage import WhatsAppUsageService
from app.utils.phone import normalise_phone

log = logging.getLogger("whatsapp.alerts")

CROP_TAMIL = {
    "turmeric": "மஞ்சள்",
    "banana": "வாழை",
    "coconut": "தென்னை",
    "paddy": "நெல்",
    "onion": "வெங்காயம்",
    "tomato": "தக்காளி",
}


class PriceMoveAlertService:
    """Detects modal price shifts >= threshold (default 5%) and dispatches alerts max 1/farmer/day."""

    def __init__(
        self,
        db_factory=SessionLocal,
        usage_service: WhatsAppUsageService | None = None,
        status_service: WhatsAppStatusService | None = None,
        threshold_pct: float | None = None,
    ) -> None:
        self.db_factory = db_factory
        self.usage_service = usage_service or WhatsAppUsageService(db_factory=db_factory)
        self.status_service = status_service or WhatsAppStatusService(db_factory=db_factory)
        self.threshold_pct = (
            threshold_pct
            if threshold_pct is not None
            else settings.WHATSAPP_PRICE_MOVE_THRESHOLD_PCT
        )

    async def check_and_send_alerts(
        self,
        channel: WhatsAppCloudChannel,
        target_date: date | None = None,
    ) -> dict[str, int]:
        """Scan for price swings >= threshold and dispatch alerts.

        Guarantees:
        1. Checks circuit breaker before sending.
        2. At most 1 price-move alert per farmer per day.
        3. Only delivers to reachable, opted-in farmers growing the impacted crop.
        """
        run_date = target_date or date.today()
        metrics = {"evaluated_crops": 0, "significant_moves": 0, "alerts_sent": 0, "skipped": 0}

        if self.usage_service.is_circuit_breaker_tripped():
            log.warning("Price alerts aborted: circuit breaker is tripped")
            return metrics

        with self.db_factory() as db:
            crops = db.query(Crop).all()
            for crop in crops:
                metrics["evaluated_crops"] += 1
                move = self._calculate_price_move(db, crop.id, run_date)
                if not move:
                    continue

                pct_change, current_price, prev_price, market_name = move
                if abs(pct_change) < self.threshold_pct:
                    continue

                metrics["significant_moves"] += 1
                direction = "up" if pct_change > 0 else "down"

                # Find farmers growing this crop
                eligible_farmers = self._get_farmers_for_crop(db, crop.id)
                for farmer in eligible_farmers:
                    p10 = normalise_phone(farmer.phone or "")
                    if not p10:
                        continue
                    wa_id = f"91{p10}" if not p10.startswith("91") and len(p10) == 10 else p10

                    if not self.status_service.is_recipient_reachable(wa_id):
                        metrics["skipped"] += 1
                        continue

                    # Strict Limit: Max 1 alert per farmer per day (T4.3)
                    if self._already_alerted_today(db, wa_id, run_date):
                        metrics["skipped"] += 1
                        continue

                    if self.usage_service.is_circuit_breaker_tripped():
                        log.warning("Price alerts halted mid-run: circuit breaker tripped")
                        break

                    lang = farmer.lang if farmer.lang in ("ta", "en") else "ta"
                    crop_label = (
                        CROP_TAMIL.get(crop.name.lower(), crop.name)
                        if lang == "ta"
                        else crop.name.capitalize()
                    )
                    dir_label = (
                        ("உயர்வு" if direction == "up" else "சரிவு")
                        if lang == "ta"
                        else ("Surge" if direction == "up" else "Drop")
                    )
                    cur_quintal = str(int(current_price * Decimal("100")))
                    change_str = f"{abs(pct_change):.1f}%"

                    params = [crop_label, dir_label, change_str, cur_quintal, market_name]

                    try:
                        success, meta_id = await channel.send_template_with_id(
                            to=wa_id,
                            name="price_move_alert",
                            lang=lang,
                            params=params,
                        )
                        if success:
                            outbound = OutboundMessage(
                                wa_id=wa_id,
                                meta_message_id=meta_id,
                                category="utility",
                                template="price_move_alert",
                                status="sent",
                                created_at=datetime.now(timezone.utc),
                            )
                            db.add(outbound)
                            db.commit()
                            metrics["alerts_sent"] += 1
                            log.info(
                                "Price alert sent to %s: %s %s (%s)",
                                mask(wa_id),
                                crop.name,
                                dir_label,
                                change_str,
                            )
                        else:
                            metrics["skipped"] += 1
                    except Exception:
                        log.exception("Price alert failed to %s", mask(wa_id))
                        metrics["skipped"] += 1

        return metrics

    def _calculate_price_move(
        self, db: Session, crop_id, target_date: date
    ) -> tuple[float, Decimal, Decimal, str] | None:
        """Calculate modal price change between latest price on/before target_date and previous day."""
        recent_prices = (
            db.query(MarketPrice, Market.name.label("market_name"))
            .join(Market, MarketPrice.market_id == Market.id)
            .filter(
                MarketPrice.crop_id == crop_id,
                MarketPrice.price_date <= target_date,
                MarketPrice.price_date >= target_date - timedelta(days=7),
                MarketPrice.source.in_(REAL_PRICE_SOURCES),
            )
            .order_by(MarketPrice.price_date.desc(), MarketPrice.modal_price.desc())
            .all()
        )
        if len(recent_prices) < 2:
            return None

        current_row, market_name = recent_prices[0]
        # Find distinct prior date
        prev_row = None
        for r, _ in recent_prices[1:]:
            if r.price_date < current_row.price_date:
                prev_row = r
                break

        if not prev_row or prev_row.modal_price <= 0:
            return None

        current_modal = current_row.modal_price
        prev_modal = prev_row.modal_price
        pct_change = float((current_modal - prev_modal) / prev_modal * Decimal("100"))

        return pct_change, current_modal, prev_modal, market_name

    def _get_farmers_for_crop(self, db: Session, crop_id) -> list[Farmer]:
        """Find opted-in, reachable farmers growing the specific crop."""
        return (
            db.query(Farmer)
            .join(Farm, Farm.farmer_id == Farmer.id)
            .filter(
                Farm.crop_id == crop_id,
                Farm.status == "active",
                Farmer.alerts_opt_in == True,  # noqa: E712
                Farmer.is_unreachable == False,  # noqa: E712
                Farmer.phone.isnot(None),
            )
            .distinct()
            .all()
        )

    def _already_alerted_today(self, db: Session, wa_id: str, target_date: date) -> bool:
        """Verify whether an alert has already been sent to this farmer today (limit 1/day)."""
        count = (
            db.query(func.count(OutboundMessage.id))
            .filter(
                OutboundMessage.wa_id == wa_id,
                OutboundMessage.template == "price_move_alert",
                extract("year", OutboundMessage.created_at) == target_date.year,
                extract("month", OutboundMessage.created_at) == target_date.month,
                extract("day", OutboundMessage.created_at) == target_date.day,
            )
            .scalar()
            or 0
        )
        return count > 0
