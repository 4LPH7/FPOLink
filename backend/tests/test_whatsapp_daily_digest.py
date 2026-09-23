"""Tests for T4.2: Daily digest worker job, freshness gating, crop matching, and idempotency."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.user import User, UserRole
from app.models.whatsapp import OutboundMessage, WhatsAppRecipientStatus
from app.services.db_bot_services import DbBotServices
from app.services.whatsapp_digest import DailyDigestService
from app.services.whatsapp_status import WhatsAppStatusService
from app.services.whatsapp_usage import WhatsAppUsageService


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


class FakeChannel:
    def __init__(self):
        self.sent_templates = []
        self.next_id_counter = 1

    async def send_template_with_id(self, to: str, name: str, lang: str, params: list[str]):
        wamid = f"wamid.mock.{self.next_id_counter}"
        self.next_id_counter += 1
        self.sent_templates.append({"to": to, "name": name, "lang": lang, "params": params})
        return True, wamid

    async def send_template(self, to: str, name: str, lang: str, params: list[str]):
        ok, _ = await self.send_template_with_id(to, name, lang, params)
        return ok


@pytest.fixture
def digest_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    yield TestingSession
    Base.metadata.drop_all(engine)


@pytest.mark.anyio
async def test_daily_digest_full_flow_with_crop_matching_and_freshness(digest_db):
    """Daily digest matches farmer crops, sends only fresh prices, and logs outbound message."""
    today = date.today()
    channel = FakeChannel()

    with digest_db() as db:
        # Create FPO, Markets, Crops
        fpo = FPO(
            id=uuid.uuid4(),
            name="Erode Turmeric FPO",
            registration_number="FPO-01",
            district="Erode",
            village="Perundurai",
            contact_phone="9876543210",
        )
        market = Market(
            id=uuid.uuid4(),
            name="Erode Mandi",
            district="Erode",
            state="Tamil Nadu",
        )
        turmeric = Crop(id=uuid.uuid4(), name="turmeric", tamil_name="மஞ்சள்", unit="kg")
        banana = Crop(id=uuid.uuid4(), name="banana", tamil_name="வாழை", unit="kg")
        db.add_all([fpo, market, turmeric, banana])
        db.flush()

        # Farmer 1: Opted in, grows turmeric, fresh price today
        u1 = User(
            id=uuid.uuid4(),
            name="Karthik",
            phone="9876543210",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        f1 = Farmer(
            id=uuid.uuid4(),
            user_id=u1.id,
            fpo_id=fpo.id,
            phone="9876543210",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=4.0,
            lang="ta",
            alerts_opt_in=True,
            is_unreachable=False,
        )
        farm1 = Farm(id=uuid.uuid4(), farmer_id=f1.id, crop_id=turmeric.id, area_acres=4.0)

        # Farmer 2: Opted OUT -> should not receive digest
        u2 = User(
            id=uuid.uuid4(),
            name="Ramu",
            phone="9876543211",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        f2 = Farmer(
            id=uuid.uuid4(),
            user_id=u2.id,
            fpo_id=fpo.id,
            phone="9876543211",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=2.0,
            lang="en",
            alerts_opt_in=False,
            is_unreachable=False,
        )

        # Farmer 3: Opted in, but UNREACHABLE -> should be skipped
        u3 = User(
            id=uuid.uuid4(),
            name="Suresh",
            phone="9876543212",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        f3 = Farmer(
            id=uuid.uuid4(),
            user_id=u3.id,
            fpo_id=fpo.id,
            phone="9876543212",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=5.0,
            lang="ta",
            alerts_opt_in=True,
            is_unreachable=True,
        )

        # Farmer 4: Opted in, grows banana, but price is STALE (10 days old)
        u4 = User(
            id=uuid.uuid4(),
            name="Velu",
            phone="9876543213",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        f4 = Farmer(
            id=uuid.uuid4(),
            user_id=u4.id,
            fpo_id=fpo.id,
            phone="9876543213",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=3.0,
            lang="en",
            alerts_opt_in=True,
            is_unreachable=False,
        )
        farm4 = Farm(id=uuid.uuid4(), farmer_id=f4.id, crop_id=banana.id, area_acres=3.0)

        db.add_all([u1, f1, farm1, u2, f2, u3, f3, u4, f4, farm4])

        # Fresh price for turmeric (today)
        mp_fresh = MarketPrice(
            id=uuid.uuid4(),
            crop_id=turmeric.id,
            market_id=market.id,
            district="Erode",
            price_date=today,
            min_price=Decimal("120"),
            max_price=Decimal("140"),
            modal_price=Decimal("130"),
            source="ceda",
        )

        # Stale price for banana (10 days old)
        mp_stale = MarketPrice(
            id=uuid.uuid4(),
            crop_id=banana.id,
            market_id=market.id,
            district="Erode",
            price_date=today - timedelta(days=10),
            min_price=Decimal("20"),
            max_price=Decimal("30"),
            modal_price=Decimal("25"),
            source="ceda",
        )

        db.add_all([mp_fresh, mp_stale])
        db.commit()

    service = DailyDigestService(
        db_factory=digest_db,
        bot_services=DbBotServices(db_factory=digest_db, stale_days_threshold=7),
    )

    # First run of digest
    metrics1 = await service.run_digest(channel, target_date=today)
    assert metrics1["opted_in"] == 2  # f1 and f4 (f3 is unreachable, f2 is opted-out)
    assert metrics1["sent"] == 1  # only f1 sent
    assert metrics1["skipped_stale"] == 1  # f4 skipped because banana price is 10 days old
    assert len(channel.sent_templates) == 1

    tpl = channel.sent_templates[0]
    assert tpl["to"] == "919876543210"
    assert tpl["name"] == "daily_price_digest"
    assert tpl["lang"] == "ta"
    assert tpl["params"] == ["மஞ்சள்", "13000", "Erode Mandi"]

    # Verify OutboundMessage logged in database
    with digest_db() as db:
        out = (
            db.query(OutboundMessage)
            .filter(OutboundMessage.wa_id == "919876543210")
            .first()
        )
        assert out is not None
        assert out.template == "daily_price_digest"
        assert out.category == "utility"
        assert out.status == "sent"

    # Strict Idempotency Check: Rerunning on the same day sends 0 new messages!
    metrics2 = await service.run_digest(channel, target_date=today)
    assert metrics2["sent"] == 0
    assert metrics2["skipped_duplicate"] == 1
    assert len(channel.sent_templates) == 1  # Still 1, nothing added!
