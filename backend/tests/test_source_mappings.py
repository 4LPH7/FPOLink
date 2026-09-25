"""Unit tests for deterministic source-to-canonical mappings and statewide market coverage."""

import uuid

from sqlalchemy import func

from app.models.crop import Crop
from app.models.market import Market
from app.models.source_mapping import (
    VarietySourceMapping,
)
from app.models.variety import Variety
from app.services.crop_resolver import resolve_crop, resolve_variety
from app.services.market_resolver import resolve_market


def test_statewide_market_coverage_all_38_districts(db):
    """Verify that every one of Tamil Nadu's 38 revenue districts has at least one regulated market."""
    distinct_districts = (
        db.query(func.count(func.distinct(Market.district_id)))
        .filter(Market.is_active.is_(True))
        .scalar()
    )
    assert distinct_districts == 38, (
        f"Expected 38 districts with active markets, found {distinct_districts}"
    )


def test_crop_source_mapping_resolution(db):
    """Verify Stage 0 deterministic external ID and external name resolution for crops."""
    # Test OGD code lookup
    crop = resolve_crop("Arbitrary Text", db, source_code="ogd", external_code="TURMERIC")
    assert crop is not None
    assert crop.name.lower() == "turmeric"

    # Test Agmarknet name lookup
    crop_agm = resolve_crop("Shallot (Small Onion)", db, source_code="agmarknet")
    assert crop_agm is not None
    assert crop_agm.name.lower() == "small onion"

    # Test paddy alias via OGD
    paddy = resolve_crop("Paddy(Dhan)(Common)", db, source_code="ogd")
    assert paddy is not None
    assert paddy.name.lower() == "paddy"


def test_market_source_mapping_resolution(db):
    """Verify Stage 0 deterministic external ID resolution for regulated markets."""
    # Test Madurai mandi via OGD code
    market = resolve_market("Unknown Raw Name", db=db, source_code="ogd", external_code="OGD_MDU")
    assert market is not None
    assert market.district == "Madurai"

    # Test Trichy mandi via Agmarknet code
    trichy = resolve_market(
        "Random String", db=db, source_code="agmarknet", external_code="AGM_TRY"
    )
    assert trichy is not None
    assert trichy.district == "Tiruchirappalli"

    # Test Erode mandi via OGD name
    erode = resolve_market("Erode", db=db, source_code="ogd")
    assert erode is not None
    assert "Erode" in erode.name


def test_variety_source_mapping_resolution(db):
    """Verify deterministic resolution for varieties via VarietySourceMapping."""
    crop = db.query(Crop).filter(Crop.name == "banana").first()
    assert crop is not None

    variety = db.query(Variety).filter(Variety.crop_id == crop.id, Variety.name == "Poovan").first()
    assert variety is not None

    # Insert test variety source mapping
    test_code = f"TEST_BAN_POOVAN_{uuid.uuid4().hex[:6]}"
    vsm = VarietySourceMapping(
        variety_id=variety.id,
        source_code="test_agri",
        external_code=test_code,
        external_name="Poovan Grand Naine",
        confidence=1.0,
    )
    db.add(vsm)
    db.commit()

    resolved = resolve_variety(
        crop.id,
        "Unknown variety label",
        db,
        source_code="test_agri",
        external_code=test_code,
    )
    assert resolved is not None
    assert resolved.id == variety.id


def test_fallback_to_canonical_when_no_source_mapping(db):
    """Verify that resolution falls back to canonical names when external code is not recognized."""
    # Crop fallback
    crop = resolve_crop("turmeric", db, source_code="unknown_src", external_code="NON_EXISTENT")
    assert crop is not None
    assert crop.name.lower() == "turmeric"

    # Market fallback
    market = resolve_market(
        "Erode Regulated Market", db=db, source_code="unknown_src", external_code="NON_EXISTENT"
    )
    assert market is not None
    assert market.district == "Erode"
