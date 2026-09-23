"""Tests for at-least-once message processing sweep and status lifecycle (T5.4)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.messaging.base import InboundMessage
from app.models.base import Base
from app.models.whatsapp import WhatsAppInbound
from app.services.bot import BotEngine
from app.services.db_bot_services import DbBotServices
from app.services.inbound_sweep import sweep_stuck_inbound


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def test_db_factory():
    """In-memory SQLite database factory for sweep tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


def test_sweep_finds_stuck_received_messages(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        stuck = WhatsAppInbound(
            message_id="msg_stuck_1",
            status="received",
            retry_count=0,
            received_at=now - timedelta(minutes=10),
        )
        db.add(stuck)
        db.commit()

    metrics = sweep_stuck_inbound(db_factory=test_db_factory)
    assert metrics["found"] == 1
    assert metrics["incremented"] == 1
    assert metrics["marked_failed"] == 0

    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_stuck_1").first()
        assert row.retry_count == 1
        assert row.status == "received"


def test_sweep_ignores_recent_received(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        recent = WhatsAppInbound(
            message_id="msg_recent_1",
            status="received",
            retry_count=0,
            received_at=now - timedelta(minutes=1),
        )
        db.add(recent)
        db.commit()

    metrics = sweep_stuck_inbound(db_factory=test_db_factory)
    assert metrics["found"] == 0
    assert metrics["incremented"] == 0


def test_sweep_ignores_processed_messages(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        processed = WhatsAppInbound(
            message_id="msg_processed_1",
            status="processed",
            retry_count=0,
            received_at=now - timedelta(minutes=30),
        )
        db.add(processed)
        db.commit()

    metrics = sweep_stuck_inbound(db_factory=test_db_factory)
    assert metrics["found"] == 0


def test_sweep_marks_failed_after_max_retries(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        almost_dead = WhatsAppInbound(
            message_id="msg_almost_dead",
            status="received",
            retry_count=2,
            received_at=now - timedelta(minutes=15),
        )
        db.add(almost_dead)
        db.commit()

    metrics = sweep_stuck_inbound(db_factory=test_db_factory)
    assert metrics["found"] == 1
    assert metrics["marked_failed"] == 1

    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_almost_dead").first()
        assert row.retry_count == 3
        assert row.status == "failed"


@pytest.mark.anyio
async def test_mark_processed_and_mark_failed(test_db_factory):
    services = DbBotServices(db_factory=test_db_factory)

    # First time records as 'received'
    assert await services.first_time("msg_test_proc") is True

    # Transition to processed
    await services.mark_processed("msg_test_proc")
    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_test_proc").first()
        assert row.status == "processed"

    # Transition another to failed
    assert await services.first_time("msg_test_fail") is True
    await services.mark_failed("msg_test_fail")
    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_test_fail").first()
        assert row.status == "failed"


class DummyChannel:
    async def send_text(self, to, body):
        pass

    async def send_buttons(self, to, body, buttons):
        pass


@pytest.mark.anyio
async def test_bot_engine_marks_processed_on_success(test_db_factory):
    services = DbBotServices(db_factory=test_db_factory)
    engine = BotEngine(services=services)

    msg = InboundMessage(
        message_id="msg_engine_ok",
        wa_id="919999999999",
        kind="text",
        text="hello",
    )
    await engine.handle(msg, DummyChannel())

    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_engine_ok").first()
        assert row is not None
        assert row.status == "processed"


@pytest.mark.anyio
async def test_bot_engine_marks_failed_on_exception(test_db_factory):
    """Verify BotEngine marks status='failed' if an unhandled exception occurs in handler."""
    services = DbBotServices(db_factory=test_db_factory)
    engine = BotEngine(services=services)

    with patch.object(
        services, "find_farmer", side_effect=RuntimeError("Simulated crash mid-processing")
    ):
        msg = InboundMessage(
            message_id="msg_engine_fail",
            wa_id="919999999999",
            kind="text",
            text="hello",
        )
        # Entry point never raises
        await engine.handle(msg, DummyChannel())

    with test_db_factory() as db:
        row = db.query(WhatsAppInbound).filter_by(message_id="msg_engine_fail").first()
        assert row is not None
        assert row.status == "failed"


def test_sweep_emits_sentry_alert_on_exhaustion(test_db_factory):
    """Verify Sentry capture_message is called with level='error' on retry exhaustion."""
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        exhausted = WhatsAppInbound(
            message_id="msg_sentry_alert",
            status="received",
            retry_count=2,
            received_at=now - timedelta(minutes=10),
        )
        db.add(exhausted)
        db.commit()

    mock_sentry = MagicMock()
    with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
        metrics = sweep_stuck_inbound(db_factory=test_db_factory)
        assert metrics["marked_failed"] == 1
        mock_sentry.capture_message.assert_called_once()
        args, kwargs = mock_sentry.capture_message.call_args
        assert "msg_sentry_alert" in args[0]
        assert kwargs["level"] == "error"


def test_worker_run_inbound_sweep(test_db_factory):
    """Verify app.worker.run_inbound_sweep runs without error."""
    from app.worker import run_inbound_sweep

    with patch("app.services.inbound_sweep.SessionLocal", test_db_factory):
        run_inbound_sweep()
