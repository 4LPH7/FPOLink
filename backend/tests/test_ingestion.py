"""Tests for data ingestion, deduplication, and upsert."""

from datetime import date
from decimal import Decimal

from app.data_sources.base import PriceRecord
from app.models.crop import Crop
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.services.ingestion import IngestionService


def test_ingestion_and_deduplication(db):
    # Setup test crop
    crop = db.query(Crop).filter(Crop.name == "turmeric").first()
    if not crop:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg", category="spice")
        db.add(crop)
        db.commit()
        db.refresh(crop)

    service = IngestionService(db)

    record1 = PriceRecord(
        crop_name="turmeric",
        market_name="Erode Test Mandi",
        district="Erode",
        state="Tamil Nadu",
        min_price=Decimal("140.00"),
        max_price=Decimal("160.00"),
        modal_price=Decimal("150.00"),
        raw_price=Decimal("15000.00"),
        raw_unit="quintal",
        arrival_quantity=100.0,
        price_date=date(2026, 9, 15),
        source="test_source",
        raw_payload={"sample": "data_1"},
    )

    # First ingestion run
    stored_first = service._store_records([record1])
    assert stored_first == 1

    # Verify record in database
    prices_after_first = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.price_date == date(2026, 9, 15),
            MarketPrice.source == "test_source",
        )
        .all()
    )
    assert len(prices_after_first) == 1
    assert prices_after_first[0].modal_price == Decimal("150.00")

    # Verify raw_ingest was recorded
    raw_entries = db.query(RawIngest).filter(RawIngest.source == "test_source").all()
    assert len(raw_entries) >= 1

    # SECOND RUN: Same crop, market, date, source, but updated price
    # "Run ingestion twice, get no duplicates"
    record1_updated = PriceRecord(
        crop_name="turmeric",
        market_name="Erode Test Mandi",
        district="Erode",
        state="Tamil Nadu",
        min_price=Decimal("145.00"),
        max_price=Decimal("165.00"),
        modal_price=Decimal("155.00"),  # updated modal price
        raw_price=Decimal("15500.00"),
        raw_unit="quintal",
        arrival_quantity=120.0,
        price_date=date(2026, 9, 15),
        source="test_source",
        raw_payload={"sample": "data_2"},
    )

    stored_second = service._store_records([record1_updated])
    # Should not store a new row, but update existing
    assert stored_second == 0

    prices_after_second = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.price_date == date(2026, 9, 15),
            MarketPrice.source == "test_source",
        )
        .all()
    )
    # Total records MUST still be 1 (NO DUPLICATES)
    assert len(prices_after_second) == 1
    # Modal price MUST be updated to the new value
    assert prices_after_second[0].modal_price == Decimal("155.00")
    assert prices_after_second[0].arrival_quantity == 120.0
