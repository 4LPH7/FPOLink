"""Tests for Data Health endpoint, CSV upload, query filters, and variety resolution."""

import io
from datetime import date
from decimal import Decimal

import pytest

from app.models.crop import Crop
from app.models.data_quality import DataQualityEvent
from app.models.market import Market
from app.models.market_price import MarketPrice


@pytest.fixture
def sample_crop_and_market(db):
    crop = db.query(Crop).filter(Crop.name == "turmeric").first()
    if not crop:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", category="spices", default_unit="kg")
        db.add(crop)
        db.flush()

    market = db.query(Market).filter(Market.name == "Erode").first()
    if not market:
        market = Market(name="Erode", district="Erode", is_active=True)
        db.add(market)
        db.flush()

    db.commit()
    return crop, market


def test_data_health_unauthenticated(client):
    res = client.get("/api/admin/data-health")
    assert res.status_code in (401, 403)


def test_data_health_authenticated(client, admin_headers, sample_crop_and_market, db):
    crop, market = sample_crop_and_market
    today = date.today()

    # Seed 2 test prices and 1 data quality event
    mp = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Erode",
        min_price=Decimal("140"),
        max_price=Decimal("160"),
        modal_price=Decimal("150"),
        price_date=today,
        source="ceda",
        raw_unit="kg",
        quality_score=95.0,
    )
    db.add(mp)

    dq = DataQualityEvent(
        record_type="market_price",
        record_id=str(mp.id),
        issue_type="price_spike",
        penalty=10.0,
        details={"info": "test anomaly"},
    )
    db.add(dq)
    db.commit()

    res = client.get("/api/admin/data-health?days=7&district=Erode", headers=admin_headers)
    assert res.status_code == 200

    data = res.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded", "critical")
    assert "summary" in data
    assert data["summary"]["total_observations"] >= 1
    assert "rows_per_market_per_day" in data
    assert len(data["rows_per_market_per_day"]) >= 1
    assert "gap_list" in data
    assert "outliers" in data
    assert "coverage_by_source" in data
    assert "ceda" in data["coverage_by_source"]


def test_prices_latest_crop_and_market_filters(client, sample_crop_and_market, db):
    crop, market = sample_crop_and_market
    today = date.today()

    # Seed an active price
    mp = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Erode",
        min_price=Decimal("140"),
        max_price=Decimal("160"),
        modal_price=Decimal("150"),
        price_date=today,
        source="agmarknet",
        raw_unit="quintal",
        quality_score=98.0,
    )
    db.add(mp)
    db.commit()

    # Test /api/prices/latest with filters
    res = client.get("/api/prices/latest?crop=turmeric&market=erode")
    assert res.status_code == 200
    prices = res.json()["prices"]
    assert len(prices) >= 1
    p = prices[0]
    assert p["crop_name"].lower() == "turmeric"
    assert p["market_name"].lower() == "erode"
    assert "last_updated" in p
    assert "unit" in p


def test_prices_upload_csv_bulk(client, sample_crop_and_market):
    csv_content = """crop,market,district,min_price,max_price,modal_price,price_date,unit
turmeric,Erode,Erode,14000,16000,15000,2026-04-05,quintal
banana,Erode,Erode,2000,2500,2200,2026-04-05,quintal
"""
    files = {"file": ("prices.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post("/api/prices/upload-csv", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["records_parsed"] == 2
    assert data["records_stored"] >= 1


def test_ingestion_guarantees_default_variety(db, sample_crop_and_market):
    from app.data_sources.base import PriceRecord
    from app.services.ingestion import IngestionService

    crop, market = sample_crop_and_market
    service = IngestionService(db)

    # Ingest record without a variety_name
    record = PriceRecord(
        crop_name=crop.name,
        market_name=market.name,
        district="Erode",
        state="Tamil Nadu",
        min_price=Decimal("100"),
        max_price=Decimal("120"),
        modal_price=Decimal("110"),
        price_date=date(2026, 4, 10),
        source="manual",
        variety_name=None,  # No variety specified
    )

    stored = service._store_records([record])
    assert stored == 1

    # Check that market price has a variety assigned
    mp = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.market_id == market.id,
            MarketPrice.price_date == date(2026, 4, 10),
        )
        .first()
    )
    assert mp is not None
    assert mp.variety_id is not None
