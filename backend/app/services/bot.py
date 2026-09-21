# ruff: noqa: E501  (Tamil message strings are long)
"""WhatsApp bot engine.

Transport-agnostic: depends only on MessageChannel (send) and BotServices (your data).
Wire BotServices to your real price / farmer / harvest services (see WHATSAPP_SETUP.md).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Protocol

from app.messaging.base import Button, InboundMessage, MessageChannel, mask

log = logging.getLogger("bot")

CROP_NAMES = {
    "turmeric": {"en": "Turmeric", "ta": "மஞ்சள்"},
    "banana": {"en": "Banana", "ta": "வாழை"},
}
CROP_KEYWORDS = {
    "turmeric": ["turmeric", "manjal", "மஞ்சள்"],
    "banana": ["banana", "vazhai", "வாழை"],
}
# Order matters: first match wins.
INTENT_KEYWORDS = {
    "cancel": ["cancel", "ரத்து"],
    "harvest": ["harvest", "அறுவடை"],
    "forecast": ["forecast", "கணிப்பு", "முன்னறிவிப்பு"],
    "weather": ["weather", "வானிலை"],
    "price": ["price", "rate", "விலை"],
    "menu": ["menu", "help", "hi", "hello", "start", "உதவி", "வணக்கம்"],
}

# Tamil copy is a first draft: have a native speaker (ideally a farmer) review it.
T = {
    "en": {
        "menu": "Hello {name}! What would you like?\nYou can also type: PRICE, FORECAST, WEATHER, HARVEST.",
        "not_registered": "This number is not registered. Please contact your FPO to register.",
        "unknown": "Sorry, I didn't understand. Send MENU to see the options.",
        "no_price": "No recent price available for {crop}.",
        "price_line": "{crop}: ₹{quintal}/quintal (min ₹{lo}, max ₹{hi}) - {market}, {date}",
        "ask_crop": "Which crop did you harvest?",
        "ask_qty": "How many kg? (send a number, e.g. 250)",
        "bad_qty": "Please send a valid number of kg, e.g. 250.",
        "ask_grade": "Which grade?",
        "confirm": "Save this harvest? {crop}, {qty} kg, grade {grade}",
        "saved": "Harvest saved ✅ {crop}, {qty} kg, grade {grade}.",
        "cancelled": "Cancelled.",
        "alerts_on": "Price alerts are ON. Send ALERTS OFF to stop.",
        "alerts_off": "Price alerts are OFF.",
        "notice": (
            "Welcome to FPOLink! 🌾\n"
            "This service provides daily mandi prices, weather updates, and harvest aggregation for your FPO.\n"
            "• Data protection: your phone number and harvest details are securely stored under the DPDP Act.\n"
            "• Support: contact your FPO coordinator for help.\n"
            "• Opt out: reply STOP anytime to disable price alerts."
        ),
        "unavailable": "This is not available yet.",
        "b_price": "Price",
        "b_forecast": "Forecast",
        "b_harvest": "Harvest",
        "b_yes": "Yes",
        "b_no": "No",
    },
    "ta": {
        "menu": "வணக்கம் {name}! உங்களுக்கு என்ன வேண்டும்?\nநீங்கள் எழுதலாம்: விலை, கணிப்பு, வானிலை, அறுவடை.",
        "not_registered": "இந்த எண் பதிவு செய்யப்படவில்லை. பதிவு செய்ய உங்கள் FPO-வைத் தொடர்பு கொள்ளவும்.",
        "unknown": "மன்னிக்கவும், புரியவில்லை. விருப்பங்களுக்கு MENU என்று அனுப்பவும்.",
        "no_price": "{crop} க்கு சமீபத்திய விலை இல்லை.",
        "price_line": "{crop}: ₹{quintal}/குவிண்டால் (குறைந்தது ₹{lo}, அதிகபட்சம் ₹{hi}) - {market}, {date}",
        "ask_crop": "எந்தப் பயிரை அறுவடை செய்தீர்கள்?",
        "ask_qty": "எத்தனை கிலோ? (எண்ணை அனுப்பவும், எ.கா. 250)",
        "bad_qty": "சரியான கிலோ எண்ணை அனுப்பவும், எ.கா. 250.",
        "ask_grade": "எந்தத் தரம்?",
        "confirm": "இந்த அறுவடையைச் சேமிக்கவா? {crop}, {qty} கிலோ, தரம் {grade}",
        "saved": "அறுவடை சேமிக்கப்பட்டது ✅ {crop}, {qty} கிலோ, தரம் {grade}.",
        "cancelled": "ரத்து செய்யப்பட்டது.",
        "alerts_on": "விலை எச்சரிக்கைகள் இயக்கத்தில் உள்ளன. நிறுத்த ALERTS OFF என்று அனுப்பவும்.",
        "alerts_off": "விலை எச்சரிக்கைகள் நிறுத்தப்பட்டன.",
        "notice": (
            "FPOLink-க்கு நல்வரவு! 🌾\n"
            "இந்த சேவை உங்கள் FPO-க்கான தினசரி மண்டி விலைகள், வானிலை தகவல்கள் மற்றும் அறுவடை விவரங்களை வழங்குகிறது.\n"
            "• தரவு பாதுகாப்பு: உங்கள் தொலைபேசி எண் மற்றும் அறுவடை விவரங்கள் DPDP சட்டத்தின்படி பாதுகாக்கப்படுகின்றன.\n"
            "• உதவிக்கு: உங்கள் FPO ஒருங்கிணைப்பாளரைத் தொடர்பு கொள்ளவும்.\n"
            "• நிறுத்த: எச்சரிக்கைகளை நிறுத்த எப்போது வேண்டுமானாலும் STOP அல்லது 'நிறுத்து' என்று அனுப்பலாம்."
        ),
        "unavailable": "இது இன்னும் கிடைக்கவில்லை.",
        "b_price": "விலை",
        "b_forecast": "கணிப்பு",
        "b_harvest": "அறுவடை",
        "b_yes": "ஆம்",
        "b_no": "இல்லை",
    },
}


# ---------------------------------------------------------------- data types


@dataclass(frozen=True)
class Farmer:
    id: str
    name: str
    district: str
    lang: str = "ta"  # "ta" | "en"
    alerts_opt_in: bool = False
    notice_sent_at: datetime | None = None
    fpo_id: str | None = None


@dataclass(frozen=True)
class PriceInfo:
    crop: str
    modal_per_kg: Decimal
    min_per_kg: Decimal
    max_per_kg: Decimal
    market: str
    price_date: date


@dataclass
class ConvState:
    step: str  # "crop" | "qty" | "grade" | "confirm"
    data: dict = field(default_factory=dict)  # keep JSON-serialisable (store in DB/Redis)


class BotServices(Protocol):
    """Everything the bot needs from your app. Implement against your DB/services."""

    async def first_time(self, message_id: str) -> bool:
        """Atomically record message_id; False if already seen (Meta retries webhooks)."""

    async def find_farmer(self, phone10: str) -> Farmer | None: ...

    async def latest_price(self, crop: str, district: str | None = None) -> PriceInfo | None: ...

    async def forecast_text(self, crop: str, lang: str) -> str | None: ...

    async def weather_text(self, district: str, lang: str) -> str | None: ...

    async def submit_harvest(
        self, farmer_id: str, crop: str, qty_kg: Decimal, grade: str
    ) -> None: ...

    async def set_alerts(self, farmer_id: str, on: bool) -> None:
        """Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in)."""

    async def mark_notice_sent(self, farmer_id: str) -> None:
        """Record timestamp when first-contact DPDP notice was sent."""

    async def get_state(self, wa_id: str) -> ConvState | None: ...

    async def set_state(self, wa_id: str, state: ConvState | None) -> None: ...


# ---------------------------------------------------------------- helpers


def normalize_phone(wa_id: str) -> str:
    """WhatsApp ids look like 919876543210. Match on the last 10 digits (India-only assumption)."""
    digits = re.sub(r"\D", "", wa_id)
    return digits[-10:] if len(digits) >= 10 else digits


def _tokens(text: str) -> list[str]:
    # \w would split Tamil words at combining vowel signs, so use explicit ranges.
    return re.findall(r"[a-z0-9\u0B80-\u0BFF]+", text.lower())


def _match(token: str, keyword: str) -> bool:
    # Tamil words take suffixes (விலையை), so allow prefix match for longer keywords.
    return token == keyword or (len(keyword) > 3 and token.startswith(keyword))


def detect_intent(text: str) -> str | None:
    toks = _tokens(text)
    # Check STOP or ALERTS OFF first (T2.3)
    if any(t in ("stop", "halt") or _match(t, "நிறுத்து") for t in toks):
        return "alerts_off"
    if any(_match(t, "alerts") or _match(t, "எச்சரிக்கை") for t in toks):
        off = any(t in ("off", "stop") or _match(t, "நிறுத்து") for t in toks)
        return "alerts_off" if off else "alerts_on"
    for intent, kws in INTENT_KEYWORDS.items():
        if any(_match(t, kw) for t in toks for kw in kws):
            return intent
    return None


def detect_crop(text: str) -> str | None:
    toks = _tokens(text)
    for crop, kws in CROP_KEYWORDS.items():
        if any(_match(t, kw) for t in toks for kw in kws):
            return crop
    return None


def parse_qty(text: str) -> Decimal | None:
    m = re.search(r"\d+(?:\.\d+)?", text.replace(",", ""))
    if not m:
        return None
    try:
        qty = Decimal(m.group())
    except InvalidOperation:
        return None
    return qty if 0 < qty <= 100_000 else None


def crop_name(crop: str, lang: str) -> str:
    return CROP_NAMES.get(crop, {}).get(lang, crop)


def format_price(p: PriceInfo, lang: str) -> str:
    # Mandi prices are quoted per quintal (100 kg); we store Rs/kg.
    q = lambda v: f"{v * 100:,.0f}"  # noqa: E731
    return T[lang]["price_line"].format(
        crop=crop_name(p.crop, lang),
        quintal=q(p.modal_per_kg),
        lo=q(p.min_per_kg),
        hi=q(p.max_per_kg),
        market=p.market,
        date=p.price_date.strftime("%d-%m-%Y"),
    )


# ---------------------------------------------------------------- engine


class BotEngine:
    def __init__(self, services: BotServices, crops: tuple[str, ...] = ("turmeric", "banana")):
        self.svc = services
        self.crops = crops

    async def handle(self, msg: InboundMessage, ch: MessageChannel) -> None:
        """Entry point for background tasks: never raises."""
        try:
            await self._handle(msg, ch)
        except Exception:
            log.exception("bot error for %s", mask(msg.wa_id))

    async def _handle(self, msg: InboundMessage, ch: MessageChannel) -> None:
        if not await self.svc.first_time(msg.message_id):
            return  # duplicate delivery

        farmer = await self.svc.find_farmer(normalize_phone(msg.wa_id))
        if farmer is None:
            # Bilingual, and reveals nothing about anyone's data.
            await ch.send_text(
                msg.wa_id, f"{T['ta']['not_registered']}\n{T['en']['not_registered']}"
            )
            return

        lang = farmer.lang if farmer.lang in T else "ta"
        t = T[lang]
        intent = self._intent(msg)
        state = await self.svc.get_state(msg.wa_id)

        # First-contact notice (T2.2)
        if farmer.notice_sent_at is None:
            await self.svc.mark_notice_sent(farmer.id)
            await ch.send_text(msg.wa_id, t["notice"])

        # Consent and STOP works from ANY state (T2.3)
        if intent in ("alerts_off", "alerts_on"):
            if intent == "alerts_off":
                await self.svc.set_state(msg.wa_id, None)
            await self.svc.set_alerts(farmer.id, intent == "alerts_on")
            await ch.send_text(msg.wa_id, t[intent])
            return

        if intent == "cancel":
            await self.svc.set_state(msg.wa_id, None)
            await ch.send_text(msg.wa_id, t["cancelled"])
            return
        if intent == "menu":
            await self.svc.set_state(msg.wa_id, None)
            await self._menu(msg, ch, farmer, t)
            return
        if state is not None:
            await self._continue_harvest(msg, ch, t, lang, state)
            return

        if intent == "price":
            await self._price(msg, ch, t, lang, district=farmer.district)
        elif intent == "forecast":
            await self._forecast(msg, ch, t, lang)
        elif intent == "weather":
            text = await self.svc.weather_text(farmer.district, lang)
            await ch.send_text(msg.wa_id, text or t["unavailable"])
        elif intent == "harvest":
            await self.svc.set_state(msg.wa_id, ConvState("crop"))
            await self._ask_crop(msg, ch, t, lang)
        else:
            await ch.send_text(msg.wa_id, t["unknown"])

    # ---- intent routing

    @staticmethod
    def _intent(msg: InboundMessage) -> str | None:
        if msg.kind in ("button", "list"):
            # menu buttons use ids equal to intent names; flow buttons use "crop:", "grade:", ...
            return msg.text if msg.text in INTENT_KEYWORDS else None
        if msg.kind == "text":
            return detect_intent(msg.text)
        return None

    # ---- simple commands

    async def _menu(self, msg, ch, farmer: Farmer, t) -> None:
        await ch.send_buttons(
            msg.wa_id,
            t["menu"].format(name=farmer.name),
            [
                Button("price", t["b_price"]),
                Button("forecast", t["b_forecast"]),
                Button("harvest", t["b_harvest"]),
            ],
        )

    async def _price(self, msg, ch, t, lang, district: str = "Erode") -> None:
        crop = detect_crop(msg.text) if msg.kind == "text" else None
        crops = (crop,) if crop else self.crops
        lines = []
        for c in crops:
            p = await self.svc.latest_price(c, district=district)
            lines.append(
                format_price(p, lang) if p else t["no_price"].format(crop=crop_name(c, lang))
            )
        await ch.send_text(msg.wa_id, "\n".join(lines))

    async def _forecast(self, msg, ch, t, lang) -> None:
        crop = detect_crop(msg.text) if msg.kind == "text" else None
        crops = (crop,) if crop else self.crops
        parts = []
        for c in crops:
            text = await self.svc.forecast_text(c, lang)
            if text:
                parts.append(text)
        await ch.send_text(msg.wa_id, "\n\n".join(parts) or t["unavailable"])

    # ---- harvest submission flow: crop -> qty -> grade -> confirm

    async def _ask_crop(self, msg, ch, t, lang) -> None:
        await ch.send_buttons(
            msg.wa_id,
            t["ask_crop"],
            [Button(f"crop:{c}", crop_name(c, lang)) for c in self.crops],
        )

    async def _continue_harvest(self, msg, ch, t, lang, state: ConvState) -> None:
        text = msg.text.strip()
        to = msg.wa_id

        if state.step == "crop":
            crop = text.split(":", 1)[1] if text.startswith("crop:") else detect_crop(text)
            if crop not in self.crops:
                await self._ask_crop(msg, ch, t, lang)
                return
            state.data["crop"], state.step = crop, "qty"
            await self.svc.set_state(to, state)
            await ch.send_text(to, t["ask_qty"])

        elif state.step == "qty":
            qty = parse_qty(text)
            if qty is None:
                await ch.send_text(to, t["bad_qty"])
                return
            state.data["qty"], state.step = str(qty), "grade"
            await self.svc.set_state(to, state)
            await ch.send_buttons(to, t["ask_grade"], [Button(f"grade:{g}", g) for g in "ABC"])

        elif state.step == "grade":
            raw = text.split(":", 1)[1] if text.startswith("grade:") else text.upper()
            if raw not in ("A", "B", "C"):
                await ch.send_buttons(to, t["ask_grade"], [Button(f"grade:{g}", g) for g in "ABC"])
                return
            state.data["grade"], state.step = raw, "confirm"
            await self.svc.set_state(to, state)
            await ch.send_buttons(
                to,
                t["confirm"].format(
                    crop=crop_name(state.data["crop"], lang),
                    qty=state.data["qty"],
                    grade=raw,
                ),
                [Button("confirm:yes", t["b_yes"]), Button("confirm:no", t["b_no"])],
            )

        elif state.step == "confirm":
            answer = text.lower()
            if answer in ("confirm:yes", "yes", "y", "ஆம்"):
                await self.svc.submit_harvest(
                    farmer_id=await self._farmer_id(msg),
                    crop=state.data["crop"],
                    qty_kg=Decimal(state.data["qty"]),
                    grade=state.data["grade"],
                )
                await self.svc.set_state(to, None)
                await ch.send_text(
                    to,
                    t["saved"].format(
                        crop=crop_name(state.data["crop"], lang),
                        qty=state.data["qty"],
                        grade=state.data["grade"],
                    ),
                )
            elif answer in ("confirm:no", "no", "n", "இல்லை"):
                await self.svc.set_state(to, None)
                await ch.send_text(to, t["cancelled"])
            else:
                await ch.send_buttons(
                    to,
                    t["confirm"].format(
                        crop=crop_name(state.data["crop"], lang),
                        qty=state.data["qty"],
                        grade=state.data["grade"],
                    ),
                    [Button("confirm:yes", t["b_yes"]), Button("confirm:no", t["b_no"])],
                )

    async def _farmer_id(self, msg: InboundMessage) -> str:
        farmer = await self.svc.find_farmer(normalize_phone(msg.wa_id))
        assert farmer is not None  # checked at the top of _handle
        return farmer.id


# ---------------------------------------------------------------- in-memory services
# For local demos and tests. Replace with a DB-backed implementation in production.


class InMemoryServices:
    def __init__(
        self,
        farmers: dict[str, Farmer] | None = None,
        prices: dict[str, PriceInfo] | None = None,
    ) -> None:
        self.farmers = farmers or {}
        self.prices = prices or {}
        self.seen: set[str] = set()
        self.states: dict[str, ConvState] = {}
        self.harvests: list[tuple[str, str, Decimal, str]] = []
        self.alerts: dict[str, bool] = {}
        self.notices: set[str] = set()

    async def first_time(self, message_id: str) -> bool:
        if message_id in self.seen:
            return False
        self.seen.add(message_id)
        return True

    async def find_farmer(self, phone10: str) -> Farmer | None:
        return self.farmers.get(phone10)

    async def latest_price(self, crop: str, district: str | None = None) -> PriceInfo | None:
        return self.prices.get(crop)

    async def forecast_text(self, crop: str, lang: str) -> str | None:
        return None

    async def weather_text(self, district: str, lang: str) -> str | None:
        return None

    async def submit_harvest(self, farmer_id, crop, qty_kg, grade) -> None:
        self.harvests.append((farmer_id, crop, qty_kg, grade))

    async def set_alerts(self, farmer_id: str, on: bool) -> None:
        self.alerts[farmer_id] = on

    async def mark_notice_sent(self, farmer_id: str) -> None:
        self.notices.add(farmer_id)
        for phone, f in list(self.farmers.items()):
            if f.id == farmer_id:
                from datetime import datetime, timezone

                self.farmers[phone] = Farmer(
                    id=f.id,
                    name=f.name,
                    district=f.district,
                    lang=f.lang,
                    alerts_opt_in=f.alerts_opt_in,
                    notice_sent_at=datetime.now(timezone.utc),
                    fpo_id=f.fpo_id,
                )
                break

    async def get_state(self, wa_id: str) -> ConvState | None:
        return self.states.get(wa_id)

    async def set_state(self, wa_id: str, state: ConvState | None) -> None:
        if state is None:
            self.states.pop(wa_id, None)
        else:
            self.states[wa_id] = state
