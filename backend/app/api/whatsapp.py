"""WhatsApp Cloud API webhook.

GET  /api/whatsapp/webhook  -> Meta's one-time verification handshake
POST /api/whatsapp/webhook  -> inbound messages (signature-verified, processed in background)

Register in app/main.py:
    from app.api import whatsapp
    app.include_router(whatsapp.router)
"""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from functools import lru_cache

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.messaging.whatsapp_cloud import (
    WhatsAppCloudChannel,
    parse_status_updates,
    parse_webhook,
    verify_signature,
)
from app.services.bot import BotEngine
from app.services.whatsapp_status import WhatsAppStatusService

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@dataclass(frozen=True)
class WhatsAppSettings:
    verify_token: str  # any long random string you choose; also entered in Meta's dashboard
    app_secret: str  # Meta app secret (App settings > Basic); used to verify signatures
    access_token: str  # system-user token with whatsapp_business_messaging permission
    phone_number_id: str
    api_version: str  # use a Graph API version that is currently supported (check Meta docs)


@lru_cache
def get_wa_settings() -> WhatsAppSettings:
    return WhatsAppSettings(
        verify_token=settings.WHATSAPP_VERIFY_TOKEN or os.environ.get("WHATSAPP_VERIFY_TOKEN", ""),
        app_secret=settings.WHATSAPP_APP_SECRET or os.environ.get("WHATSAPP_APP_SECRET", ""),
        access_token=settings.WHATSAPP_ACCESS_TOKEN or os.environ.get("WHATSAPP_ACCESS_TOKEN", ""),
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID
        or os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
        api_version=settings.WHATSAPP_API_VERSION
        or os.environ.get("WHATSAPP_API_VERSION", "v23.0"),
    )


@lru_cache
def _channel() -> WhatsAppCloudChannel:
    cfg = get_wa_settings()
    return WhatsAppCloudChannel(cfg.access_token, cfg.phone_number_id, cfg.api_version)


def get_channel() -> WhatsAppCloudChannel:
    return _channel()


@lru_cache
def _bot() -> BotEngine:
    from app.services.db_bot_services import DbBotServices

    return BotEngine(DbBotServices())


def get_bot() -> BotEngine:
    """Return active BotEngine or raise 503 if WhatsApp is disabled via kill switch."""
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(status_code=503, detail="WhatsApp bot is currently disabled")
    return _bot()


@router.get("/webhook")
async def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
    cfg: WhatsAppSettings = Depends(get_wa_settings),
):
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(status_code=503, detail="WhatsApp bot is currently disabled")

    ok = (
        bool(cfg.verify_token)
        and mode == "subscribe"
        and hmac.compare_digest(token, cfg.verify_token)
    )
    if not ok:
        raise HTTPException(status_code=403, detail="Verification failed")
    return PlainTextResponse(challenge)


@lru_cache
def _status_service() -> WhatsAppStatusService:
    return WhatsAppStatusService()


def get_status_service() -> WhatsAppStatusService:
    return _status_service()


@router.post("/webhook")
async def receive(
    request: Request,
    background: BackgroundTasks,
    cfg: WhatsAppSettings = Depends(get_wa_settings),
    channel: WhatsAppCloudChannel = Depends(get_channel),
    bot: BotEngine = Depends(get_bot),
    status_service: WhatsAppStatusService = Depends(get_status_service),
):
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(status_code=503, detail="WhatsApp bot is currently disabled")

    raw = await request.body()  # signature is over the exact raw bytes, so read before parsing
    if not verify_signature(cfg.app_secret, raw, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=403, detail="Invalid signature")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON") from None

    # Reply 200 fast: Meta retries slow or failed webhooks. Real work happens in the background.
    # 1. Status callbacks (sent, delivered, read, failed)
    for update in parse_status_updates(payload):
        background.add_task(status_service.handle_status_update, update)

    # 2. Inbound messages
    for msg in parse_webhook(payload):
        background.add_task(bot.handle, msg, channel)
    return {"status": "ok"}

