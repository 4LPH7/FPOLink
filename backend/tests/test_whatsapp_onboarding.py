"""Tests for WhatsApp Phase 2: Onboarding, Identity, Consent, and Scoping (T2.1 - T2.4)."""

import hashlib
import hmac
import json
from datetime import date
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import whatsapp as wa
from app.messaging.base import Button
from app.services.bot import (
    BotEngine,
    ConvState,
    Farmer,
    InMemoryServices,
    PriceInfo,
    detect_intent,
)

SECRET = "test-secret"
VERIFY = "test-verify"


class MockChannel:
    def __init__(self):
        self.sent = []  # list of (to, kind, body, buttons)

    async def send_text(self, to, body):
        self.sent.append((to, "text", body, []))

    async def send_buttons(self, to, body, buttons: list[Button]):
        self.sent.append((to, "buttons", body, [b.id for b in buttons]))

    async def send_template(self, to, name, lang, params):
        self.sent.append((to, "template", name, params))


def build_payload(wa_id: str, text: str, msg_id: str = "m1"):
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
                            "contacts": [{"profile": {"name": "Test"}, "wa_id": wa_id}],
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


def post_webhook(client: TestClient, payload: dict):
    body = json.dumps(payload).encode()
    sig = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return client.post(
        "/api/whatsapp/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )


def test_intent_detection_stop_and_alerts():
    """T2.3: Verify STOP, halt, and Tamil நிறுத்து detection."""
    assert detect_intent("STOP") == "alerts_off"
    assert detect_intent("stop") == "alerts_off"
    assert detect_intent("HALT") == "alerts_off"
    assert detect_intent("நிறுத்து") == "alerts_off"
    assert detect_intent("நிறுத்துக") == "alerts_off"
    assert detect_intent("ALERTS OFF") == "alerts_off"
    assert detect_intent("alerts on") == "alerts_on"
    assert detect_intent("எச்சரிக்கை ஆன்") == "alerts_on"


def test_t2_2_first_contact_notice():
    """T2.2: First message from registered farmer gets DPDP notice and sets notice_sent_at."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at=None),
        },
        prices={
            "turmeric": PriceInfo(
                "turmeric", Decimal("120"), Decimal("110"), Decimal("130"), "Erode", date.today()
            ),
        },
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    app = FastAPI()
    app.include_router(wa.router)
    app.dependency_overrides[wa.get_wa_settings] = lambda: wa.WhatsAppSettings(
        VERIFY, SECRET, "tok", "123", "v23.0"
    )
    app.dependency_overrides[wa.get_channel] = lambda: ch
    app.dependency_overrides[wa.get_bot] = lambda: engine
    client = TestClient(app)

    # First message: triggers first-contact notice + intent response
    resp = post_webhook(client, build_payload("919876543210", "வணக்கம்", "msg-1"))
    assert resp.status_code == 200
    assert "f1" in svc.notices
    assert len(ch.sent) == 2
    # First sent item is the DPDP notice
    notice_body = ch.sent[0][2]
    assert "FPOLink" in notice_body and "DPDP" in notice_body
    # Second sent item is the menu
    assert ch.sent[1][1] == "buttons"

    # Second message: notice should NOT be sent again
    ch.sent.clear()
    resp2 = post_webhook(client, build_payload("919876543210", "விலை", "msg-2"))
    assert resp2.status_code == 200
    assert len(ch.sent) == 1
    assert "மஞ்சள்" in ch.sent[0][2]


def test_t2_3_stop_from_any_state_clears_conversation():
    """T2.3: STOP and நிறுத்து take effect immediately from within active harvest flow."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Kandasamy", "Erode", "ta", alerts_opt_in=True),
        },
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    app = FastAPI()
    app.include_router(wa.router)
    app.dependency_overrides[wa.get_wa_settings] = lambda: wa.WhatsAppSettings(
        VERIFY, SECRET, "tok", "123", "v23.0"
    )
    app.dependency_overrides[wa.get_channel] = lambda: ch
    app.dependency_overrides[wa.get_bot] = lambda: engine
    client = TestClient(app)

    # Simulate farmer currently in middle of harvest flow at step "qty"
    svc.states["919876543210"] = ConvState(step="qty", data={"crop": "turmeric"})
    assert svc.alerts.get("f1", True) is True

    # Farmer sends STOP
    resp = post_webhook(client, build_payload("919876543210", "STOP", "msg-stop"))
    assert resp.status_code == 200

    # Verify: state cleared, alerts turned OFF
    assert svc.states.get("919876543210") is None
    assert svc.alerts["f1"] is False
    assert any("நிறுத்தப்பட்டன" in s[2] for s in ch.sent)


def test_t2_3_tamil_niruthu_opt_out():
    """T2.3: Tamil keyword நிறுத்து opts out from alerts."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Kandasamy", "Erode", "ta", alerts_opt_in=True),
        },
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    app = FastAPI()
    app.include_router(wa.router)
    app.dependency_overrides[wa.get_wa_settings] = lambda: wa.WhatsAppSettings(
        VERIFY, SECRET, "tok", "123", "v23.0"
    )
    app.dependency_overrides[wa.get_channel] = lambda: ch
    app.dependency_overrides[wa.get_bot] = lambda: engine
    client = TestClient(app)

    resp = post_webhook(client, build_payload("919876543210", "நிறுத்து", "msg-ta-stop"))
    assert resp.status_code == 200
    assert svc.alerts["f1"] is False


def test_t2_4_unregistered_number_gets_zero_data():
    """T2.4: Unknown phone numbers get generic bilingual message and no price data."""
    svc = InMemoryServices(
        farmers={},
        prices={
            "turmeric": PriceInfo(
                "turmeric", Decimal("120"), Decimal("110"), Decimal("130"), "Erode", date.today()
            ),
        },
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    app = FastAPI()
    app.include_router(wa.router)
    app.dependency_overrides[wa.get_wa_settings] = lambda: wa.WhatsAppSettings(
        VERIFY, SECRET, "tok", "123", "v23.0"
    )
    app.dependency_overrides[wa.get_channel] = lambda: ch
    app.dependency_overrides[wa.get_bot] = lambda: engine
    client = TestClient(app)

    resp = post_webhook(client, build_payload("919999999999", "price", "msg-anon"))
    assert resp.status_code == 200
    assert len(ch.sent) == 1
    reply = ch.sent[0][2]
    # No price data, no market name, generic message
    assert "₹" not in reply
    assert "Erode" not in reply
    assert "not registered" in reply.lower() or "பதிவு செய்யப்படவில்லை" in reply
