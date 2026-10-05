# ruff: noqa: E501  (Tamil message strings are long)
"""Telegram front-end for the transport-agnostic BotEngine.

Flow:
1. Unknown chat -> ask the user to share their phone number (Telegram contact button).
2. Contact shared (must be the sender's own contact) -> link chat to the farmer with that
   phone (users.telegram_chat_id). If no farmer exists and auto-registration is enabled,
   a minimal farmer profile is created under the default FPO so the FPO can complete it.
3. Linked chat -> commands/text/buttons are converted to InboundMessage and handed to
   BotEngine, which runs price / forecast / harvest / weather / buyers flows.
"""

from __future__ import annotations

import logging
import re
import secrets
from datetime import datetime, timezone

from app.config import settings
from app.database import SessionLocal
from app.messaging.base import InboundMessage
from app.messaging.telegram import TelegramChatChannel, TelegramClient, TelegramUpdate, map_command
from app.services.bot import BotEngine

log = logging.getLogger("telegram.bot")

TG_TEXT = {
    "welcome": (
        "வணக்கம்! FPOLink-க்கு நல்வரவு 🌾\n"
        "மண்டி விலை, 7-நாள் விலை கணிப்பு மற்றும் அறுவடை பதிவுக்கு உங்கள் தொலைபேசி எண்ணைப் பகிரவும்.\n\n"
        "Welcome to FPOLink 🌾\n"
        "Share your phone number (button below) to get mandi prices, 7-day forecasts and report harvests to your FPO."
    ),
    "share_button": "📱 Share phone number / எண்ணைப் பகிர்",
    "own_contact_only": "Please share YOUR OWN number using the button. / உங்கள் சொந்த எண்ணை மட்டும் பகிரவும்.",
    "linked": "✅ இணைக்கப்பட்டது / Linked: {name}",
    "registered": (
        "✅ புதிய விவசாயி பதிவு செய்யப்பட்டது ({fpo}). உங்கள் கிராமம், நிலப்பரப்பு விவரங்களை FPO முடிக்கும்.\n"
        "✅ New farmer profile created under {fpo}. Your FPO will complete village/farm details."
    ),
    "not_registered": (
        "இந்த எண் பதிவு செய்யப்படவில்லை. பதிவு செய்ய உங்கள் FPO-வைத் தொடர்பு கொள்ளவும்.\n"
        "This number is not registered. Please contact your FPO to register."
    ),
    "lang_set": {"ta": "மொழி: தமிழ் ✅", "en": "Language: English ✅"},
    "unlinked": "🔓 Unlinked. Send /start to link again.",
}


