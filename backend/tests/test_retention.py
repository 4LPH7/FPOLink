"""Tests for DPDP data retention purge jobs (T5.3)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.whatsapp import ConversationState, OutboundMessage, WhatsAppInbound
from app.services.retention import (
    purge_conversation_state,
    purge_inbound,
    purge_outbound,
)


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def test_db_factory():
    """In-memory SQLite database factory for retention tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


def test_purge_inbound_deletes_old_keeps_recent(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        old_row = WhatsAppInbound(
            message_id="msg_old_8d",
            status="processed",
            received_at=now - timedelta(days=8),
        )
        recent_row = WhatsAppInbound(
            message_id="msg_recent_1d",
            status="processed",
            received_at=now - timedelta(days=1),
        )
        db.add_all([old_row, recent_row])
        db.commit()

    purged = purge_inbound(retention_days=7, db_factory=test_db_factory)
    assert purged == 1

    with test_db_factory() as db:
        remaining = db.query(WhatsAppInbound).all()
        assert len(remaining) == 1
        assert remaining[0].message_id == "msg_recent_1d"


def test_purge_conversation_state_deletes_stale(test_db_factory):
    now = datetime.now(timezone.utc)
    with test_db_factory() as db:
        stale_row = ConversationState(
            wa_id="919876543210",
            step="crop",
            data={"foo": "bar"},
            updated_at=now - timedelta(hours=25),
        )
        active_row = ConversationState(
            wa_id="919876543211",
            step="qty",
            data={"crop": "banana"},
            updated_at=now - timedelta(hours=1),
        )
        db.add_all([stale_row, active_row])
        db.commit()

    purged = purge_conversation_state(ttl_hours=24, db_factory=test_db_factory)
    assert purged == 1

    with test_db_factory() as db:
        remaining = db.query(ConversationState).all()
        assert len(remaining) == 1
        assert remaining[0].wa_id == "919876543211"


def test_purge_outbound_deletes_old_keeps_recent(test_db_factory):
    now = datetime.now(timezone.utc)
    old_id = uuid.uuid4()
    recent_id = uuid.uuid4()
    with test_db_factory() as db:
        old_outbound = OutboundMessage(
            id=old_id,
            wa_id="919876543210",
            category="utility",
            template="daily_price_digest",
            status="delivered",
            created_at=now - timedelta(days=390),
            updated_at=now - timedelta(days=390),
        )
        recent_outbound = OutboundMessage(
            id=recent_id,
            wa_id="919876543210",
            category="utility",
            template="daily_price_digest",
            status="delivered",
            created_at=now - timedelta(days=15),
            updated_at=now - timedelta(days=15),
        )
        db.add_all([old_outbound, recent_outbound])
        db.commit()

    purged = purge_outbound(retention_months=12, db_factory=test_db_factory)
    assert purged == 1

    with test_db_factory() as db:
        remaining = db.query(OutboundMessage).all()
        assert len(remaining) == 1
        assert remaining[0].id == recent_id


def test_purge_empty_tables_no_error(test_db_factory):
    assert purge_inbound(retention_days=7, db_factory=test_db_factory) == 0
    assert purge_conversation_state(ttl_hours=24, db_factory=test_db_factory) == 0
    assert purge_outbound(retention_months=12, db_factory=test_db_factory) == 0


def test_worker_run_data_retention(test_db_factory):
    """Verify app.worker.run_data_retention executes without error."""
    from unittest.mock import patch

    from app.worker import run_data_retention

    with patch("app.services.retention.SessionLocal", test_db_factory):
        run_data_retention()
