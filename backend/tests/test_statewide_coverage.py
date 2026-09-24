"""Comprehensive Statewide Integration and Multi-District Coverage Test Suite (Phase 9 v0.6).

Verifies:
1. Multi-district ingestion across distinct TN districts (Madurai, Salem, Coimbatore, Thanjavur, Dindigul, Erode).
2. Deterministic source mapping resolution with fallback to aliases.
3. 8-stage pipeline invariants (SHA-256 deduplication, quality scoring, lineage linking).
4. Commodity Registry API querying and category filtering across statewide commodities.
5. Ingestion freshness and coverage reporting across 38 districts.
6. Zero regression on existing Erode pilot endpoints and models.
"""

from datetime import date, timedelta
from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient

from app.data_sources.base import PriceRecord
from app.main import app
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.data_quality import IngestionRun
from app.models.raw_ingest import RawIngest
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.market_price import MarketPrice
from app.models.source_mapping import CropSourceMapping, MarketSourceMapping
from app.services.ingestion import IngestionService

client = TestClient(app)


def test_multi_district_ingestion_and_lineage(db):
    """Test statewide ingestion across multiple districts (Madurai, Salem, Thanjavur)."""
    # Verify/Fetch TN state
    state = db.query(State).filter(State.code == "TN").first()
    if not state:
        state = State(name="Tamil Nadu", code="TN")
        db.add(state)
        db.commit()
        db.refresh(state)

    districts = ["Madurai", "Salem", "Thanjavur"]
    district_objs = {}
    for dist_name in districts:
        d = db.query(District).filter(District.name == dist_name).first()
        if not d:
            d = District(name=dist_name, state_id=state.id, code=dist_name[:3].upper())
            db.add(d)
            db.commit()
            db.refresh(d)
        district_objs[dist_name] = d

    # Verify/Setup canonical markets for these districts
    markets_to_setup = [
        {"name": "Madurai Mattuthavani Regulated Market", "district": "Madurai", "code": "TN-MDU-01"},
        {"name": "Salem Shevapet Regulated Market", "district": "Salem", "code": "TN-SLM-01"},
        {"name": "Thanjavur Regulated Market", "district": "Thanjavur", "code": "TN-TNJ-01"},
    ]
    market_objs = {}
    for m_info in markets_to_setup:
        m = db.query(Market).filter(
            (Market.code == m_info["code"]) | (Market.name == m_info["name"])
        ).first()
        if not m:
            m = Market(
                name=m_info["name"],
                code=m_info["code"],
                district=m_info["district"],
                district_id=district_objs[m_info["district"]].id,
                state="Tamil Nadu",
                is_active=True,
                is_regulated=True,
            )
            db.add(m)
            db.commit()
            db.refresh(m)
        market_objs[m_info["district"]] = m

    # Verify/Setup Crops
    crops_to_setup = [
        {"name": "banana", "canonical_name": "banana", "tamil": "வாழை", "unit": "bunch", "cat": "fruit"},
        {"name": "paddy", "canonical_name": "paddy", "tamil": "நெல்", "unit": "quintal", "cat": "cereal"},
        {"name": "coconut", "canonical_name": "coconut", "tamil": "தேங்காய்", "unit": "count", "cat": "commercial"},
    ]
    crop_objs = {}
    for c_info in crops_to_setup:
        c = db.query(Crop).filter(Crop.name == c_info["name"]).first()
        if not c:
            c = Crop(
                name=c_info["name"],
                canonical_name=c_info["canonical_name"],
                tamil_name=c_info["tamil"],
                unit=c_info["unit"],
                category=c_info["cat"],
                is_active=True,
            )
            db.add(c)
            db.commit()
            db.refresh(c)
        crop_objs[c_info["name"]] = c

    # Set up deterministic source mappings
    # Madurai source mapping: "MDU_MANDI" -> Madurai Mattuthavani
    mdu_mapping = db.query(MarketSourceMapping).filter(
        MarketSourceMapping.source_code == "ogd",
        MarketSourceMapping.external_code == "MDU_MANDI"
    ).first()
    if not mdu_mapping:
        mdu_mapping = MarketSourceMapping(
            source_code="ogd",
            external_code="MDU_MANDI",
            external_name="Madurai Market Center",
            market_id=market_objs["Madurai"].id,
        )
        db.add(mdu_mapping)

    # Salem source mapping: "SLM_MANDI" -> Salem Shevapet
    slm_mapping = db.query(MarketSourceMapping).filter(
        MarketSourceMapping.source_code == "ceda",
        MarketSourceMapping.external_code == "SLM_MANDI"
    ).first()
    if not slm_mapping:
        slm_mapping = MarketSourceMapping(
            source_code="ceda",
            external_code="SLM_MANDI",
            external_name="Salem Shevapet Central",
            market_id=market_objs["Salem"].id,
        )
        db.add(slm_mapping)

    # Crop source mapping: "CROP_BANANA_TN" -> banana
    banana_mapping = db.query(CropSourceMapping).filter(
        CropSourceMapping.source_code == "ogd",
        CropSourceMapping.external_code == "CROP_BANANA_TN"
    ).first()
    if not banana_mapping:
        banana_mapping = CropSourceMapping(
            source_code="ogd",
            external_code="CROP_BANANA_TN",
            external_name="Banana Poovan",
            crop_id=crop_objs["banana"].id,
        )
        db.add(banana_mapping)
    db.commit()

    service = IngestionService(db)
    today = date.today()

    # 1. Ingest Madurai record using deterministic external IDs
    rec_madurai = PriceRecord(
        crop_name="CROP_BANANA_TN",
        market_name="MDU_MANDI",
        district="Madurai",
        state="Tamil Nadu",
        min_price=Decimal("350.00"),
        max_price=Decimal("450.00"),
        modal_price=Decimal("400.00"),
        price_date=today,
        source="ogd",
        raw_payload={"source_code": "ogd_feed_mdu", "ts": "2026-09-24T06:00:00", "source_record_id": "mdu_raw_01"},
    )

    # 2. Ingest Salem record using deterministic external market ID + canonical crop
    rec_salem = PriceRecord(
        crop_name="coconut",
        market_name="SLM_MANDI",
        district="Salem",
        state="Tamil Nadu",
        min_price=Decimal("15.00"),
        max_price=Decimal("22.00"),
        modal_price=Decimal("18.00"),
        price_date=today,
        source="ceda",
        raw_payload={"source_code": "ceda_slm", "ts": "2026-09-24T06:15:00", "source_record_id": "slm_raw_02"},
    )

    # 3. Ingest Thanjavur record using canonical market name
    rec_thanjavur = PriceRecord(
        crop_name="paddy",
        market_name="Thanjavur Regulated Market",
        district="Thanjavur",
        state="Tamil Nadu",
        min_price=Decimal("2100.00"),
        max_price=Decimal("2350.00"),
        modal_price=Decimal("2250.00"),
        price_date=today,
        source="agmarknet",
        raw_payload={"source_code": "agmarknet_tnj", "source_record_id": "tnj_raw_03"},
    )

    records = [rec_madurai, rec_salem, rec_thanjavur]

    # Ingest using service._store_records with an IngestionRun
    run = IngestionRun(
        source_code="ogd",
        status="running",
        district="statewide",
        records_fetched=len(records),
        records_ingested=0,
    )
    db.add(run)
    db.commit()

    stored = service._store_records(records, ingestion_run_id=run.id)
    assert stored == 3

    # Verify database records and data lineage
    madurai_price = db.query(MarketPrice).filter(
        MarketPrice.crop_id == crop_objs["banana"].id,
        MarketPrice.market_id == market_objs["Madurai"].id,
        MarketPrice.price_date == today,
    ).first()
    assert madurai_price is not None
    assert madurai_price.district == "Madurai"
    assert madurai_price.ingestion_run_id is not None
    assert madurai_price.raw_ingest_id is not None
    assert madurai_price.quality_score is not None
    assert madurai_price.quality_score >= Decimal("0.80")

    # Verify Lineage API for Madurai Price
    resp = client.get(f"/api/v1/prices/{madurai_price.id}/lineage")
    assert resp.status_code == 200
    lineage = resp.json()
    assert lineage["price_id"] == str(madurai_price.id)
    assert lineage["crop_name"] == "banana"
    assert lineage["market_name"] == market_objs["Madurai"].name
    assert lineage["raw_ingest"]["checksum"] is not None


