"""Tests for raw ingestion persistence, SHA-256 checksum deduplication, and replay fidelity."""

import hashlib
import json
from datetime import date
from decimal import Decimal
import uuid

from app.data_sources.base import PriceRecord
from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.services.ingestion import IngestionService
from scripts.replay_raw_ingestion import replay_raw_records


def test_raw_ingest_persistence_and_checksum(db):
    """Verify that every ingested record generates an immutable RawIngest entry with SHA-256 checksum."""
    service = IngestionService(db)

    # Unique test market and crop
    test_market_name = f"Test Replay Mandi {uuid.uuid4().hex[:6]}"
    market = Market(
        name=test_market_name,
        district="Madurai",
        state="Tamil Nadu",
        is_active=True,
    )
    db.add(market)
    db.commit()

    test_payload = {
        "crop_name": "turmeric",
        "market_name": test_market_name,
        "district": "Madurai",
        "min_price": "7500.00",
        "max_price": "8500.00",
        "modal_price": "8000.00",
        "price_date": "2026-09-24",
        "source": "ogd",
    }
    expected_checksum = hashlib.sha256(
        json.dumps(test_payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()

    record = PriceRecord(
        crop_name="turmeric",
        market_name=test_market_name,
        district="Madurai",
        min_price=Decimal("7500.00"),
        max_price=Decimal("8500.00"),
        modal_price=Decimal("8000.00"),
        price_date=date(2026, 9, 24),
        source="ogd",
        raw_payload=test_payload,
    )

    stored_count = service._store_records([record])
    assert stored_count == 1

    # Verify RawIngest entry exists
    raw_record = (
        db.query(RawIngest)
        .filter(RawIngest.source == "ogd", RawIngest.checksum == expected_checksum)
        .first()
    )
    assert raw_record is not None
    assert raw_record.checksum == expected_checksum
    assert raw_record.processed is True

    # Verify MarketPrice lineage
    price = (
        db.query(MarketPrice)
        .filter(MarketPrice.market_id == market.id, MarketPrice.price_date == date(2026, 9, 24))
        .first()
    )
    assert price is not None
    assert price.raw_ingest_id == raw_record.id


def test_raw_ingest_deduplication(db):
    """Verify that ingesting identical raw payloads deduplicates at the raw layer."""
    service = IngestionService(db)

    test_market_name = f"Dedup Mandi {uuid.uuid4().hex[:6]}"
    market = Market(
        name=test_market_name,
        district="Salem",
        state="Tamil Nadu",
        is_active=True,
    )
    db.add(market)
    db.commit()

    test_payload = {
        "crop_name": "banana",
        "market_name": test_market_name,
        "district": "Salem",
        "min_price": "2500.00",
        "max_price": "3000.00",
        "modal_price": "2800.00",
        "price_date": "2026-09-24",
        "source": "agmarknet",
    }
    record = PriceRecord(
        crop_name="banana",
        market_name=test_market_name,
        district="Salem",
        min_price=Decimal("2500.00"),
        max_price=Decimal("3000.00"),
        modal_price=Decimal("2800.00"),
        price_date=date(2026, 9, 24),
        source="agmarknet",
        raw_payload=test_payload,
    )

    # First ingest
    service._store_records([record])

    initial_raw_count = (
        db.query(RawIngest)
        .filter(RawIngest.source == "agmarknet")
        .count()
    )

    # Second ingest of identical payload
    service._store_records([record])

    final_raw_count = (
        db.query(RawIngest)
        .filter(RawIngest.source == "agmarknet")
        .count()
    )

    assert final_raw_count == initial_raw_count, "Identical raw payload should not create duplicate RawIngest"


def test_replay_harness_reproduces_prices(db):
    """Verify that replay_raw_records accurately normalizes raw records without API calls."""
    test_market_name = f"Replay Harness Mandi {uuid.uuid4().hex[:6]}"
    market = Market(
        name=test_market_name,
        district="Erode",
        state="Tamil Nadu",
        is_active=True,
    )
    db.add(market)
    db.commit()

    unique_code = f"SRC_{uuid.uuid4().hex[:8]}"
    raw_payload = {
        "crop_name": "coconut",
        "market_name": test_market_name,
        "district": "Erode",
        "min_price": "22.00",
        "max_price": "28.00",
        "modal_price": "25.00",
        "price_date": "2026-09-24",
        "source": "test_src",
        "source_record_id": unique_code,
    }
    checksum = hashlib.sha256(
        json.dumps(raw_payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()

    raw_entry = RawIngest(
        source="test_src",
        source_record_id=unique_code,
        checksum=checksum,
        payload=raw_payload,
        processed=False,
    )
    db.add(raw_entry)
    db.commit()

    # Replay
    result = replay_raw_records(db_session=db, source="test_src", unprocessed_only=True)
    assert result["total"] >= 1
    assert result["replayed"] >= 1
    assert result["errors"] == 0

    # Verify that the price was stored
    crop = db.query(Crop).filter(Crop.name == "coconut").first()
    assert crop is not None

    price = (
        db.query(MarketPrice)
        .filter(MarketPrice.crop_id == crop.id, MarketPrice.market_id == market.id)
        .first()
    )
    assert price is not None
    assert price.modal_price == Decimal("25.00")
    assert price.raw_ingest_id == raw_entry.id
