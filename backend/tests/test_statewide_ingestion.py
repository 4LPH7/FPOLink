"""Tests for statewide ingestion, canonical resolution, quality scoring, and v1 prices API."""

from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from app.data_sources.base import PriceRecord
from app.main import app
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.data_quality import DataQualityEvent
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.market_price import MarketPrice
from app.services.ingestion import IngestionService

client = TestClient(app)


def test_statewide_ingestion_canonical_resolution_and_quality(db):
    """Test ingestion resolves aliases, computes quality scores, and records telemetry."""
    # 1. Setup State, District
    state = db.query(State).filter(State.code == "TN").first()
    if not state:
        state = State(name="Tamil Nadu", code="TN")
        db.add(state)
        db.commit()
        db.refresh(state)

    district = db.query(District).filter(District.name == "Coimbatore").first()
    if not district:
        district = District(name="Coimbatore", state_id=state.id, code="CBE")
        db.add(district)
        db.commit()
        db.refresh(district)

    # 2. Setup Canonical Crop and Alias
    crop = db.query(Crop).filter(Crop.name == "tomato").first()
    if not crop:
        crop = Crop(
            name="tomato",
            canonical_name="tomato",
            tamil_name="தக்காளி",
            unit="kg",
            category="vegetable",
            is_active=True,
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    alias = db.query(CropAlias).filter(CropAlias.alias == "tamatar").first()
    if not alias:
        alias = CropAlias(crop_id=crop.id, alias="tamatar", source="agmarknet")
        db.add(alias)
        db.commit()

    # 3. Setup Canonical Market and Alias
    from app.services.market_resolver import resolve_market

    market = resolve_market("cbe mandi", db=db)
    if not market:
        market = Market(
            name="Coimbatore Regulated Market",
            code="TN-CBE-01",
            district="Coimbatore",
            district_id=district.id,
            state="Tamil Nadu",
            is_active=True,
        )
        db.add(market)
        db.commit()
        db.refresh(market)

        m_alias = db.query(MarketAlias).filter(MarketAlias.alias == "cbe mandi").first()
        if not m_alias:
            m_alias = MarketAlias(market_id=market.id, alias="cbe mandi", source="ceda")
            db.add(m_alias)
            db.commit()

    # 4. Ingest record using ALIASES ("tamatar" and "cbe mandi")
    service = IngestionService(db)
    today = date.today()
    record = PriceRecord(
        crop_name="tamatar",  # should resolve to "tomato"
        market_name="cbe mandi",  # should resolve to canonical market
        district="Coimbatore",
        state="Tamil Nadu",
        min_price=Decimal("25.00"),
        max_price=Decimal("35.00"),
        modal_price=Decimal("30.00"),
        raw_price=Decimal("3000.00"),
        raw_unit="quintal",
        arrival_quantity=50.0,
        price_date=today,
        source="ogd",
        raw_payload={"item": "tamatar"},
    )

    stored = service._store_records([record])
    assert stored == 1

    # 5. Verify MarketPrice stored with canonical foreign keys & quality score
    mp = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.market_id == market.id,
            MarketPrice.price_date == today,
            MarketPrice.source == "ogd",
        )
        .first()
    )
    assert mp is not None
    assert mp.quality_score is not None
    assert mp.quality_score >= 85.0  # Fresh, reliable source, full prices & arrival
    assert mp.quality_breakdown is not None
    assert mp.quality_breakdown["rating"] == "verified"

    # 6. Ingest record with logical contradiction (min > max) -> triggers low quality penalty and event
    contradictory_record = PriceRecord(
        crop_name="tomato",
        market_name=market.name,
        district="Coimbatore",
        state="Tamil Nadu",
        min_price=Decimal("50.00"),
        max_price=Decimal("20.00"),  # min > max contradiction
        modal_price=Decimal("30.00"),
        raw_price=Decimal("3000.00"),
        raw_unit="quintal",
        arrival_quantity=10.0,
        price_date=today - timedelta(days=20),  # also stale
        source="unknown_feed",
        raw_payload={"error": "corrupt data"},
    )

    stored_bad = service._store_records([contradictory_record])
    assert stored_bad == 1

    bad_mp = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.market_id == market.id,
            MarketPrice.price_date == today - timedelta(days=20),
            MarketPrice.source == "unknown_feed",
        )
        .first()
    )
    assert bad_mp is not None
    assert bad_mp.quality_score < 50.0

    # Verify DataQualityEvent was recorded
    dq_event = (
        db.query(DataQualityEvent).filter(DataQualityEvent.record_id == str(bad_mp.id)).first()
    )
    assert dq_event is not None
    assert dq_event.issue_type == "price_contradiction"


def test_v1_prices_api(db):
    """Test v1 prices endpoints: latest, history, and quality-summary."""
    # Ensure crop and market exist
    crop = db.query(Crop).filter(Crop.name == "tomato").first()
    if not crop:
        crop = Crop(
            name="tomato", canonical_name="tomato", tamil_name="தக்காளி", unit="kg", is_active=True
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    market = db.query(Market).filter(Market.name == "Coimbatore Market").first()
    if not market:
        market = Market(
            name="Coimbatore Market", district="Coimbatore", state="Tamil Nadu", is_active=True
        )
        db.add(market)
        db.commit()
        db.refresh(market)

    # Insert verified price record
    today = date.today()
    mp = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Coimbatore",
        min_price=Decimal("25.00"),
        max_price=Decimal("35.00"),
        modal_price=Decimal("30.00"),
        raw_price=Decimal("3000.00"),
        raw_unit="quintal",
        arrival_quantity=50.0,
        price_date=today,
        source="ogd",
        quality_score=95.0,
        quality_breakdown={"freshness": 1.0, "source_reliability": 1.0, "rating": "verified"},
    )
    db.add(mp)
    db.commit()

    # Query latest prices for Coimbatore
    res = client.get("/api/v1/prices/latest?district=Coimbatore")
    assert res.status_code == 200
    data = res.json()
    assert "prices" in data
    assert len(data["prices"]) >= 1

    first = data["prices"][0]
    assert "quality_score" in first
    assert "quality_breakdown" in first
    assert first["crop_name"] == "tomato"

    # Query with min_quality filter
    res_filtered = client.get("/api/v1/prices/latest?district=Coimbatore&min_quality=90")
    assert res_filtered.status_code == 200
    for item in res_filtered.json()["prices"]:
        assert item["quality_score"] >= 90.0

    # Query quality summary
    res_summary = client.get("/api/v1/prices/quality-summary?district=Coimbatore&days=30")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_records"] >= 1
    assert "average_quality_score" in summary
    assert "verified_count" in summary
    assert "by_source" in summary

    # Query price history
    res_hist = client.get(f"/api/v1/prices/history?crop_id={crop.id}&market_id={market.id}&days=30")
    assert res_hist.status_code == 200
    hist = res_hist.json()
    assert "history" in hist
    assert hist["period_days"] == 30
