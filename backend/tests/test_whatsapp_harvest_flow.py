"""Tests for WhatsApp Harvest Submission and Robustness (T3.2 - T3.3)."""

import hashlib
import hmac
import json
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import whatsapp as wa
from app.messaging.base import Button, InboundMessage
from app.models.base import Base
from app.models.crop import Crop
from app.models.farmer import Farmer as DbFarmer
from app.models.fpo import FPO
from app.models.harvest import Harvest, HarvestGrade
from app.models.user import User, UserRole
from app.services.bot import BotEngine, ConvState, Farmer, InMemoryServices
from app.services.db_bot_services import DbBotServices

SECRET = "test-secret"
VERIFY = "test-verify"


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(PgUUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


class MockChannel:
    def __init__(self):
        self.sent = []  # list of (to, kind, body, buttons)

    async def send_text(self, to, body):
        self.sent.append((to, "text", body, []))
        return True

    async def send_buttons(self, to, body, buttons: list[Button]):
        self.sent.append((to, "buttons", body, [b.id for b in buttons]))
        return True

    async def send_template(self, to, name, lang, params):
        self.sent.append((to, "template", name, params))
        return True


def build_payload(wa_id: str, text: str, msg_id: str = "m1", msg_type: str = "text"):
    msg_dict = {
        "from": wa_id,
        "id": msg_id,
        "timestamp": "1",
        "type": msg_type,
    }
    if msg_type == "text":
        msg_dict["text"] = {"body": text}
    elif msg_type == "button":
        msg_dict["type"] = "interactive"
        msg_dict["interactive"] = {
            "type": "button_reply",
            "button_reply": {"id": text, "title": text},
        }
    elif msg_type in ("audio", "image"):
        msg_dict["type"] = msg_type
        msg_dict[msg_type] = {"id": "media-123"}

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
                            "messages": [msg_dict],
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


def test_harvest_chat_full_flow():
    """T3.2: Complete multi-step conversational harvest flow."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at="done"),
        }
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

    # 1. Farmer initiates harvest
    resp1 = post_webhook(client, build_payload("919876543210", "அறுவடை", "msg-1"))
    assert resp1.status_code == 200
    assert ch.sent[-1][1] == "buttons"
    assert "crop:turmeric" in ch.sent[-1][3]

    # 2. Select crop
    ch.sent.clear()
    resp2 = post_webhook(
        client, build_payload("919876543210", "crop:turmeric", "msg-2", msg_type="button")
    )
    assert resp2.status_code == 200
    assert "கிலோ" in ch.sent[-1][2] or "kg" in ch.sent[-1][2].lower()

    # 3. Enter quantity
    ch.sent.clear()
    resp3 = post_webhook(client, build_payload("919876543210", "250", "msg-3"))
    assert resp3.status_code == 200
    assert ch.sent[-1][1] == "buttons"
    assert "grade:A" in ch.sent[-1][3]

    # 4. Select grade
    ch.sent.clear()
    resp4 = post_webhook(
        client, build_payload("919876543210", "grade:A", "msg-4", msg_type="button")
    )
    assert resp4.status_code == 200
    assert "confirm:yes" in ch.sent[-1][3]

    # 5. Confirm harvest
    ch.sent.clear()
    resp5 = post_webhook(
        client, build_payload("919876543210", "confirm:yes", "msg-5", msg_type="button")
    )
    assert resp5.status_code == 200
    assert "அறுவடை சேமிக்கப்பட்டது" in ch.sent[-1][2]
    assert svc.harvests == [("f1", "turmeric", Decimal("250"), "A")]
    assert svc.states.get("919876543210") is None


def test_harvest_webhook_retry_idempotency():
    """T3.1 & T3.2: Duplicate delivery of final confirmation creates only 1 harvest."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at="done"),
        }
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    # Set state ready for confirm
    svc.states["919876543210"] = ConvState(
        step="confirm", data={"crop": "turmeric", "qty": "300", "grade": "B"}
    )

    # Send confirm
    msg1 = InboundMessage(
        message_id="dup-msg-id", wa_id="919876543210", kind="text", text="confirm:yes"
    )
    import asyncio

    asyncio.run(engine.handle(msg1, ch))

    assert len(svc.harvests) == 1

    # Meta retries same message ID -> ignored at top of handle
    asyncio.run(engine.handle(msg1, ch))
    assert len(svc.harvests) == 1


