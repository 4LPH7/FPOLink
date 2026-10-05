"""Telegram channel: parsing, linking/auto-registration, command routing, harvest flow, webhook."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database  # noqa: F401  (registers SQLite JSONB/UUID compilers)
from app.config import settings
from app.messaging.telegram import (
    TelegramChatChannel,
    derive_webhook_secret,
    map_command,
    parse_update,
)
from app.models.base import Base
from app.models.crop import Crop
from app.models.farmer import Farmer as DbFarmer
from app.models.fpo import FPO
from app.models.harvest import Harvest
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.user import User, UserRole
from app.services.bot import BotEngine
from app.services.db_bot_services import DbBotServices
from app.services.telegram_bot import TelegramBotService

CHAT = 555001


class FakeClient:
    """Records Bot API calls instead of hitting Telegram."""

    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self.token = "test-token"

    async def call(self, method, payload=None, timeout=None):
        self.calls.append((method, payload or {}))
        return {"message_id": len(self.calls)}

    def texts(self) -> list[str]:
        return [p.get("text", "") for m, p in self.calls if m == "sendMessage"]


@pytest.fixture
def factory():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with Session() as db:
        fpo = FPO(
            name="Erode Turmeric FPO",
            registration_number="TG-1",
            district="Erode",
            village="Perundurai",
            contact_phone="9000000000",
        )
        db.add(fpo)
        db.flush()
        user = User(name="Murugan", phone="9876543210", role=UserRole.FARMER, hashed_password="x")
        db.add(user)
        db.flush()
        db.add(
            DbFarmer(
                user_id=user.id,
                fpo_id=fpo.id,
                phone="9876543210",
                village="Perundurai",
                taluk="Perundurai",
                district="Erode",
                farm_area_acres=2.0,
                lang="en",
            )
        )
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg")
        market = Market(name="Erode Mandi", district="Erode", market_type="regulated")
        db.add_all([crop, market])
        db.flush()
        db.add(
            MarketPrice(
                crop_id=crop.id,
                market_id=market.id,
                district="Erode",
                price_date=date.today(),
                min_price=Decimal("120"),
                max_price=Decimal("140"),
                modal_price=Decimal("130"),
                source="ogd",
            )
        )
        db.commit()
    yield Session
    Base.metadata.drop_all(bind=engine)


def _svc(factory):
    client = FakeClient()
    return TelegramBotService(BotEngine(DbBotServices(db_factory=factory)), client, factory), client


def _text(uid, text, chat=CHAT):
    return parse_update(
        {
            "update_id": uid,
            "message": {
                "message_id": uid,
                "chat": {"id": chat, "type": "private"},
                "from": {"id": chat, "first_name": "Murugan", "language_code": "en"},
                "text": text,
            },
        }
    )


def _contact(uid, phone, contact_user_id=CHAT, chat=CHAT, name="Murugan"):
    return parse_update(
        {
            "update_id": uid,
            "message": {
                "message_id": uid,
                "chat": {"id": chat, "type": "private"},
                "from": {"id": chat, "first_name": name, "language_code": "en"},
                "contact": {"phone_number": phone, "user_id": contact_user_id},
            },
        }
    )


def _button(uid, data, chat=CHAT):
    return parse_update(
        {
            "update_id": uid,
            "callback_query": {
                "id": f"cb{uid}",
                "from": {"id": chat, "first_name": "Murugan"},
                "message": {"chat": {"id": chat, "type": "private"}},
                "data": data,
            },
        }
    )


def test_map_command_and_parse():
    assert map_command("/price turmeric") == "price turmeric"
    assert map_command("/forecast@Fpo_Link_Bot banana") == "forecast banana"
    assert map_command("/start") == "menu"
    assert map_command("hello") == "hello"
    assert parse_update({"update_id": 1, "message": {"chat": {"id": 1, "type": "group"}}}) is None
    assert _button(3, "price").kind == "button"
    assert derive_webhook_secret("abc") == derive_webhook_secret("abc")
    assert derive_webhook_secret("abc", "explicit") == "explicit"


@pytest.mark.anyio
async def test_unlinked_chat_is_asked_for_contact(factory):
    svc, client = _svc(factory)
    await svc.handle_update(_text(1, "/start"))
    method, payload = client.calls[-1]
    assert method == "sendMessage"
    assert payload["reply_markup"]["keyboard"][0][0]["request_contact"] is True


@pytest.mark.anyio
async def test_foreign_contact_rejected(factory):
    svc, client = _svc(factory)
    await svc.handle_update(_contact(1, "+919876543210", contact_user_id=999))
    assert svc.linked_phone(CHAT) is None


@pytest.mark.anyio
async def test_link_existing_farmer_then_price_and_harvest(factory):
    svc, client = _svc(factory)
    await svc.handle_update(_contact(1, "+91 98765 43210"))
    assert svc.linked_phone(CHAT) == "9876543210"
    assert any("Linked" in t for t in client.texts())

    await svc.handle_update(_text(2, "/price turmeric"))
    assert "13,000" in client.texts()[-1]  # Rs 130/kg -> Rs 13,000/quintal

    await svc.handle_update(_text(3, "/harvest"))
    await svc.handle_update(_button(4, "crop:turmeric"))
    await svc.handle_update(_text(5, "250"))
    await svc.handle_update(_button(6, "grade:A"))
    await svc.handle_update(_button(7, "confirm:yes"))
    assert "Harvest saved" in client.texts()[-1]
    with factory() as db:
        h = db.query(Harvest).one()
        assert float(h.quantity_kg) == 250.0
        assert h.source_message_id == "tg:7"
    assert ("answerCallbackQuery", {"callback_query_id": "cb4"}) in client.calls


@pytest.mark.anyio
async def test_duplicate_update_ignored(factory):
    svc, client = _svc(factory)
    await svc.handle_update(_contact(1, "9876543210"))
    n = len(client.calls)
    await svc.handle_update(_text(2, "/price"))
    await svc.handle_update(_text(2, "/price"))
    assert len(client.calls) == n + 1


@pytest.mark.anyio
async def test_auto_register_unknown_phone(factory, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_AUTO_REGISTER", True)
    svc, client = _svc(factory)
    await svc.handle_update(
        _contact(1, "+919123456789", chat=777, contact_user_id=777, name="Selvi")
    )
    assert svc.linked_phone(777) == "9123456789"
    with factory() as db:
        f = db.query(DbFarmer).filter(DbFarmer.phone == "9123456789").one()
        assert f.user.role == UserRole.FARMER
        assert f.user.consent_given is True


@pytest.mark.anyio
async def test_auto_register_disabled(factory, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_AUTO_REGISTER", False)
    svc, client = _svc(factory)
    await svc.handle_update(_contact(1, "+919123456789", chat=777, contact_user_id=777))
    assert svc.linked_phone(777) is None
    assert "not registered" in client.texts()[-1]


@pytest.mark.anyio
async def test_lang_toggle(factory):
    svc, client = _svc(factory)
    await svc.handle_update(_contact(1, "9876543210"))
    await svc.handle_update(_text(2, "/lang ta"))
    assert "தமிழ்" in client.texts()[-1]


@pytest.mark.anyio
async def test_channel_buttons_render_inline_keyboard():
    from app.messaging.base import Button

    client = FakeClient()
    ch = TelegramChatChannel(client, 42)
    await ch.send_buttons(
        "ignored", "Pick", [Button("price", "Price"), Button("harvest", "Harvest")]
    )
    payload = client.calls[0][1]
    assert payload["chat_id"] == 42
    assert payload["reply_markup"]["inline_keyboard"][1][0]["callback_data"] == "harvest"


def test_webhook_rejects_bad_secret(monkeypatch):
    from app.api import telegram as tg_api

    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setattr(settings, "TELEGRAM_ENABLED", True)
    received = []

    class Svc:
        async def handle_update(self, update):
            received.append(update)

    app = FastAPI()
    app.include_router(tg_api.router)
    app.dependency_overrides[tg_api.get_service] = lambda: Svc()
    client = TestClient(app)
    body = {"update_id": 9, "message": {"chat": {"id": 1, "type": "private"}, "text": "hi"}}

    assert client.post("/api/telegram/webhook", json=body).status_code == 403
    bad = {"X-Telegram-Bot-Api-Secret-Token": "nope"}
    assert client.post("/api/telegram/webhook", json=body, headers=bad).status_code == 403
    good = {"X-Telegram-Bot-Api-Secret-Token": tg_api.webhook_secret()}
    assert client.post("/api/telegram/webhook", json=body, headers=good).status_code == 200
    assert received and received[0].text == "hi"


def test_webhook_503_without_token(monkeypatch):
    from app.api import telegram as tg_api

    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "")
    app = FastAPI()
    app.include_router(tg_api.router)
    r = TestClient(app).post("/api/telegram/webhook", json={"update_id": 1})
    assert r.status_code == 503
