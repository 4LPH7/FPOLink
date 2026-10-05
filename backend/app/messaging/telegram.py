"""Telegram Bot API adapter: update parsing, webhook secret check, and sending.

The BotEngine is transport-agnostic and addresses users by phone ("wa_id"). Telegram
addresses users by chat id, so a TelegramChatChannel is bound to one chat per update and
ignores the ``to`` argument the engine passes.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass

import httpx

from app.messaging.base import Button

log = logging.getLogger("telegram")

API_BASE = "https://api.telegram.org"
MAX_TEXT = 4096

# Slash commands -> text the BotEngine understands (keywords from INTENT_KEYWORDS).
COMMAND_MAP = {
    "/start": "menu",
    "/help": "menu",
    "/menu": "menu",
    "/price": "price",
    "/prices": "price",
    "/forecast": "forecast",
    "/harvest": "harvest",
    "/weather": "weather",
    "/buyers": "buyers",
    "/cancel": "cancel",
    "/stop": "alerts off",
    "/alerts": "alerts",
}

BOT_COMMANDS = [
    {"command": "start", "description": "Start / link your phone number"},
    {"command": "price", "description": "Latest mandi prices (e.g. /price turmeric)"},
    {"command": "forecast", "description": "7-day price forecast (e.g. /forecast banana)"},
    {"command": "harvest", "description": "Report a harvest to your FPO"},
    {"command": "weather", "description": "Weather for your district"},
    {"command": "buyers", "description": "Open buyer demand for your crops"},
    {"command": "cancel", "description": "Cancel the current step"},
    {"command": "help", "description": "Show the menu"},
]


def derive_webhook_secret(bot_token: str, explicit: str = "") -> str:
    """Secret Telegram echoes in X-Telegram-Bot-Api-Secret-Token (1-256 chars, [A-Za-z0-9_-])."""
    if explicit:
        return explicit
    if not bot_token:
        return ""
    return hashlib.sha256(f"fpolink-tg:{bot_token}".encode()).hexdigest()[:48]


def verify_secret(expected: str, header: str | None) -> bool:
    if not expected or not header:
        return False
    return hmac.compare_digest(expected, header)


@dataclass(frozen=True)
class TelegramUpdate:
    update_id: int
    chat_id: int
    user_id: int | None
    kind: str  # "text" | "button" | "contact" | media kinds | "unsupported"
    text: str = ""
    first_name: str = ""
    language_code: str = ""
    contact_phone: str = ""
    contact_user_id: int | None = None
    callback_query_id: str = ""


def map_command(text: str) -> str:
    """Translate '/price turmeric' or '/price@Fpo_Link_Bot' into engine text ('price turmeric')."""
    stripped = text.strip()
    if not stripped.startswith("/"):
        return stripped
    head, _, rest = stripped.partition(" ")
    cmd = head.split("@", 1)[0].lower()
    mapped = COMMAND_MAP.get(cmd)
    if mapped is None:
        return stripped.lstrip("/")
    return f"{mapped} {rest}".strip()


def parse_update(payload: dict) -> TelegramUpdate | None:
    """Parse a Telegram Update into a TelegramUpdate. Returns None for ignorable updates."""
    update_id = payload.get("update_id")
    if update_id is None:
        return None

    cq = payload.get("callback_query")
    if cq:
        msg = cq.get("message") or {}
        chat = msg.get("chat") or {}
        sender = cq.get("from") or {}
        if not chat.get("id"):
            return None
        return TelegramUpdate(
            update_id=update_id,
            chat_id=chat["id"],
            user_id=sender.get("id"),
            kind="button",
            text=cq.get("data", ""),
            first_name=sender.get("first_name", ""),
            language_code=sender.get("language_code", ""),
            callback_query_id=cq.get("id", ""),
        )

    msg = payload.get("message")
    if not msg:
        return None  # edited messages, channel posts, etc.
    chat = msg.get("chat") or {}
    if chat.get("type", "private") != "private" or not chat.get("id"):
        return None  # the bot only serves 1:1 chats (farmer data is personal)
    sender = msg.get("from") or {}
    base = dict(
        update_id=update_id,
        chat_id=chat["id"],
        user_id=sender.get("id"),
        first_name=sender.get("first_name", ""),
        language_code=sender.get("language_code", ""),
    )
    if "contact" in msg:
        c = msg["contact"]
        return TelegramUpdate(
            kind="contact",
            contact_phone=c.get("phone_number", ""),
            contact_user_id=c.get("user_id"),
            **base,
        )
    if "text" in msg:
        return TelegramUpdate(kind="text", text=msg["text"], **base)
    for media in ("voice", "audio", "photo", "document", "video", "sticker", "location"):
        if media in msg:
            return TelegramUpdate(kind="image" if media == "photo" else media, **base)
    return TelegramUpdate(kind="unsupported", **base)


class TelegramClient:
    """Thin async wrapper over the Bot API."""

    def __init__(self, token: str, timeout: float = 15.0):
        self.token = token
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.token)

    async def call(self, method: str, payload: dict | None = None, timeout: float | None = None):
        if not self.token:
            log.warning("Telegram token missing; skipping %s", method)
            return None
        url = f"{API_BASE}/bot{self.token}/{method}"
        try:
            async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
                r = await client.post(url, json=payload or {})
            data = r.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.error("Telegram %s failed: %s", method, type(exc).__name__)
            return None
        if not data.get("ok"):
            log.error("Telegram %s error: %s", method, data.get("description"))
            return None
        return data.get("result")


class TelegramChatChannel:
    """MessageChannel implementation bound to a single Telegram chat."""

    def __init__(self, client: TelegramClient, chat_id: int):
        self.client = client
        self.chat_id = chat_id
        self.sent: list[dict] = []  # handy for tests and debugging

    async def _send(self, payload: dict) -> bool:
        payload = {"chat_id": self.chat_id, **payload}
        self.sent.append(payload)
        result = await self.client.call("sendMessage", payload)
        return result is not None

    async def send_text(self, to: str, body: str) -> bool:
        return await self._send({"text": body[:MAX_TEXT]})

    async def send_buttons(self, to: str, body: str, buttons: list[Button]) -> bool:
        keyboard = [[{"text": b.title[:64], "callback_data": b.id[:64]}] for b in buttons]
        return await self._send(
            {"text": body[:MAX_TEXT], "reply_markup": {"inline_keyboard": keyboard}}
        )

    async def send_template(self, to: str, name: str, lang: str, params: list[str]) -> bool:
        # Telegram has no templates; render a plain message instead.
        return await self.send_text(to, " ".join([name, *params]))

    async def request_contact(self, body: str, button_text: str) -> bool:
        return await self._send(
            {
                "text": body,
                "reply_markup": {
                    "keyboard": [[{"text": button_text, "request_contact": True}]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                },
            }
        )

    async def remove_keyboard(self, body: str) -> bool:
        return await self._send({"text": body, "reply_markup": {"remove_keyboard": True}})
