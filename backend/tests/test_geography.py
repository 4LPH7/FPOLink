"""Tests for geography models and API v1 geography endpoints."""

import uuid
import pytest
from app.models.geography import Block, District, State, Taluk, Village
from app.models.fpo import FPO
from app.models.market import Market


def test_geography_model_hierarchy(db):
    """Test State -> District -> Taluk -> Block -> Village relationship integrity."""
    state = State(name=f"State-{uuid.uuid4().hex[:6]}", code=f"S{uuid.uuid4().hex[:3].upper()}")
    db.add(state)
    db.commit()
    db.refresh(state)

    district = District(state_id=state.id, name="Erode", code=f"ERD-{uuid.uuid4().hex[:4]}", latitude=11.3410, longitude=77.7172)
    db.add(district)
    db.commit()
    db.refresh(district)

    taluk = Taluk(district_id=district.id, name="Perundurai")
    db.add(taluk)
    db.commit()
    db.refresh(taluk)

    block = Block(taluk_id=taluk.id, name="Perundurai Block")
    db.add(block)
    db.commit()
    db.refresh(block)

    village = Village(taluk_id=taluk.id, block_id=block.id, name="Kunnathur")
    db.add(village)
    db.commit()
    db.refresh(village)

    # Verify relationships
    assert district.state.id == state.id
    assert taluk.district.id == district.id
    assert block.taluk.id == taluk.id
    assert village.taluk.id == taluk.id
    assert village.block.id == block.id
    assert len(state.districts) >= 1
    assert len(district.taluks) >= 1


def test_fpo_market_geography_foreign_keys(db):
    """Verify FPO and Market models accept state_id, district_id, taluk_id foreign keys."""
    state = State(name=f"State-FK-{uuid.uuid4().hex[:6]}", code=f"K{uuid.uuid4().hex[:3].upper()}")
    db.add(state)
    db.commit()

    district = District(state_id=state.id, name="Erode", code=f"ERD-FK-{uuid.uuid4().hex[:4]}")
    db.add(district)
    db.commit()

    taluk = Taluk(district_id=district.id, name="Gobichettipalayam")
    db.add(taluk)
    db.commit()

    # Create FPO with geography links
    fpo = FPO(
        name="Test Geographic FPO",
        registration_number=f"REG-{uuid.uuid4().hex[:8]}",
        district="Erode",
        village="Gobi",
        contact_phone="9988776655",
        state_id=state.id,
        district_id=district.id,
        taluk_id=taluk.id,
    )
    db.add(fpo)
    db.commit()
    db.refresh(fpo)

    assert fpo.state_id == state.id
    assert fpo.district_id == district.id
    assert fpo.taluk_id == taluk.id

    # Create Market with geography links and code
    market = Market(
        name="Gobi Regulated Market",
        code=f"MKT-GOBI-{uuid.uuid4().hex[:4]}",
        district="Erode",
        market_type="regulated_market",
        is_active=True,
        state_id=state.id,
        district_id=district.id,
        taluk_id=taluk.id,
    )
    db.add(market)
    db.commit()
    db.refresh(market)

    assert market.code.startswith("MKT-GOBI")
    assert market.district_id == district.id
    assert market.is_active is True


def test_api_v1_geography_endpoints(client, db):
    """Test public GET /api/v1/geography/ endpoints."""
    # Setup test data
    state = State(name=f"Tamil Nadu Test {uuid.uuid4().hex[:4]}", code=f"T{uuid.uuid4().hex[:3].upper()}")
    db.add(state)
    db.commit()

    district = District(state_id=state.id, name="Test District", code=f"TD{uuid.uuid4().hex[:3].upper()}")
    db.add(district)
    db.commit()

    taluk = Taluk(district_id=district.id, name="Test Taluk")
    db.add(taluk)
    db.commit()

    village = Village(taluk_id=taluk.id, name="Test Village")
    db.add(village)
    db.commit()

    # 1. GET states
    r = client.get("/api/v1/geography/states")
    assert r.status_code == 200
    states = r.json()
    assert any(s["code"] == state.code for s in states)

    # 2. GET districts
    r = client.get("/api/v1/geography/districts")
    assert r.status_code == 200
    districts = r.json()
    assert any(d["id"] == str(district.id) for d in districts)

    # 3. GET district taluks
    r = client.get(f"/api/v1/geography/districts/{district.id}/taluks")
    assert r.status_code == 200
    taluks = r.json()
    assert len(taluks) >= 1
    assert taluks[0]["name"] == "Test Taluk"

    # 4. GET taluk villages
    r = client.get(f"/api/v1/geography/taluks/{taluk.id}/villages")
    assert r.status_code == 200
    villages = r.json()
    assert len(villages) >= 1
    assert villages[0]["name"] == "Test Village"
