"""Unit tests for WhatsApp bot wiring, settings validation, and kill switch."""

import pytest
from fastapi.testclient import TestClient

from app.api.whatsapp import get_bot
from app.config import Settings
from app.main import app
from app.services.bot import BotEngine


def test_production_refuses_missing_whatsapp_secrets():
    """In production with WhatsApp enabled, missing secrets must raise a fatal ValueError."""
    with pytest.raises(ValueError, match="FATAL SECURITY ERROR.*WHATSAPP_VERIFY_TOKEN"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 64,
            WHATSAPP_ENABLED=True,
            WHATSAPP_VERIFY_TOKEN="",
            WHATSAPP_APP_SECRET="",
            WHATSAPP_ACCESS_TOKEN="",
            WHATSAPP_PHONE_NUMBER_ID="",
        )


def test_production_allows_disabled_whatsapp_without_secrets():
    """In production with WhatsApp disabled, missing secrets should not raise."""
    cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 64,
        WHATSAPP_ENABLED=False,
    )
    assert cfg.WHATSAPP_ENABLED is False


def test_production_accepts_valid_whatsapp_secrets():
    """In production with WhatsApp enabled and all secrets present, startup succeeds."""
    cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 64,
        WHATSAPP_ENABLED=True,
        WHATSAPP_VERIFY_TOKEN="super_secure_verify_token_12345",
        WHATSAPP_APP_SECRET="super_secure_app_secret_12345",
        WHATSAPP_ACCESS_TOKEN="super_secure_access_token_12345",
        WHATSAPP_PHONE_NUMBER_ID="1234567890",
    )
    assert cfg.WHATSAPP_ENABLED is True


def test_kill_switch_returns_503(monkeypatch):
    """When WHATSAPP_ENABLED is False, both GET and POST webhooks return 503."""
    from app.config import settings

    monkeypatch.setattr(settings, "WHATSAPP_ENABLED", False)

    client = TestClient(app)

    # GET handshake returns 503
    res_get = client.get(
        "/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=tok&hub.challenge=123"
    )
    assert res_get.status_code == 503
    assert "disabled" in res_get.text.lower()

    # POST delivery returns 503
    res_post = client.post("/api/whatsapp/webhook", json={"entry": []})
    assert res_post.status_code == 503
    assert "disabled" in res_post.text.lower()


def test_get_bot_dependency_wired(monkeypatch):
    """get_bot() returns an active BotEngine when enabled."""
    from app.config import settings

    monkeypatch.setattr(settings, "WHATSAPP_ENABLED", True)
    bot = get_bot()
    assert isinstance(bot, BotEngine)
