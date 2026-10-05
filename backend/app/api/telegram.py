"""Telegram bot webhook (farmer channel).

POST /api/telegram/webhook     -> updates from Telegram (secret-token verified, processed in background)
GET  /api/telegram/status      -> staff view of bot + webhook health
POST /api/telegram/set-webhook -> (admin) re-register the webhook and command menu
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.api.deps import require_role
from app.config import settings
from app.messaging.telegram import (
    BOT_COMMANDS,
    TelegramClient,
    derive_webhook_secret,
    parse_update,
    verify_secret,
)
from app.models.user import User

log = logging.getLogger("telegram.api")

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

WEBHOOK_PATH = "/api/telegram/webhook"


def public_base_url() -> str:
    return (settings.PUBLIC_API_URL or os.environ.get("RENDER_EXTERNAL_URL", "")).rstrip("/")


def webhook_secret() -> str:
    return derive_webhook_secret(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_WEBHOOK_SECRET)


@lru_cache
def get_client() -> TelegramClient:
    return TelegramClient(settings.TELEGRAM_BOT_TOKEN)


@lru_cache
def _service():
    from app.services.bot import BotEngine
    from app.services.db_bot_services import DbBotServices
    from app.services.telegram_bot import TelegramBotService

    return TelegramBotService(BotEngine(DbBotServices()), get_client())


def get_service():
    if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot is not configured")
    return _service()


async def register_webhook(client: TelegramClient) -> dict:
    """Point Telegram at this API and publish the command menu."""
    base = public_base_url()
    if not base:
        return {"ok": False, "reason": "PUBLIC_API_URL / RENDER_EXTERNAL_URL not set"}
    url = f"{base}{WEBHOOK_PATH}"
    result = await client.call(
        "setWebhook",
        {
            "url": url,
            "secret_token": webhook_secret(),
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": False,
        },
    )
    await client.call("setMyCommands", {"commands": BOT_COMMANDS})
    return {"ok": result is not None, "url": url}


@router.post("/webhook")
async def receive(request: Request, background: BackgroundTasks, svc=Depends(get_service)):
    if not verify_secret(webhook_secret(), request.headers.get("X-Telegram-Bot-Api-Secret-Token")):
        raise HTTPException(status_code=403, detail="Invalid secret token")
    try:
        payload = json.loads(await request.body())
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON") from None
    update = parse_update(payload)
    if update is not None:
        # Reply 200 fast; Telegram retries slow webhooks. Dedup happens in BotServices.first_time.
        background.add_task(svc.handle_update, update)
    return {"ok": True}


@router.get("/status")
async def status(_: User = Depends(require_role(["admin", "fpo_admin", "fpo_staff"]))):
    configured = bool(settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN)
    info = {
        "enabled": settings.TELEGRAM_ENABLED,
        "configured": configured,
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
        "bot_link": f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}",
        "public_api_url": public_base_url() or None,
        "webhook": None,
        "linked_farmers": 0,
    }
    from app.database import SessionLocal

    with SessionLocal() as db:
        info["linked_farmers"] = db.query(User).filter(User.telegram_chat_id.isnot(None)).count()
    if configured:
        wh = await get_client().call("getWebhookInfo")
        if wh is not None:
            info["webhook"] = {
                "url": wh.get("url") or None,
                "pending_update_count": wh.get("pending_update_count", 0),
                "last_error_message": wh.get("last_error_message"),
            }
    return info


@router.post("/set-webhook")
async def set_webhook(_: User = Depends(require_role(["admin"]))):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="TELEGRAM_BOT_TOKEN not set")
    return await register_webhook(get_client())
