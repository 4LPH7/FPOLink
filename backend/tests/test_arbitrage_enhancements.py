"""Automated tests for Phase M3: Defensible Arbitrage & Transport Realization.

Verifies:
1. Vehicle profile presets (pickup, lcv, medium_truck) and freight cost scaling.
2. Commodity-specific transit spoilage defaults (Banana 3% vs Turmeric 0%).
3. Itemized cost deductions (handling fee, mandi commission, spoilage buffer).
4. Like-for-like variety matching (exact vs cross_variety_approximate).
5. Observation date disparity tracking and multi-factor uncertainty scoring.
6. REST API endpoint query by crop/market names and parameter overrides.
7. Presence of bilingual defensibility disclaimers.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.crop import Crop
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.variety import Variety
from app.services.arbitrage import (
    find_market_arbitrage,
    get_default_spoilage_risk,
)

client = TestClient(app)


@pytest.fixture
def arbitrage_test_env(db):
    """Sets up state, districts, markets, crops with varieties, and prices."""
    state = db.query(State).filter(State.code == "TN").first()
    if not state:
        state = State(name="Tamil Nadu", code="TN")
        db.add(state)
        db.commit()
        db.refresh(state)

    dist_erode = db.query(District).filter(District.name == "Erode").first()
    if not dist_erode:
        dist_erode = District(name="Erode", state_id=state.id, code="ERD")
        db.add(dist_erode)
        db.commit()
        db.refresh(dist_erode)

    dist_salem = db.query(District).filter(District.name == "Salem").first()
    if not dist_salem:
        dist_salem = District(name="Salem", state_id=state.id, code="SLM")
        db.add(dist_salem)
        db.commit()
        db.refresh(dist_salem)

    # Origin Mandi: Erode
    m_erode = db.query(Market).filter(Market.code == "TN-ERD-ARB").first()
    if not m_erode:
        m_erode = Market(
            name="Erode Main Mandi",
            code="TN-ERD-ARB",
            district="Erode",
            district_id=dist_erode.id,
            state="Tamil Nadu",
            latitude=11.3410,
            longitude=77.7172,
            is_active=True,
            is_regulated=True,
        )
        db.add(m_erode)
        db.commit()
        db.refresh(m_erode)

    # Target Mandi: Salem (~65 km from Erode)
    m_salem = db.query(Market).filter(Market.code == "TN-SLM-ARB").first()
    if not m_salem:
        m_salem = Market(
            name="Salem Market Committee",
            code="TN-SLM-ARB",
            district="Salem",
            district_id=dist_salem.id,
            state="Tamil Nadu",
            latitude=11.6643,
            longitude=78.1460,
            is_active=True,
            is_regulated=True,
        )
        db.add(m_salem)
        db.commit()
        db.refresh(m_salem)

    # Commodity 1: Turmeric (Durable spice)
    c_turmeric = db.query(Crop).filter(Crop.name == "Turmeric Arbitrage").first()
    if not c_turmeric:
        c_turmeric = Crop(
            name="Turmeric Arbitrage",
            canonical_name="turmeric_arbitrage",
            tamil_name="மஞ்சள்",
            category="spices",
            perishability="low",
            is_active=True,
        )
        db.add(c_turmeric)
        db.commit()
        db.refresh(c_turmeric)

    # Variety for Turmeric
    v_erode_local = db.query(Variety).filter(Variety.name == "Erode Local").first()
    if not v_erode_local:
        v_erode_local = Variety(crop_id=c_turmeric.id, name="Erode Local", grade="FAQ")
        db.add(v_erode_local)
        db.commit()
        db.refresh(v_erode_local)

    # Commodity 2: Banana (Perishable horticulture)
    c_banana = db.query(Crop).filter(Crop.name == "Banana Arbitrage").first()
    if not c_banana:
        c_banana = Crop(
            name="Banana Arbitrage",
            canonical_name="banana_arbitrage",
            tamil_name="வாழை",
            category="horticulture",
            perishability="high",
            is_horticulture=True,
            is_active=True,
        )
        db.add(c_banana)
        db.commit()
        db.refresh(c_banana)

    today = date.today()

    # Seed Turmeric Prices: Erode ₹8,000 vs Salem ₹9,200
    db.add(
        MarketPrice(
            crop_id=c_turmeric.id,
            variety_id=v_erode_local.id,
            market_id=m_erode.id,
            district="Erode",
            modal_price=Decimal("8000.00"),
            min_price=Decimal("7800.00"),
            max_price=Decimal("8200.00"),
            price_date=today,
            source="agmarknet",
            quality_score=Decimal("95.0"),
        )
    )
    db.add(
        MarketPrice(
            crop_id=c_turmeric.id,
            variety_id=v_erode_local.id,
            market_id=m_salem.id,
            district="Salem",
            modal_price=Decimal("9200.00"),
            min_price=Decimal("9000.00"),
            max_price=Decimal("9400.00"),
            price_date=today - timedelta(days=1),
            source="agmarknet",
            arrival_quantity=Decimal("12.5"),
            quality_score=Decimal("92.0"),
        )
    )

    # Seed Banana Prices: Erode ₹2,500 vs Salem ₹3,200 (Observed 3 days ago at Salem)
    db.add(
        MarketPrice(
            crop_id=c_banana.id,
            market_id=m_erode.id,
            district="Erode",
            modal_price=Decimal("2500.00"),
            min_price=Decimal("2400.00"),
            max_price=Decimal("2600.00"),
            price_date=today,
            source="agmarknet",
            quality_score=Decimal("90.0"),
        )
    )
    db.add(
        MarketPrice(
            crop_id=c_banana.id,
            market_id=m_salem.id,
            district="Salem",
            modal_price=Decimal("3200.00"),
            min_price=Decimal("3100.00"),
            max_price=Decimal("3300.00"),
            price_date=today - timedelta(days=3),
            source="agmarknet",
            arrival_quantity=Decimal("3.0"),  # thin liquidity
            quality_score=Decimal("88.0"),
        )
    )
    db.commit()

    return {
        "m_erode": m_erode,
        "m_salem": m_salem,
        "c_turmeric": c_turmeric,
        "c_banana": c_banana,
        "v_erode_local": v_erode_local,
    }


def test_vehicle_profile_freight_scaling(db, arbitrage_test_env):
    """Test freight calculations across vehicle profiles (pickup, lcv, medium_truck)."""
    m_erode = arbitrage_test_env["m_erode"]
    c_turmeric = arbitrage_test_env["c_turmeric"]

    # 1. Pickup (1.5T payload): Base ₹35, Rate ₹2.00/km/qtl
    arb_pickup = find_market_arbitrage(
        db,
        crop_id=c_turmeric.id,
        origin_market_id=m_erode.id,
        vehicle_profile="pickup",
    )
    opp_pickup = arb_pickup["opportunities"][0]
    dist = opp_pickup["distance_km"]
    expected_freight_pickup = round(35.0 + (dist * 2.00), 2)
    assert opp_pickup["costs_breakdown"]["freight"] == expected_freight_pickup

    # 2. Medium Truck (10T payload): Base ₹25, Rate ₹0.85/km/qtl
    arb_heavy = find_market_arbitrage(
        db,
        crop_id=c_turmeric.id,
        origin_market_id=m_erode.id,
        vehicle_profile="medium_truck",
    )
    opp_heavy = arb_heavy["opportunities"][0]
    expected_freight_heavy = round(25.0 + (dist * 0.85), 2)
    assert opp_heavy["costs_breakdown"]["freight"] == expected_freight_heavy
    # Heavy freight rate per quintal should be significantly cheaper than pickup
    assert opp_heavy["costs_breakdown"]["freight"] < opp_pickup["costs_breakdown"]["freight"]


def test_perishability_spoilage_defaults(db, arbitrage_test_env):
    """Verify that perishable banana receives 3% buffer, while turmeric receives 0%."""
    c_turmeric = arbitrage_test_env["c_turmeric"]
    c_banana = arbitrage_test_env["c_banana"]
    m_erode = arbitrage_test_env["m_erode"]

    assert get_default_spoilage_risk(c_turmeric) == 0.0
    assert get_default_spoilage_risk(c_banana) == 3.0

    # Turmeric arbitrage: spoilage cost should be 0
    arb_turmeric = find_market_arbitrage(db, crop_id=c_turmeric.id, origin_market_id=m_erode.id)
    opp_turmeric = arb_turmeric["opportunities"][0]
    assert opp_turmeric["costs_breakdown"]["spoilage_risk"] == 0.0

    # Banana arbitrage: spoilage buffer is 3% of origin price (3% of ₹2,500 = ₹75.0)
    arb_banana = find_market_arbitrage(db, crop_id=c_banana.id, origin_market_id=m_erode.id)
    opp_banana = arb_banana["opportunities"][0]
    assert opp_banana["costs_breakdown"]["spoilage_risk"] == 75.0


def test_variety_matching_and_date_disparity(db, arbitrage_test_env):
    """Verify variety match tagging and observation date disparity penalties."""
    m_erode = arbitrage_test_env["m_erode"]
    c_turmeric = arbitrage_test_env["c_turmeric"]
    c_banana = arbitrage_test_env["c_banana"]

    # Turmeric has exact matching variety at both mandis
    arb_turmeric = find_market_arbitrage(db, crop_id=c_turmeric.id, origin_market_id=m_erode.id)
    opp_turmeric = arb_turmeric["opportunities"][0]
    assert opp_turmeric["variety_match"] == "exact"
    assert opp_turmeric["date_difference_days"] == 1
    assert opp_turmeric["uncertainty_rating"] == "low"

    # Banana has 3-day observation lag and thin arrival volume (3 tonnes)
    arb_banana = find_market_arbitrage(db, crop_id=c_banana.id, origin_market_id=m_erode.id)
    opp_banana = arb_banana["opportunities"][0]
    assert opp_banana["date_difference_days"] == 3
    # Uncertainty rating should escalate due to date lag, thin liquidity, and spoilage risk
    assert opp_banana["uncertainty_rating"] in ("moderate", "high")
    assert any("lag" in r.lower() for r in opp_banana["uncertainty_reasons"])
    assert any("liquidity" in r.lower() for r in opp_banana["uncertainty_reasons"])


def test_arbitrage_api_endpoints_with_name_resolution_and_disclaimers(arbitrage_test_env):
    """Test /api/v1/intelligence/arbitrage with crop/market names, overrides, and disclaimers."""
    c_turmeric = arbitrage_test_env["c_turmeric"]
    m_erode = arbitrage_test_env["m_erode"]

    resp = client.get(
        "/api/v1/intelligence/arbitrage",
        params={
            "crop": c_turmeric.name,
            "market": m_erode.name,
            "vehicle_profile": "medium_truck",
            "handling_cost": 15.0,
            "commission_pct": 1.5,
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["crop_name"] == c_turmeric.name
    assert data["origin_market_name"] == m_erode.name
    assert data["vehicle_profile"] == "medium_truck"
    assert "disclaimer_ta" in data
    assert "disclaimer_en" in data
    assert "சாத்தியக்கூறு" in data["disclaimer_ta"]
    assert "Estimated net opportunities" in data["disclaimer_en"]

    opp = data["opportunities"][0]
    assert opp["costs_breakdown"]["handling"] == 15.0
    # Commission on ₹9,200 @ 1.5% = ₹138.0
    assert opp["costs_breakdown"]["commission"] == 138.0
    assert opp["uncertainty_rating"] is not None
