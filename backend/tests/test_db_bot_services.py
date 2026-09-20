"""Unit and integration tests for DbBotServices."""

import asyncio
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
from app.models.farmer import Farmer as DbFarmer
from app.models.fpo import FPO
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.user import User, UserRole
from app.services.bot import ConvState
from app.services.db_bot_services import DbBotServices


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def test_db_factory():
    """In-memory SQLite database factory for unit tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


@pytest.mark.anyio
async def test_first_time_atomic_dedup(test_db_factory):
    """Verify first_time returns True on first delivery, False on retries, and handles concurrency."""
    services = DbBotServices(db_factory=test_db_factory)

    # First time message ID arrives
    res1 = await services.first_time("msg_unique_1")
    assert res1 is True

    # Duplicate delivery
    res2 = await services.first_time("msg_unique_1")
    assert res2 is False

    # Concurrent deliveries for the same message ID
    results = await asyncio.gather(
        services.first_time("msg_concurrent_2"),
        services.first_time("msg_concurrent_2"),
    )
    # Exactly one must succeed and one must fail
    assert sorted(results) == [False, True]


@pytest.mark.anyio
async def test_find_farmer_by_phone(test_db_factory):
    """Verify farmer lookup by last 10 digits and formatted phone."""
    services = DbBotServices(db_factory=test_db_factory)

    # Seed test FPO, User, and Farmer
    with test_db_factory() as db:
        fpo = FPO(
            name="Erode Turmeric FPO",
            registration_number="FPO-ERD-001",
            district="Erode",
            village="Modakkurichi",
            contact_phone="9876500000",
        )
        db.add(fpo)
        db.flush()

        user = User(
            name="Senthil Kumar",
            phone="9876543210",
            role=UserRole.FARMER,
            hashed_password="mock_password",
            language_preference="ta",
        )
        db.add(user)
        db.flush()

        farmer = DbFarmer(
            user_id=user.id,
            fpo_id=fpo.id,
            phone="9876543210",
            village="Modakkurichi",
            taluk="Modakkurichi",
            district="Erode",
            farm_area_acres=4.5,
            lang="ta",
            alerts_opt_in=True,
        )
        db.add(farmer)
        db.commit()

    # Find with exact 10 digits
    found = await services.find_farmer("9876543210")
    assert found is not None
    assert found.name == "Senthil Kumar"
    assert found.district == "Erode"
    assert found.lang == "ta"
    assert found.alerts_opt_in is True

    # Find with +91 country code
    found_e164 = await services.find_farmer("+91 98765 43210")
    assert found_e164 is not None
    assert found_e164.name == "Senthil Kumar"

    # Unknown number returns None
    assert await services.find_farmer("9999999999") is None


@pytest.mark.anyio
async def test_latest_price_and_staleness(test_db_factory):
    """Verify price lookup by district with fallback, and staleness detection."""
    services = DbBotServices(db_factory=test_db_factory, stale_days_threshold=7)

    with test_db_factory() as db:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg")
        db.add(crop)
        db.flush()

        market_erode = Market(name="Erode Mandi", district="Erode", state="Tamil Nadu")
        market_salem = Market(name="Salem Mandi", district="Salem", state="Tamil Nadu")
        db.add_all([market_erode, market_salem])
        db.flush()

        today = date.today()
        ten_days_ago = today - timedelta(days=10)

        # Older price in Erode, newer price in Salem
        mp_erode = MarketPrice(
            crop_id=crop.id,
            market_id=market_erode.id,
            district="Erode",
            min_price=Decimal("120.00"),
            max_price=Decimal("140.00"),
            modal_price=Decimal("130.00"),
            price_date=ten_days_ago,
            source="ceda",
        )
        mp_salem = MarketPrice(
            crop_id=crop.id,
            market_id=market_salem.id,
            district="Salem",
            min_price=Decimal("125.00"),
            max_price=Decimal("145.00"),
            modal_price=Decimal("135.00"),
            price_date=today,
            source="ceda",
        )
        db.add_all([mp_erode, mp_salem])
        db.commit()

    # Query with district Erode
    price_erode = await services.latest_price("turmeric", district="Erode")
    assert price_erode is not None
    assert price_erode.market == "Erode Mandi"
    assert price_erode.modal_per_kg == Decimal("130.00")
    assert services.is_price_stale(price_erode) is True  # 10 days old > 7 days

    # Query with district Coimbatore (doesn't exist -> falls back to newest in state)
    price_fallback = await services.latest_price("turmeric", district="Coimbatore")
    assert price_fallback is not None
    assert price_fallback.market == "Salem Mandi"
    assert price_fallback.modal_per_kg == Decimal("135.00")
    assert services.is_price_stale(price_fallback) is False  # today is not stale


@pytest.mark.anyio
async def test_conversation_state_ttl(test_db_factory):
    """Verify conversation state persistence and 30-minute TTL expiration."""
    services = DbBotServices(db_factory=test_db_factory, state_ttl_minutes=30)
    wa_id = "919876543210"

    # Set state
    state = ConvState(step="qty", data={"crop": "turmeric"})
    await services.set_state(wa_id, state)

    # Retrieve fresh state
    retrieved = await services.get_state(wa_id)
    assert retrieved is not None
    assert retrieved.step == "qty"
    assert retrieved.data["crop"] == "turmeric"

    # Simulate expired state (> 30 minutes)
    with test_db_factory() as db:
        from app.models.whatsapp import ConversationState

        row = db.query(ConversationState).filter(ConversationState.wa_id == wa_id).first()
        row.updated_at = datetime.now(timezone.utc) - timedelta(minutes=35)
        db.commit()

    # Getting expired state purges it and returns None
    expired = await services.get_state(wa_id)
    assert expired is None

    # Verify row was actually deleted from DB
    with test_db_factory() as db:
        row = db.query(ConversationState).filter(ConversationState.wa_id == wa_id).first()
        assert row is None

    # Set and explicitly clear state
    await services.set_state(wa_id, ConvState(step="grade", data={}))
    assert (await services.get_state(wa_id)) is not None
    await services.set_state(wa_id, None)
    assert (await services.get_state(wa_id)) is None