def test_harvest_retry_cap_resets_to_menu():
    """T3.3: 3 invalid input attempts reset state and send menu."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at="done"),
        }
    )
    ch = MockChannel()
    engine = BotEngine(svc)
    svc.states["919876543210"] = ConvState(step="qty", data={"crop": "turmeric"})

    import asyncio

    # Strike 1
    asyncio.run(
        engine.handle(
            InboundMessage(
                message_id="m-1", wa_id="919876543210", kind="text", text="invalid-number"
            ),
            ch,
        )
    )
    state = asyncio.run(svc.get_state("919876543210"))
    assert state.data["retries"] == 1

    # Strike 2
    asyncio.run(
        engine.handle(
            InboundMessage(message_id="m-2", wa_id="919876543210", kind="text", text="still-bad"),
            ch,
        )
    )
    state = asyncio.run(svc.get_state("919876543210"))
    assert state.data["retries"] == 2

    # Strike 3 -> Clears state and sends menu
    ch.sent.clear()
    asyncio.run(
        engine.handle(
            InboundMessage(
                message_id="m-3", wa_id="919876543210", kind="text", text="third-strike"
            ),
            ch,
        )
    )
    assert asyncio.run(svc.get_state("919876543210")) is None
    # Sent too_many_retries + menu buttons
    assert any("மீண்டும் தொடங்குவோம்" in s[2] or "start over" in s[2].lower() for s in ch.sent)


def test_media_unsupported_fallback():
    """T3.3: Inbound audio/image receives friendly guidance message."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at="done"),
        }
    )
    ch = MockChannel()
    engine = BotEngine(svc)

    import asyncio

    asyncio.run(
        engine.handle(
            InboundMessage(message_id="m-audio-1", wa_id="919876543210", kind="audio", text=""), ch
        )
    )
    assert len(ch.sent) == 1
    assert "FPOLink" in ch.sent[0][2]
    assert "மீடியாவை ஏற்க முடியாது" in ch.sent[0][2] or "cannot process" in ch.sent[0][2].lower()


def test_rate_limiter():
    """T3.3: Sliding window rate limit stops replies and warns once."""
    svc = InMemoryServices(
        farmers={
            "9876543210": Farmer("f1", "Periyasamy", "Erode", "ta", notice_sent_at="done"),
        }
    )
    ch = MockChannel()
    # Set limit to 3 for testing
    engine = BotEngine(svc, rate_limit_max=3, rate_limit_window_seconds=60.0)

    import asyncio

    # Messages 1, 2, 3 succeed
    for i in range(1, 4):
        asyncio.run(
            engine.handle(
                InboundMessage(
                    message_id=f"msg-{i}", wa_id="919876543210", kind="text", text="menu"
                ),
                ch,
            )
        )
    assert len(ch.sent) == 3

    # Message 4 exceeds limit -> Sends warning
    ch.sent.clear()
    asyncio.run(
        engine.handle(
            InboundMessage(message_id="msg-4", wa_id="919876543210", kind="text", text="menu"), ch
        )
    )
    assert len(ch.sent) == 1
    assert "Rate limit exceeded" in ch.sent[0][2] or "அதிக செய்திகள்" in ch.sent[0][2]

    # Message 5 -> Dropped, zero replies sent
    ch.sent.clear()
    asyncio.run(
        engine.handle(
            InboundMessage(message_id="msg-5", wa_id="919876543210", kind="text", text="menu"), ch
        )
    )
    assert len(ch.sent) == 0


@pytest.mark.anyio
async def test_db_bot_services_submit_harvest_persistence():
    """T3.2: Verify DbBotServices.submit_harvest stores Harvest with grade and source_message_id in DB."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Seed FPO, Farmer, Crop
    with TestingSession() as db:
        fpo = FPO(
            name="Test FPO",
            registration_number="FPO-TEST-1",
            district="Erode",
            village="Modakkurichi",
            contact_phone="9876543210",
        )
        db.add(fpo)
        db.flush()

        farmer_user = User(
            name="Kavitha",
            phone="9876543210",
            role=UserRole.FARMER,
            hashed_password="hash",
        )
        db.add(farmer_user)
        db.flush()

        farmer = DbFarmer(
            user_id=farmer_user.id,
            fpo_id=fpo.id,
            phone="9876543210",
            village="Modakkurichi",
            taluk="Erode",
            district="Erode",
            farm_area_acres=2.0,
        )
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg")
        db.add_all([farmer, crop])
        db.commit()
        farmer_id_str = str(farmer.id)

    db_services = DbBotServices(db_factory=TestingSession)

    # 1. Submit harvest via db_services
    await db_services.submit_harvest(
        farmer_id=farmer_id_str,
        crop="turmeric",
        qty_kg=Decimal("450.0"),
        grade="A",
        source_message_id="wa-idemp-1",
    )

    with TestingSession() as db:
        h = db.query(Harvest).first()
        assert h is not None
        assert h.quantity_kg == 450.0
        assert h.grade == HarvestGrade.A
        assert h.status == "SUBMITTED" or h.status.value == "SUBMITTED"
        assert h.source_message_id == "wa-idemp-1"

    # 2. Retry with same source_message_id -> Does not insert duplicate
    await db_services.submit_harvest(
        farmer_id=farmer_id_str,
        crop="turmeric",
        qty_kg=Decimal("450.0"),
        grade="A",
        source_message_id="wa-idemp-1",
    )

    with TestingSession() as db:
        assert db.query(Harvest).count() == 1

    Base.metadata.drop_all(bind=engine)
