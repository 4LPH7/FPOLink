"""Tests for agricultural crop ontology and alias resolution."""

import uuid
import pytest
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.variety import Variety
from app.models.variety_alias import VarietyAlias
from app.services.crop_resolver import resolve_crop, resolve_variety


def test_crop_ontology_expansion(db):
    """Test Crop model with category, seasonality, perishability, and units."""
    crop = Crop(
        name=f"Paddy-{uuid.uuid4().hex[:6]}",
        canonical_name=f"paddy_{uuid.uuid4().hex[:6]}",
        tamil_name="நெல்",
        scientific_name="Oryza sativa",
        category="Cereals",
        subcategory="Grains",
        default_unit="kg",
        market_unit="quintal",
        season_type="Kuruvai",
        water_requirement="High",
        perishability="Low",
        storage_days=365,
        is_commercial=True,
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)

    assert crop.scientific_name == "Oryza sativa"
    assert crop.season_type == "Kuruvai"
    assert crop.is_commercial is True


def test_crop_alias_resolution(db):
    """Verify raw strings resolve to canonical crops via CropAlias and Tamil names."""
    crop = Crop(
        name=f"turmeric_test_{uuid.uuid4().hex[:6]}",
        canonical_name=f"turmeric_can_{uuid.uuid4().hex[:6]}",
        tamil_name="மஞ்சள் பயிர்",
        category="Commercial",
    )
    db.add(crop)
    db.commit()

    alias1 = CropAlias(crop_id=crop.id, alias="manjal", source="tamil")
    alias2 = CropAlias(crop_id=crop.id, alias="turmeric finger polished", source="agmarknet")
    db.add_all([alias1, alias2])
    db.commit()

    # 1. Exact canonical
    assert resolve_crop(crop.canonical_name, db).id == crop.id

    # 2. Tamil name
    assert resolve_crop("மஞ்சள் பயிர்", db).id == crop.id

    # 3. Aliases
    assert resolve_crop("manjal", db).id == crop.id
    assert resolve_crop("MANJAL", db).id == crop.id
    assert resolve_crop("Turmeric Finger Polished", db).id == crop.id

    # 4. Unknown string
    assert resolve_crop("nonexistent_exotic_spice", db) is None


def test_variety_alias_resolution(db):
    """Verify varietal aliases resolve to canonical varieties under a crop."""
    crop = Crop(name=f"banana_test_{uuid.uuid4().hex[:6]}", category="Horticulture")
    db.add(crop)
    db.commit()

    variety = Variety(crop_id=crop.id, name="Grand Naine", canonical_name="grand_naine", grade="A")
    db.add(variety)
    db.commit()

    valias = VarietyAlias(variety_id=variety.id, alias="G9 Banana", source="local")
    db.add(valias)
    db.commit()

    # 1. Direct name
    assert resolve_variety(crop.id, "Grand Naine", db).id == variety.id
    assert resolve_variety(crop.id, "grand_naine", db).id == variety.id

    # 2. Alias
    assert resolve_variety(crop.id, "G9 Banana", db).id == variety.id
    assert resolve_variety(crop.id, "g9 banana", db).id == variety.id


def test_api_v1_crops_resolve(client, db):
    """Test POST /api/v1/crops/resolve endpoint."""
    crop = Crop(
        name=f"groundnut_test_{uuid.uuid4().hex[:6]}",
        canonical_name=f"groundnut_{uuid.uuid4().hex[:4]}",
        tamil_name="நிலக்கடலை",
        category="Oilseeds",
    )
    db.add(crop)
    db.commit()

    alias = CropAlias(crop_id=crop.id, alias=f"peanuts_{uuid.uuid4().hex[:4]}", source="english")
    db.add(alias)
    db.commit()

    # Call resolve endpoint
    r = client.post("/api/v1/crops/resolve", json={"text": alias.alias})
    assert r.status_code == 200
    data = r.json()
    assert data["matched"] is True
    assert data["crop"]["id"] == str(crop.id)
    assert data["crop"]["tamil_name"] == "நிலக்கடலை"