def phone10(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    return digits[-10:] if len(digits) >= 10 else digits


class TelegramBotService:
    def __init__(self, engine: BotEngine, client: TelegramClient, db_factory=SessionLocal):
        self.engine = engine
        self.client = client
        self.db_factory = db_factory

    # ------------------------------------------------------------ DB helpers

    def linked_phone(self, chat_id: int) -> str | None:
        from app.models.farmer import Farmer
        from app.models.user import User

        with self.db_factory() as db:
            row = (
                db.query(Farmer, User)
                .join(User, Farmer.user_id == User.id)
                .filter(User.telegram_chat_id == str(chat_id))
                .first()
            )
            if not row:
                return None
            farmer, user = row
            return phone10(farmer.phone or user.phone)

    def link_contact(self, update: TelegramUpdate) -> tuple[str, str]:
        """Link the chat to a farmer by phone. Returns (status, display) where status is
        'linked' | 'registered' | 'not_registered'."""
        from app.models.farmer import Farmer
        from app.models.fpo import FPO
        from app.models.user import User, UserRole
        from app.services.auth import hash_password

        p10 = phone10(update.contact_phone)
        if len(p10) != 10:
            return "not_registered", ""
        now = datetime.now(timezone.utc)
        with self.db_factory() as db:
            # Unlink any other account previously bound to this chat.
            db.query(User).filter(User.telegram_chat_id == str(update.chat_id)).update(
                {User.telegram_chat_id: None}, synchronize_session=False
            )
            farmer = (
                db.query(Farmer)
                .join(User, Farmer.user_id == User.id)
                .filter((Farmer.phone == p10) | (User.phone == p10) | (User.phone.endswith(p10)))
                .first()
            )
            if farmer:
                farmer.user.telegram_chat_id = str(update.chat_id)
                db.commit()
                return "linked", farmer.user.name

            if not settings.TELEGRAM_AUTO_REGISTER:
                db.commit()
                return "not_registered", ""
            if db.query(User).filter(User.phone == p10).first():
                # Phone belongs to a staff/buyer account: never turn it into a farmer.
                db.commit()
                return "not_registered", ""
            fpo = (
                db.query(FPO).filter(FPO.district.ilike(f"{settings.DEFAULT_DISTRICT}%")).first()
                or db.query(FPO).first()
            )
            if fpo is None:
                db.commit()
                return "not_registered", ""
            lang = "en" if (update.language_code or "").startswith("en") else "ta"
            user = User(
                name=(update.first_name or "Farmer")[:100],
                phone=p10,
                role=UserRole.FARMER,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                language_preference=lang,
                telegram_chat_id=str(update.chat_id),
                consent_given=True,
                consent_date=now,
            )
            db.add(user)
            db.flush()
            db.add(
                Farmer(
                    user_id=user.id,
                    fpo_id=fpo.id,
                    phone=p10,
                    village="Not provided",
                    taluk="Not provided",
                    district=fpo.district or settings.DEFAULT_DISTRICT,
                    farm_area_acres=0.0,
                    lang=lang,
                )
            )
            db.commit()
            return "registered", fpo.name

    def set_lang(self, chat_id: int, lang: str | None) -> str | None:
        from app.models.farmer import Farmer
        from app.models.user import User

        with self.db_factory() as db:
            farmer = (
                db.query(Farmer)
                .join(User, Farmer.user_id == User.id)
                .filter(User.telegram_chat_id == str(chat_id))
                .first()
            )
            if not farmer:
                return None
            new = lang if lang in ("ta", "en") else ("en" if farmer.lang == "ta" else "ta")
            farmer.lang = new
            db.commit()
            return new

    def unlink(self, chat_id: int) -> None:
        from app.models.user import User

        with self.db_factory() as db:
            db.query(User).filter(User.telegram_chat_id == str(chat_id)).update(
                {User.telegram_chat_id: None}, synchronize_session=False
            )
            db.commit()

    # ------------------------------------------------------------ entry point

    async def handle_update(self, update: TelegramUpdate) -> TelegramChatChannel:
        """Process one update. Never raises (runs as a background task)."""
        ch = TelegramChatChannel(self.client, update.chat_id)
        try:
            await self._handle(update, ch)
        except Exception:
            log.exception("telegram update %s failed", update.update_id)
        return ch

    async def _handle(self, update: TelegramUpdate, ch: TelegramChatChannel) -> None:
        if update.callback_query_id:
            await self.client.call(
                "answerCallbackQuery", {"callback_query_id": update.callback_query_id}
            )

        if update.kind == "contact":
            if update.contact_user_id is None or update.contact_user_id != update.user_id:
                await ch.request_contact(TG_TEXT["own_contact_only"], TG_TEXT["share_button"])
                return
            status, display = self.link_contact(update)
            if status == "not_registered":
                await ch.remove_keyboard(TG_TEXT["not_registered"])
                return
            if status == "registered":
                await ch.remove_keyboard(TG_TEXT["registered"].format(fpo=display))
            else:
                await ch.remove_keyboard(TG_TEXT["linked"].format(name=display))
            await self._to_engine(update, ch, phone10(update.contact_phone), "text", "menu")
            return

        text = update.text or ""
        cmd = (
            text.strip().split(" ", 1)[0].split("@", 1)[0].lower() if update.kind == "text" else ""
        )

        if cmd == "/unlink":
            self.unlink(update.chat_id)
            await ch.remove_keyboard(TG_TEXT["unlinked"])
            return

        p10 = self.linked_phone(update.chat_id)
        if p10 is None:
            await ch.request_contact(TG_TEXT["welcome"], TG_TEXT["share_button"])
            return

        if cmd in ("/lang", "/language"):
            arg = text.strip().split(" ", 1)[1].strip().lower() if " " in text.strip() else None
            new = self.set_lang(update.chat_id, arg)
            if new:
                await ch.send_text(str(update.chat_id), TG_TEXT["lang_set"][new])
            return

        engine_text = map_command(text) if update.kind == "text" else text
        await self._to_engine(update, ch, p10, update.kind, engine_text)

    async def _to_engine(self, update, ch, p10: str, kind: str, text: str) -> None:
        msg = InboundMessage(
            message_id=f"tg:{update.update_id}",
            wa_id=f"91{p10}",
            kind=kind,
            text=text,
            profile_name=update.first_name,
        )
        await self.engine.handle(msg, ch)
