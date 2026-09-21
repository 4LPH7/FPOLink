"""Database implementation of BotServices protocol for FPOLink.

Provides atomic deduplication, farmer profile lookup, price querying with
stale detection, DPDP consent tracking, and conversation state TTL.
"""

from __future__ import annotations

import asyncio
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.crop import Crop
from app.models.farmer import Farmer as DbFarmer
from app.models.harvest import Harvest
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.prediction import Prediction
from app.models.user import User
from app.models.weather import WeatherData
from app.models.whatsapp import ConversationState, WhatsAppInbound
from app.services.bot import ConvState, Farmer, PriceInfo


class DbBotServices:
    """Production implementation of BotServices using SQLAlchemy and PostgreSQL."""

    def __init__(
        self,
        db_factory=SessionLocal,
        stale_days_threshold: int = 7,
        state_ttl_minutes: int = 30,
    ):
        self.db_factory = db_factory
        self.stale_days_threshold = stale_days_threshold
        self.state_ttl = timedelta(minutes=state_ttl_minutes)
        self._notice_claims: dict[str, float] = {}
        self._claims_lock = asyncio.Lock()

    async def first_time(self, message_id: str) -> bool:
        """Atomically record message_id; returns False if already seen (Meta retries webhooks)."""
        if not message_id:
            return False

        with self.db_factory() as db:
            try:
                inbound = WhatsAppInbound(message_id=message_id, status="received")
                db.add(inbound)
                db.commit()
                return True
            except IntegrityError:
                db.rollback()
                return False

    async def find_farmer(self, phone10: str) -> Optional[Farmer]:
        """Match farmer by last 10 digits of phone."""
        if not phone10:
            return None

        # Clean digits and take last 10
        cleaned = "".join(c for c in phone10 if c.isdigit())
        p10 = cleaned[-10:] if len(cleaned) >= 10 else cleaned

        with self.db_factory() as db:
            farmer = (
                db.query(DbFarmer)
                .join(User, DbFarmer.user_id == User.id)
                .filter((DbFarmer.phone == p10) | (User.phone == p10) | (User.phone.endswith(p10)))
                .first()
            )
            if not farmer:
                return None

            return Farmer(
                id=str(farmer.id),
                name=farmer.user.name if farmer.user else "",
                district=farmer.district or "Erode",
                lang=farmer.lang or "ta",
                alerts_opt_in=bool(farmer.alerts_opt_in),
                notice_sent_at=farmer.notice_sent_at,
                fpo_id=str(farmer.fpo_id) if farmer.fpo_id else None,
            )

    async def claim_notice(self, farmer_id: str, lease_seconds: float = 60.0) -> bool:
        """Atomically claim notice sending lease for farmer. Return True if claim acquired."""
        now_mono = time.monotonic()
        async with self._claims_lock:
            with self.db_factory() as db:
                farmer = db.query(DbFarmer).filter(DbFarmer.id == UUID(farmer_id)).first()
                if not farmer or farmer.notice_sent_at is not None:
                    return False

            claim_exp = self._notice_claims.get(farmer_id)
            if claim_exp is not None and now_mono < claim_exp:
                return False

            self._notice_claims[farmer_id] = now_mono + lease_seconds
            return True

    async def mark_notice_delivered(self, farmer_id: str) -> None:
        """Record timestamp when first-contact DPDP notice was confirmed delivered."""
        now = datetime.now(timezone.utc)
        async with self._claims_lock:
            self._notice_claims.pop(farmer_id, None)
            with self.db_factory() as db:
                farmer = db.query(DbFarmer).filter(DbFarmer.id == UUID(farmer_id)).first()
                if farmer:
                    farmer.notice_sent_at = now
                    db.commit()

    async def release_notice_claim(self, farmer_id: str) -> None:
        """Release leased claim after send failure so future inbound messages can retry."""
        async with self._claims_lock:
            self._notice_claims.pop(farmer_id, None)

    async def mark_notice_sent(self, farmer_id: str) -> None:
        """Record timestamp when first-contact DPDP notice was sent (alias to mark_notice_delivered)."""
        await self.mark_notice_delivered(farmer_id)

    async def latest_price(
        self, crop: str, district: Optional[str] = "Erode"
    ) -> Optional[PriceInfo]:
        """Retrieve newest available price for crop in district, with state fallback.

        Price rule:
        1. Find newest date for the given crop in the specified district from verified
           sources only (whitelisted: ceda, ogd). Never returns synthetic or demo prices.
        2. If both OGD and CEDA exist for the newest date, OGD takes precedence as the
           official live mandi feed.
        3. If none found in district, fallback to the newest verified date in Tamil Nadu.
        4. If newest date is older than stale_days_threshold (default 7 days),
           the price is flagged with an advisory.
        """
        from sqlalchemy import case

        from app.core.sources import REAL_PRICE_SOURCES

        source_precedence = case(
            (MarketPrice.source == "ogd", 1),
            (MarketPrice.source == "ceda", 2),
            else_=99,
        )

        with self.db_factory() as db:
            # Query with district filter first — strictly whitelisting real sources
            query = (
                db.query(MarketPrice, Market.name.label("market_name"))
                .join(Crop, MarketPrice.crop_id == Crop.id)
                .join(Market, MarketPrice.market_id == Market.id)
                .filter(
                    Crop.name.ilike(f"{crop}%"),
                    MarketPrice.source.in_(REAL_PRICE_SOURCES),
                )
            )

            if district:
                district_prices = (
                    query.filter(Market.district.ilike(f"{district}%"))
                    .order_by(
                        MarketPrice.price_date.desc(),
                        source_precedence.asc(),
                        MarketPrice.modal_price.desc(),
                    )
                    .first()
                )
                if district_prices:
                    mp, market_name = district_prices
                    return PriceInfo(
                        crop=crop,
                        modal_per_kg=mp.modal_price,
                        min_per_kg=mp.min_price,
                        max_per_kg=mp.max_price,
                        market=market_name,
                        price_date=mp.price_date,
                    )

            # Fallback across all districts in state
            state_price = query.order_by(
                MarketPrice.price_date.desc(),
                source_precedence.asc(),
                MarketPrice.modal_price.desc(),
            ).first()

            if state_price:
                mp, market_name = state_price
                return PriceInfo(
                    crop=crop,
                    modal_per_kg=mp.modal_price,
                    min_per_kg=mp.min_price,
                    max_per_kg=mp.max_price,
                    market=market_name,
                    price_date=mp.price_date,
                )

            return None

    def is_price_stale(self, price_info: PriceInfo) -> bool:
        """Check if price date exceeds staleness threshold."""
        today = date.today()
        days_old = (today - price_info.price_date).days
        return days_old > self.stale_days_threshold

    async def forecast_text(self, crop: str, lang: str = "ta") -> Optional[str]:
        """Return latest ML price forecast for crop."""
        with self.db_factory() as db:
            pred = (
                db.query(Prediction)
                .join(Crop, Prediction.crop_id == Crop.id)
                .filter(Crop.name.ilike(f"{crop}%"))
                .order_by(Prediction.created_at.desc())
                .first()
            )
            if not pred:
                return None

            quintal_price = pred.predicted_price * Decimal("100")
            if lang == "ta":
                return f"{crop.capitalize()} அடுத்த மாத கணிப்பு: ₹{quintal_price:.0f}/குவிண்டால் (நம்பகத்தன்மை: {pred.confidence_lower * Decimal('100'):.0f} - {pred.confidence_upper * Decimal('100'):.0f})"
            return f"{crop.capitalize()} next month forecast: ₹{quintal_price:.0f}/quintal (range: ₹{pred.confidence_lower * Decimal('100'):.0f} - ₹{pred.confidence_upper * Decimal('100'):.0f})"

    async def weather_text(self, district: str = "Erode", lang: str = "ta") -> Optional[str]:
        """Return latest weather advisory for district."""
        with self.db_factory() as db:
            w = (
                db.query(WeatherData)
                .filter(WeatherData.district.ilike(f"{district}%"))
                .order_by(WeatherData.forecast_date.desc())
                .first()
            )
            if not w:
                return None

            if lang == "ta":
                return f"{district} வானிலை ({w.forecast_date}): {w.condition or 'மிதமான வானிலை'}, வெப்பநிலை: {w.temp_min:.0f}°C - {w.temp_max:.0f}°C, மழை: {w.rainfall_mm:.1f}mm"
            return f"{district} Weather ({w.forecast_date}): {w.condition or 'Normal'}, Temp: {w.temp_min:.0f}°C - {w.temp_max:.0f}°C, Rain: {w.rainfall_mm:.1f}mm"

    async def submit_harvest(self, farmer_id: str, crop: str, qty_kg: Decimal, grade: str) -> None:
        """Create harvest record from WhatsApp chat flow."""
        with self.db_factory() as db:
            # Find crop id
            crop_obj = db.query(Crop).filter(Crop.name.ilike(f"{crop}%")).first()
            crop_id = crop_obj.id if crop_obj else None
            if not crop_id:
                # Create or fallback
                new_crop = Crop(name=crop.lower(), tamil_name=crop, unit="kg")
                db.add(new_crop)
                db.commit()
                db.refresh(new_crop)
                crop_id = new_crop.id

            harvest = Harvest(
                farmer_id=UUID(farmer_id),
                crop_id=crop_id,
                quantity_kg=float(qty_kg),
                quality_grade=grade.upper(),
                harvest_date=date.today(),
                status="SUBMITTED",
            )
            db.add(harvest)
            db.commit()

    async def set_alerts(self, farmer_id: str, on: bool) -> None:
        """Store opt-in/out with timestamp for DPDP audit compliance."""
        now = datetime.now(timezone.utc)
        with self.db_factory() as db:
            farmer = db.query(DbFarmer).filter(DbFarmer.id == UUID(farmer_id)).first()
            if farmer:
                farmer.alerts_opt_in = on
                if on:
                    farmer.alerts_opt_in_at = now
                    farmer.alerts_opt_out_at = None
                else:
                    farmer.alerts_opt_out_at = now
                db.commit()

    async def get_state(self, wa_id: str) -> Optional[ConvState]:
        """Retrieve conversation state, returning None if expired beyond 30m TTL."""
        with self.db_factory() as db:
            row = db.query(ConversationState).filter(ConversationState.wa_id == wa_id).first()
            if not row:
                return None

            now = datetime.now(timezone.utc)
            updated = row.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)

            if now - updated > self.state_ttl:
                # TTL expired — purge and return None
                db.delete(row)
                db.commit()
                return None

            return ConvState(step=row.step, data=dict(row.data or {}))

    async def set_state(self, wa_id: str, state: Optional[ConvState]) -> None:
        """Persist or remove conversation state."""
        with self.db_factory() as db:
            if state is None:
                db.query(ConversationState).filter(ConversationState.wa_id == wa_id).delete()
                db.commit()
                return

            now = datetime.now(timezone.utc)
            row = db.query(ConversationState).filter(ConversationState.wa_id == wa_id).first()
            if row:
                row.step = state.step
                row.data = state.data
                row.updated_at = now
            else:
                row = ConversationState(
                    wa_id=wa_id,
                    step=state.step,
                    data=state.data,
                    updated_at=now,
                )
                db.add(row)
            db.commit()
