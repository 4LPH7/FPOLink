import hashlib
import hmac
import json
from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import whatsapp as wa
from app.messaging.base import Button
from app.messaging.whatsapp_cloud import parse_webhook, verify_signature
from app.services.bot import (
    BotEngine,
    Farmer,
    InMemoryServices,
    PriceInfo,
    detect_crop,
    detect_intent,
    parse_qty,
)

SECRET = "test-app-secret"
VERIFY = "test-verify-token"
PHONE_TA = "919876543210"
PHONE_EN = "919000000001"


class FakeChannel:
    def __init__(self):
        self.sent = []  # (to, kind, body, buttons)

    async def send_text(self, to, body):
        self.sent.append((to, "text", body, []))

    async def send_buttons(self, to, body, buttons: list[Button]):
        self.sent.append((to, "buttons", body, [b.id for b in buttons]))

    async def send_template(self, to, name, lang, params):
        self.sent.append((to, "template", name, params))


def make_services():
    return InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Muthu", "Erode", "ta"),
            "9000000001": Farmer("f2", "Ravi", "Erode", "en"),
        },
        prices={
            "turmeric": PriceInfo(
                "turmeric",
                Decimal("120.50"),
                Decimal("110"),
                Decimal("130"),
                "Erode",
                date(2026, 9, 18),
            ),
            "banana": PriceInfo(
                "banana", Decimal("28"), Decimal("25"), Decimal("32"), "Erode", date(2026, 9, 18)
            ),
        },
    )


@pytest.fixture
def env():
    svc = make_services()
    channel = FakeChannel()
    bot = BotEngine(svc)
    app = FastAPI()
    app.include_router(wa.router)
    cfg = wa.WhatsAppSettings(VERIFY, SECRET, "tok", "123", "v23.0")
    app.dependency_overrides[wa.get_wa_settings] = lambda: cfg
    app.dependency_overrides[wa.get_channel] = lambda: channel
    app.dependency_overrides[wa.get_bot] = lambda: bot
    return TestClient(app), svc, channel, app


def text_payload(wa_id, text, msg_id):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "contacts": [{"profile": {"name": "T"}, "wa_id": wa_id}],
                            "messages": [
                                {
                                    "from": wa_id,
                                    "id": msg_id,
                                    "timestamp": "1",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def button_payload(wa_id, button_id, msg_id):
    p = text_payload(wa_id, "", msg_id)
    p["entry"][0]["changes"][0]["value"]["messages"][0] = {
        "from": wa_id,
        "id": msg_id,
        "timestamp": "1",
        "type": "interactive",
        "interactive": {"type": "button_reply", "button_reply": {"id": button_id, "title": "x"}},
    }
    return p


def post(client, payload, secret=SECRET, sign=True):
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if sign:
        headers["X-Hub-Signature-256"] = (
            "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        )
    return client.post("/api/whatsapp/webhook", content=body, headers=headers)


# ---------------------------------------------------------------- webhook security


def test_verification_handshake(env):
    client, *_ = env
    r = client.get(
        "/api/whatsapp/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": VERIFY, "hub.challenge": "12345"},
    )
    assert r.status_code == 200 and r.text == "12345"


def test_verification_rejects_wrong_token(env):
    client, *_ = env
    r = client.get(
        "/api/whatsapp/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "1"},
    )
    assert r.status_code == 403


def test_rejects_bad_or_missing_signature(env):
    client, _, channel, _ = env
    payload = text_payload(PHONE_TA, "price", "m1")
    assert post(client, payload, secret="wrong").status_code == 403
    assert post(client, payload, sign=False).status_code == 403
    assert channel.sent == []


def test_empty_app_secret_never_verifies():
    body = b"{}"
    forged = "sha256=" + hmac.new(b"", body, hashlib.sha256).hexdigest()
    assert verify_signature("", body, forged) is False


def test_status_only_payload_is_ignored(env):
    client, _, channel, _ = env
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {"statuses": [{"id": "x", "status": "delivered"}]},
                    }
                ]
            }
        ],
    }
    assert post(client, payload).status_code == 200
    assert channel.sent == []
    assert parse_webhook(payload) == []


