"""Automated verification test asserting exact statewide reference counts."""

from app.models.crop import Crop
from app.models.data_quality import DataSource
from app.models.geography import District, Taluk
from app.models.market import Market
from scripts.seed_statewide_foundation import (
    DATA_SOURCES,
    PILOT_MARKETS,
    TALUKS_BY_DISTRICT,
    TIER_A_CROPS,
    TN_DISTRICTS,
)


def test_seed_constant_counts():
    """Verify that all seed specification arrays contain the exact claimed entity counts."""
    assert len(TN_DISTRICTS) == 38, f"Expected 38 districts, got {len(TN_DISTRICTS)}"
    assert len(TIER_A_CROPS) == 20, f"Expected 20 Tier-A crops, got {len(TIER_A_CROPS)}"
    total_taluks = sum(len(t) for t in TALUKS_BY_DISTRICT.values())
    assert total_taluks == 25, f"Expected 25 taluks across pilot hubs, got {total_taluks}"
    assert len(PILOT_MARKETS) == 8, f"Expected 8 pilot regulated markets, got {len(PILOT_MARKETS)}"
    assert len(DATA_SOURCES) == 5, f"Expected 5 ingestion data sources, got {len(DATA_SOURCES)}"


def test_seed_database_counts(db):
    """Verify that the database contains all 38 districts, 20 crops, 25 taluks, and 8 markets."""
    district_count = db.query(District).count()
    assert district_count == 38, f"Expected 38 districts in DB, found {district_count}"

    active_crops = db.query(Crop).filter(Crop.is_active.is_(True)).all()
    assert len(active_crops) >= 20, f"Expected >= 20 active crops in DB, found {len(active_crops)}"

    # Verify each of the 20 Tier-A crops is present
    crop_names = {c.name.lower() for c in active_crops}
    expected_crops = [
        "turmeric",
        "banana",
        "coconut",
        "paddy",
        "groundnut",
        "tomato",
        "small onion",
        "onion",
        "green chilli",
        "red chilli",
        "maize",
        "cotton",
        "sugarcane",
        "black gram",
        "green gram",
        "tapioca",
        "mango",
        "brinjal",
        "ladies finger",
        "ginger",
    ]
    assert len(expected_crops) == 20
    for name in expected_crops:
        assert name in crop_names, f"Expected crop '{name}' not found in active crops"

    taluk_count = db.query(Taluk).count()
    assert taluk_count >= 25, f"Expected >= 25 taluks in DB, found {taluk_count}"

    market_count = db.query(Market).count()
    assert market_count >= 8, f"Expected >= 8 markets in DB, found {market_count}"

    source_count = db.query(DataSource).count()
    assert source_count >= 5, f"Expected >= 5 data sources in DB, found {source_count}"