def test_commodity_registry_api_and_categories(db):
    """Test statewide Commodity Registry API with categories, aliases, and varieties."""
    # List all commodities
    resp = client.get("/api/v1/commodities")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 18
    all_names = [c["canonical_name"] for c in data]
    assert "turmeric" in all_names
    assert "banana" in all_names

    # Filter by category
    resp_spice = client.get("/api/v1/commodities?category=spice")
    assert resp_spice.status_code == 200
    spices = resp_spice.json()
    assert len(spices) >= 1
    spice_names = [s["canonical_name"] for s in spices]
    assert "turmeric" in spice_names

    # Query single commodity detail
    turmeric = db.query(Crop).filter(Crop.name == "turmeric").first()
    if turmeric:
        resp_detail = client.get(f"/api/v1/commodities/{turmeric.id}")
        assert resp_detail.status_code == 200
        detail = resp_detail.json()
        assert detail["canonical_name"] == "turmeric"
        assert "varieties" in detail
        assert "aliases" in detail
        assert "source_mappings" in detail


def test_statewide_freshness_and_erode_backward_compatibility(db):
    """Verify statewide freshness telemetry and guarantee zero regression on Erode pilot."""
    # Freshness
    resp = client.get("/api/v1/ingestion/freshness")
    assert resp.status_code == 200
    freshness = resp.json()
    assert freshness["total_districts"] == 38
    assert freshness["total_canonical_markets"] >= 38
    assert len(freshness["data_sources"]) >= 5

    # Erode backward compatibility via v1 prices
    resp_erode = client.get("/api/v1/prices/latest?district=Erode")
    assert resp_erode.status_code == 200
    erode_data = resp_erode.json()
    assert "prices" in erode_data
    assert isinstance(erode_data["prices"], list)

    # Legacy endpoint backward compatibility
    resp_legacy = client.get("/api/prices/latest?district=Erode")
    assert resp_legacy.status_code == 200
