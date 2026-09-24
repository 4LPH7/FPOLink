"""Tests for end-to-end price data lineage and provenance tracking."""

from datetime import date
from decimal import Decimal
import uuid

from fastapi.testclient import TestClient

from app.data_sources.base import PriceRecord
from app.main import app
from app.models.crop import Crop
from app.models.data_quality import IngestionRun
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.services.ingestion import IngestionService

client = TestClient(app)


def test_price_data_lineage_chain(db):
    """Verify that every MarketPrice is tied back to its IngestionRun and RawIngest packet."""
    service = IngestionService(db)

    # Create test market and crop
    test_market_name = f"Lineage Mandi {uuid.uuid4().hex[:6]}"
    market = Market(
        name=test_market_name,
        district="Madurai",
        state="Tamil Nadu",
        is_active=True,
    )
    db.add(market)
    db.commit()

    run = IngestionRun(
        source_code="ogd",
        status="running",
        district="Madurai",
        records_fetched=1,
        records_ingested=1,
    )
    db.add(run)
    db.commit()

    raw_payload = {
        "crop_name": "tomato",
        "market_name": test_market_name,
        "district": "Madurai",
        "min_price": "18.00",
        "max_price": "24.00",
        "modal_price": "22.00",
        "price_date": "2026-09-24",
        "source": "ogd",
        "source_record_id": f"REC_{uuid.uuid4().hex[:6]}",
    }
    record = PriceRecord(
        crop_name="tomato",
        market_name=test_market_name,
        district="Madurai",
        min_price=Decimal("18.00"),
        max_price=Decimal("24.00"),
        modal_price=Decimal("22.00"),
        price_date=date(2026, 9, 24),
        source="ogd",
        raw_payload=raw_payload,
    )

    stored = service._store_records([record], ingestion_run_id=run.id)
    assert stored == 1

    crop = db.query(Crop).filter(Crop.name == "tomato").first()
    assert crop is not None

    price = (
        db.query(MarketPrice)
        .filter(MarketPrice.crop_id == crop.id, MarketPrice.market_id == market.id)
        .first()
    )
    assert price is not None
    assert price.ingestion_run_id == run.id
    assert price.raw_ingest_id is not None

    # Test the lineage API endpoint
    response = client.get(f"/api/v1/prices/{price.id}/lineage")
    assert response.status_code == 200
    data = response.json()

    assert data["price_id"] == str(price.id)
    assert data["crop_name"] == "tomato"
    assert data["market_name"] == test_market_name
    assert data["modal_price"] == 22.0
    assert data["source"] == "ogd"

    # Ingestion run provenance
    assert data["ingestion_run"] is not None
    assert data["ingestion_run"]["id"] == str(run.id)
    assert data["ingestion_run"]["source_code"] == "ogd"

    # Raw ingest provenance
    assert data["raw_ingest"] is not None
    assert data["raw_ingest"]["id"] == str(price.raw_ingest_id)
    assert data["raw_ingest"]["checksum"] is not None
    assert data["raw_ingest"]["payload"]["source_record_id"] == raw_payload["source_record_id"]


def test_lineage_non_existent_price():
    """Verify 404 behavior for unknown price ID."""
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/prices/{fake_id}/lineage")
    assert response.status_code == 404
