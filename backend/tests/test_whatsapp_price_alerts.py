"""Tests for T4.3: Price-move alerts (>= 5% threshold) and max 1 alert per farmer per day."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
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
from app.services.whatsapp_alerts import PriceMoveAlertService


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


class FakeChannel:
    def __init__(self):
        self.sent_alerts = []
        self.next_id = 1

    async def send_template_with_id(self, to: str, name: str, lang: str, params: list[str]):
        wamid = f"wamid.alert.{self.next_id}"
        self.next_id += 1
        self.sent_alerts.append({"to": to, "name": name, "lang": lang, "params": params})
        return True, wamid


@pytest.fixture
def alert_db():
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
async def test_price_move_alert_triggers_at_5_percent_and_respects_daily_limit(alert_db):
    """Price swings >= 5% trigger an alert, swings < 5% do not, and max 1 alert/farmer/day is enforced."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    channel = FakeChannel()

    with alert_db() as db:
        fpo = FPO(
            id=uuid.uuid4(),
            name="Erode FPO",
            registration_number="FPO-01",
            district="Erode",
            village="Perundurai",
            contact_phone="9876543210",
        )
        market = Market(id=uuid.uuid4(), name="Erode Mandi", district="Erode", state="Tamil Nadu")
        turmeric = Crop(id=uuid.uuid4(), name="turmeric", tamil_name="மஞ்சள்", unit="kg")
        banana = Crop(id=uuid.uuid4(), name="banana", tamil_name="வாழை", unit="kg")
        db.add_all([fpo, market, turmeric, banana])
        db.flush()

        # Farmer 1 grows turmeric
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

        # Farmer 2 grows banana
        u2 = User(
            id=uuid.uuid4(),
            name="Velu",
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
            alerts_opt_in=True,
            is_unreachable=False,
        )
        farm2 = Farm(id=uuid.uuid4(), farmer_id=f2.id, crop_id=banana.id, area_acres=2.0)

        db.add_all([u1, f1, farm1, u2, f2, farm2])

        # Turmeric price: 100 yesterday -> 110 today (+10% increase >= 5% threshold)
        t_prev = MarketPrice(
            id=uuid.uuid4(),
            crop_id=turmeric.id,
            market_id=market.id,
            district="Erode",
            price_date=yesterday,
            min_price=Decimal("95"),
            max_price=Decimal("105"),
            modal_price=Decimal("100"),
            source="ceda",
        )
        t_curr = MarketPrice(
            id=uuid.uuid4(),
            crop_id=turmeric.id,
            market_id=market.id,
            district="Erode",
            price_date=today,
            min_price=Decimal("105"),
            max_price=Decimal("115"),
            modal_price=Decimal("110"),
            source="ceda",
        )

        # Banana price: 50 yesterday -> 51 today (+2% increase < 5% threshold -> NO alert)
        b_prev = MarketPrice(
            id=uuid.uuid4(),
            crop_id=banana.id,
            market_id=market.id,
            district="Erode",
            price_date=yesterday,
            min_price=Decimal("48"),
            max_price=Decimal("52"),
            modal_price=Decimal("50"),
            source="ceda",
        )
        b_curr = MarketPrice(
            id=uuid.uuid4(),
            crop_id=banana.id,
            market_id=market.id,
            district="Erode",
            price_date=today,
            min_price=Decimal("49"),
            max_price=Decimal("53"),
            modal_price=Decimal("51"),
            source="ceda",
        )

        db.add_all([t_prev, t_curr, b_prev, b_curr])
        db.commit()

    service = PriceMoveAlertService(db_factory=alert_db, threshold_pct=5.0)

    # First check: Turmeric triggers alert for Farmer 1, Banana does not
    metrics1 = await service.check_and_send_alerts(channel, target_date=today)
    assert metrics1["evaluated_crops"] == 2
    assert metrics1["significant_moves"] == 1  # Only turmeric moved >= 5%
    assert metrics1["alerts_sent"] == 1
    assert len(channel.sent_alerts) == 1

    alert = channel.sent_alerts[0]
    assert alert["to"] == "919876543210"
    assert alert["name"] == "price_move_alert"
    assert alert["lang"] == "ta"
    assert alert["params"] == ["மஞ்சள்", "உயர்வு", "10.0%", "11000", "Erode Mandi"]

    # Limit Check: Running check_and_send_alerts again today must NOT send another alert to Farmer 1
    metrics2 = await service.check_and_send_alerts(channel, target_date=today)
    assert metrics2["alerts_sent"] == 0
    assert metrics2["skipped"] == 1
    assert len(channel.sent_alerts) == 1  # No duplicate alert sent


@pytest.mark.anyio
async def test_price_drop_triggers_downward_alert(alert_db):
    """A price drop >= 5% triggers an alert with direction 'Drop' / 'சரிவு'."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    channel = FakeChannel()

    with alert_db() as db:
        fpo = FPO(
            id=uuid.uuid4(),
            name="Erode FPO",
            registration_number="FPO-02",
            district="Erode",
            village="Perundurai",
            contact_phone="9876543210",
        )
        market = Market(id=uuid.uuid4(), name="Erode Mandi", district="Erode", state="Tamil Nadu")
        onion = Crop(id=uuid.uuid4(), name="onion", tamil_name="வெங்காயம்", unit="kg")
        db.add_all([fpo, market, onion])
        db.flush()

        u = User(
            id=uuid.uuid4(),
            name="Ravi",
            phone="9876543219",
            role=UserRole.FARMER,
            hashed_password="pw",
        )
        f = Farmer(
            id=uuid.uuid4(),
            user_id=u.id,
            fpo_id=fpo.id,
            phone="9876543219",
            village="Perundurai",
            taluk="Perundurai",
            district="Erode",
            farm_area_acres=1.5,
            lang="en",
            alerts_opt_in=True,
            is_unreachable=False,
        )
        farm = Farm(id=uuid.uuid4(), farmer_id=f.id, crop_id=onion.id, area_acres=1.5)
        db.add_all([u, f, farm])

        # Onion drops from 50 yesterday to 45 today (-10%)
        p_prev = MarketPrice(
            id=uuid.uuid4(),
            crop_id=onion.id,
            market_id=market.id,
            district="Erode",
            price_date=yesterday,
            min_price=Decimal("48"),
            max_price=Decimal("52"),
            modal_price=Decimal("50"),
            source="ceda",
        )
        p_curr = MarketPrice(
            id=uuid.uuid4(),
            crop_id=onion.id,
            market_id=market.id,
            district="Erode",
            price_date=today,
            min_price=Decimal("43"),
            max_price=Decimal("47"),
            modal_price=Decimal("45"),
            source="ceda",
        )
        db.add_all([p_prev, p_curr])
        db.commit()

    service = PriceMoveAlertService(db_factory=alert_db, threshold_pct=5.0)
    metrics = await service.check_and_send_alerts(channel, target_date=today)
    assert metrics["alerts_sent"] == 1
    assert len(channel.sent_alerts) == 1

    alert = channel.sent_alerts[0]
    assert alert["to"] == "919876543219"
    assert alert["lang"] == "en"
    assert alert["params"][1] == "Drop"  # English direction label
    assert alert["params"][2] == "10.0%"
