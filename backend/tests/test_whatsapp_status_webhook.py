"""Tests for T4.1: Status webhooks (delivered/read/failed) and unreachable number tracking."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.whatsapp import get_status_service
from app.config import settings
from app.main import app
from app.messaging.base import StatusUpdate
from app.messaging.whatsapp_cloud import parse_status_updates
from app.models.base import Base
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.user import User, UserRole
from app.models.whatsapp import OutboundMessage, WhatsAppRecipientStatus
from app.services.whatsapp_status import WhatsAppStatusService


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def status_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    yield TestingSession
    Base.metadata.drop_all(engine)


def test_parse_status_updates_payload():
    """Verify parse_status_updates extracts delivered, read, and failed statuses from Meta payload."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "12345",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "99999",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.HBgL12345",
                                    "status": "delivered",
                                    "timestamp": "1727000000",
                                    "recipient_id": "919876543210",
                                },
                                {
                                    "id": "wamid.HBgL67890",
                                    "status": "failed",
                                    "timestamp": "1727000100",
                                    "recipient_id": "919876543211",
                                    "errors": [
                                        {
                                            "code": 131026,
                                            "title": "Receiver is incapable of receiving this message",
                                            "message": "Recipient not on WhatsApp",
                                        }
                                    ],
                                },
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    updates = parse_status_updates(payload)
    assert len(updates) == 2

    assert updates[0].meta_message_id == "wamid.HBgL12345"
    assert updates[0].status == "delivered"
    assert updates[0].recipient_id == "919876543210"

    assert updates[1].meta_message_id == "wamid.HBgL67890"
    assert updates[1].status == "failed"
    assert updates[1].recipient_id == "919876543211"
    assert updates[1].errors[0]["code"] == 131026


def test_status_service_updates_outbound_and_tracks_consecutive_failures(status_db):
    """Status service should update OutboundMessage and track recipient failure count."""
    service = WhatsAppStatusService(db_factory=status_db)

    # Pre-populate an outbound message and a matching farmer
    with status_db() as db:
        user = User(
            id=uuid.uuid4(),
            name="Murugan",
            phone="9876543210",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        fpo = FPO(
            id=uuid.uuid4(),
            name="Erode Turmeric FPO",
            registration_number="FPO-001",
            district="Erode",
            village="Perundurai",
            contact_phone="9876543210",
        )
        db.add_all([user, fpo])
        db.flush()

        farmer = Farmer(
            id=uuid.uuid4(),
            user_id=user.id,
            fpo_id=fpo.id,
            phone="9876543210",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=3.5,
            is_unreachable=False,
        )
        db.add(farmer)

        outbound = OutboundMessage(
            id=uuid.uuid4(),
            wa_id="919876543210",
            meta_message_id="wamid.test1",
            category="utility",
            template="daily_price_digest",
            status="sent",
        )
        db.add(outbound)
        db.commit()

    # 1. First failure
    update1 = StatusUpdate(
        meta_message_id="wamid.test1",
        recipient_id="919876543210",
        status="failed",
        errors=[{"code": 131026, "title": "Undeliverable"}],
    )
    service.handle_status_update(update1)

    with status_db() as db:
        out = (
            db.query(OutboundMessage)
            .filter(OutboundMessage.meta_message_id == "wamid.test1")
            .first()
        )
        assert out.status == "failed"
        assert out.error_details[0]["code"] == 131026

        recip = (
            db.query(WhatsAppRecipientStatus)
            .filter(WhatsAppRecipientStatus.wa_id == "919876543210")
            .first()
        )
        assert recip is not None
        assert recip.consecutive_failures == 1
        assert recip.is_unreachable is False
        assert service.is_recipient_reachable("919876543210") is True

    # 2. Second failure
    service.handle_status_update(
        StatusUpdate(
            meta_message_id="wamid.test1",
            recipient_id="919876543210",
            status="failed",
            errors=[{"code": 131026, "title": "Undeliverable"}],
        )
    )

    # 3. Third failure -> marks unreachable!
    service.handle_status_update(
        StatusUpdate(
            meta_message_id="wamid.test1",
            recipient_id="919876543210",
            status="failed",
            errors=[{"code": 131026, "title": "Undeliverable"}],
        )
    )

    with status_db() as db:
        recip = (
            db.query(WhatsAppRecipientStatus)
            .filter(WhatsAppRecipientStatus.wa_id == "919876543210")
            .first()
        )
        assert recip.consecutive_failures == 3
        assert recip.is_unreachable is True
        assert service.is_recipient_reachable("919876543210") is False

        # Farmer record is also synchronized
        farmer = db.query(Farmer).filter(Farmer.phone == "9876543210").first()
        assert farmer.is_unreachable is True

    # 4. Successful delivery resets failure counter and unmarks unreachable
    delivered_update = StatusUpdate(
        meta_message_id="wamid.test1",
        recipient_id="919876543210",
        status="delivered",
    )
    service.handle_status_update(delivered_update)

    with status_db() as db:
        recip = (
            db.query(WhatsAppRecipientStatus)
            .filter(WhatsAppRecipientStatus.wa_id == "919876543210")
            .first()
        )
        assert recip.consecutive_failures == 0
        assert recip.is_unreachable is False
        assert service.is_recipient_reachable("919876543210") is True

        farmer = db.query(Farmer).filter(Farmer.phone == "9876543210").first()
        assert farmer.is_unreachable is False


def test_webhook_receives_status_update_and_responds_fast(monkeypatch, status_db):
    """Meta status webhook POST must respond 200 fast and dispatch status handling to background."""
    secret = "test-secret"
    monkeypatch.setattr(settings, "WHATSAPP_ENABLED", True)
    monkeypatch.setattr(settings, "WHATSAPP_APP_SECRET", secret)

    service = WhatsAppStatusService(db_factory=status_db)
    app.dependency_overrides[get_status_service] = lambda: service

    with status_db() as db:
        out = OutboundMessage(
            id=uuid.uuid4(),
            wa_id="919876543210",
            meta_message_id="wamid.live999",
            category="utility",
            template="daily_price_digest",
            status="sent",
        )
        db.add(out)
        db.commit()

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "statuses": [
                                {
                                    "id": "wamid.live999",
                                    "status": "delivered",
                                    "timestamp": "1727000000",
                                    "recipient_id": "919876543210",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    raw = json.dumps(payload).encode()
    sig = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()

    client = TestClient(app)
    resp = client.post("/api/whatsapp/webhook", content=raw, headers={"X-Hub-Signature-256": sig})
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    with status_db() as db:
        updated = (
            db.query(OutboundMessage)
            .filter(OutboundMessage.meta_message_id == "wamid.live999")
            .first()
        )
        assert updated.status == "delivered"

    app.dependency_overrides.clear()