def test_invalid_json_with_valid_signature_is_400(env):
    client, *_ = env
    body = b"not json"
    sig = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    r = client.post("/api/whatsapp/webhook", content=body, headers={"X-Hub-Signature-256": sig})
    assert r.status_code == 400


# ---------------------------------------------------------------- behaviour


def test_price_reply_in_tamil_uses_quintal(env):
    client, _, channel, _ = env
    assert post(client, text_payload(PHONE_TA, "விலை", "m1")).status_code == 200
    to, kind, body, _ = channel.sent[0]
    assert to == PHONE_TA and kind == "text"
    assert "மஞ்சள்" in body and "12,050" in body and "குவிண்டால்" in body
    assert "வாழை" in body


def test_price_single_crop_english(env):
    client, _, channel, _ = env
    post(client, text_payload(PHONE_EN, "turmeric price", "m1"))
    body = channel.sent[0][2]
    assert "Turmeric" in body and "Banana" not in body and "quintal" in body


def test_duplicate_delivery_processed_once(env):
    client, _, channel, _ = env
    payload = text_payload(PHONE_EN, "price", "same-id")
    post(client, payload)
    post(client, payload)
    assert len(channel.sent) == 1


def test_unregistered_number_gets_generic_reply(env):
    client, _, channel, _ = env
    post(client, text_payload("911111111111", "price", "m1"))
    assert len(channel.sent) == 1
    assert "₹" not in channel.sent[0][2]


def test_menu_has_three_buttons(env):
    client, _, channel, _ = env
    post(client, text_payload(PHONE_EN, "hi", "m1"))
    assert channel.sent[0][1] == "buttons"
    assert channel.sent[0][3] == ["price", "forecast", "harvest"]


def test_menu_button_tap_triggers_price(env):
    client, _, channel, _ = env
    post(client, button_payload(PHONE_EN, "price", "m1"))
    assert "quintal" in channel.sent[0][2]


def test_harvest_flow_end_to_end(env):
    client, svc, channel, _ = env
    post(client, text_payload(PHONE_EN, "harvest", "m1"))
    assert channel.sent[-1][3] == ["crop:turmeric", "crop:banana"]
    post(client, button_payload(PHONE_EN, "crop:turmeric", "m2"))
    post(client, text_payload(PHONE_EN, "abc", "m3"))  # invalid quantity
    assert "valid number" in channel.sent[-1][2]
    post(client, text_payload(PHONE_EN, "250 kg", "m4"))
    assert channel.sent[-1][3] == ["grade:A", "grade:B", "grade:C"]
    post(client, button_payload(PHONE_EN, "grade:A", "m5"))
    assert channel.sent[-1][3] == ["confirm:yes", "confirm:no"]
    post(client, button_payload(PHONE_EN, "confirm:yes", "m6"))
    assert svc.harvests == [("f2", "turmeric", Decimal("250"), "A")]
    assert "saved" in channel.sent[-1][2].lower()
    assert svc.states == {}


def test_cancel_clears_state(env):
    client, svc, channel, _ = env
    post(client, text_payload(PHONE_EN, "harvest", "m1"))
    post(client, text_payload(PHONE_EN, "cancel", "m2"))
    assert svc.states == {} and svc.harvests == []


def test_alerts_opt_in_and_out(env):
    client, svc, _, _ = env
    post(client, text_payload(PHONE_EN, "alerts on", "m1"))
    assert svc.alerts["f2"] is True
    post(client, text_payload(PHONE_EN, "alerts off", "m2"))
    assert svc.alerts["f2"] is False


# ---------------------------------------------------------------- helpers


def test_intent_and_crop_detection():
    assert detect_intent("Price of turmeric?") == "price"
    assert detect_intent("விலையை சொல்லுங்கள்") == "price"  # Tamil suffix
    assert detect_intent("which") is None  # "hi" must not match inside words
    assert detect_crop("மஞ்சள் விலை") == "turmeric"
    assert detect_crop("vazhai") == "banana"


def test_parse_qty_bounds():
    assert parse_qty("1,250 kg") == Decimal("1250")
    assert parse_qty("0") is None
    assert parse_qty("999999") is None
    assert parse_qty("no number") is None
