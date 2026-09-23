"""Tests for T4.4: WhatsApp usage reporting, cost estimation, caps, and circuit breaker."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.admin_whatsapp import get_usage_service
from app.api.deps import get_current_user
from app.config import settings
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.whatsapp import OutboundMessage, WhatsAppRecipientStatus
from app.services.whatsapp_usage import WhatsAppUsageService


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def usage_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    yield TestingSession
    Base.metadata.drop_all(engine)


def test_whatsapp_usage_service_calculation_and_circuit_breaker(usage_db, monkeypatch):
    """Verify category counts, configurable INR costs, delivery rate, and circuit breaker."""
    monkeypatch.setattr(settings, "WHATSAPP_RATE_SERVICE_INR", 0.00)
    monkeypatch.setattr(settings, "WHATSAPP_RATE_UTILITY_INR", 0.35)
    monkeypatch.setattr(settings, "WHATSAPP_RATE_MARKETING_INR", 0.85)
    monkeypatch.setattr(settings, "WHATSAPP_RATE_AUTH_INR", 0.15)
    monkeypatch.setattr(settings, "WHATSAPP_MONTHLY_SEND_CAP", 10)  # low cap for testing
    monkeypatch.setattr(settings, "WHATSAPP_MONTHLY_BUDGET_INR", 100.0)

    service = WhatsAppUsageService(db_factory=usage_db)
    dt = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)

    with usage_db() as db:
        # Add 4 utility messages (2 delivered, 1 read, 1 failed) -> 4 * 0.35 = 1.40
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543210",
                category="utility",
                status="delivered",
                created_at=dt,
            )
        )
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543211",
                category="utility",
                status="delivered",
                created_at=dt,
            )
        )
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543212",
                category="utility",
                status="read",
                created_at=dt,
            )
        )
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543213",
                category="utility",
                status="failed",
                created_at=dt,
            )
        )

        # Add 2 marketing messages (both delivered) -> 2 * 0.85 = 1.70
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543214",
                category="marketing",
                status="delivered",
                created_at=dt,
            )
        )
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543215",
                category="marketing",
                status="delivered",
                created_at=dt,
            )
        )

        # Add 2 service messages -> 2 * 0.00 = 0.00
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543216",
                category="service",
                status="delivered",
                created_at=dt,
            )
        )
        db.add(
            OutboundMessage(
                id=uuid.uuid4(),
                wa_id="919876543217",
                category="service",
                status="delivered",
                created_at=dt,
            )
        )

        # 1 unreachable recipient in recipient status
        db.add(
            WhatsAppRecipientStatus(
                wa_id="919876543213",
                consecutive_failures=3,
                is_unreachable=True,
            )
        )

        db.commit()

    summary = service.get_usage_summary(month_str="2026-09")
    assert summary.month == "2026-09"
    assert summary.total_messages == 8
    assert summary.by_category == {"utility": 4, "marketing": 2, "service": 2}
    assert summary.by_status == {"delivered": 6, "read": 1, "failed": 1}

    # Expected Cost: (4 * 0.35) + (2 * 0.85) + (2 * 0.00) = 1.40 + 1.70 = 3.10
    assert summary.estimated_cost_inr == 3.10

    # Delivery rate: (6 + 1) / (6 + 1 + 1) = 7/8 = 87.5%
    assert summary.delivery_rate_pct == 87.5
    assert summary.unreachable_recipients == 1
    assert summary.circuit_breaker_tripped is False

    # Now simulate reaching the send cap (cap is 10, total messages = 8 + 3 = 11 >= 10)
    with usage_db() as db:
        for _ in range(3):
            db.add(
                OutboundMessage(
                    id=uuid.uuid4(),
                    wa_id="919876543210",
                    category="service",
                    status="sent",
                    created_at=dt,
                )
            )
        db.commit()

    summary_capped = service.get_usage_summary(month_str="2026-09")
    assert summary_capped.total_messages == 11
    assert summary_capped.circuit_breaker_tripped is True


def test_admin_usage_api_endpoint(usage_db):
    """GET /api/admin/whatsapp/usage enforces admin role and returns usage metrics."""
    service = WhatsAppUsageService(db_factory=usage_db)
    app.dependency_overrides[get_usage_service] = lambda: service

    admin_user = User(
        id=uuid.uuid4(),
        name="Admin User",
        phone="9999999999",
        role=UserRole.ADMIN,
        hashed_password="pw",
    )
    farmer_user = User(
        id=uuid.uuid4(),
        name="Farmer User",
        phone="8888888888",
        role=UserRole.FARMER,
        hashed_password="pw",
    )

    client = TestClient(app)

    # 1. Without auth -> 401
    resp_no_auth = client.get("/api/admin/whatsapp/usage")
    assert resp_no_auth.status_code == 401

    # 2. With farmer role -> 403 Forbidden
    app.dependency_overrides[get_current_user] = lambda: farmer_user
    resp_forbidden = client.get("/api/admin/whatsapp/usage")
    assert resp_forbidden.status_code == 403

    # 3. With admin role -> 200 OK
    app.dependency_overrides[get_current_user] = lambda: admin_user
    resp_ok = client.get("/api/admin/whatsapp/usage?month=2026-09")
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert data["month"] == "2026-09"
    assert "total_messages" in data
    assert "estimated_cost_inr" in data
    assert "circuit_breaker_tripped" in data

    app.dependency_overrides.clear()
