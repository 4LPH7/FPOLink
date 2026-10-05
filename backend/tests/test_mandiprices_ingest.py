"""Tests for MandiPrices Agmarknet data provider and ingestion pipeline."""

from datetime import date
from decimal import Decimal

from app.data_sources.base import PriceRecord
from app.data_sources.mandiprices import MandiPricesProvider
from app.data_sources.registry import DataSourceRegistry
from app.models.crop import Crop
from app.models.market_price import MarketPrice
from app.services.ingestion import IngestionService


def test_mandiprices_provider_in_registry():
    """Verify MandiPricesProvider is registered in fallback chain."""
    registry = DataSourceRegistry()
    provider_names = [p.source_name for p in registry.providers]
    assert "agmarknet" in provider_names


def test_mandiprices_provider_parses_cached_turmeric():
    """Verify MandiPricesProvider parses cached turmeric data correctly."""
    provider = MandiPricesProvider(use_cache_first=True)
    records = provider.fetch_prices(crop="turmeric", district="Erode")

    assert len(records) > 0
    for r in records:
        assert r.crop_name == "turmeric"
        assert "Erode" in r.district
        assert r.modal_price > 0
        assert r.raw_unit == "quintal"
        assert r.min_price <= r.modal_price <= r.max_price or r.min_price <= r.max_price
        assert r.source == "agmarknet"


def test_mandiprices_clean_price():
    """Test price conversion helper."""
    assert MandiPricesProvider._clean_price("₹8,048") == Decimal("8048")
    assert MandiPricesProvider._clean_price("₹13,254.50") == Decimal("13254.50")
    assert MandiPricesProvider._clean_price("₹0") == Decimal("0")
    assert MandiPricesProvider._clean_price("") is None


def test_mandiprices_parse_date():
    """Test date parsing helper."""
    d = MandiPricesProvider._parse_date("25 Sep 2026")
    assert d == date(2026, 9, 25)
    d2 = MandiPricesProvider._parse_date("2026-09-25")
    assert d2 == date(2026, 9, 25)


def test_mandiprices_ingestion_service_integration(db):
    """Test full ingestion flow for a sample PriceRecord through IngestionService."""
    # Ensure crop exists
    crop = db.query(Crop).filter(Crop.name == "banana").first()
    if not crop:
        crop = Crop(name="banana", tamil_name="வாழை", category="fruit", unit="kg")
        db.add(crop)
        db.commit()

    service = IngestionService(db)
    rec = PriceRecord(
        crop_name="banana",
        market_name="Gobichettipalayam Test Market",
        district="Erode",
        state="Tamil Nadu",
        min_price=Decimal("20.00"),
        max_price=Decimal("40.00"),
        modal_price=Decimal("30.00"),
        raw_price=Decimal("3000"),
        raw_unit="quintal",
        price_date=date(2026, 9, 25),
        source="agmarknet",
    )

    stored = service._store_records([rec])
    assert stored == 1

    # Verify persisted record
    persisted = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.price_date == date(2026, 9, 25),
            MarketPrice.source == "agmarknet",
        )
        .first()
    )
    assert persisted is not None
    assert persisted.modal_price == Decimal("30.00")
    assert persisted.quality_score is not None
    assert persisted.quality_score >= 70.0

    # Test idempotent duplicate update
    rec_updated = PriceRecord(
        crop_name="banana",
        market_name="Gobichettipalayam Test Market",
        district="Erode",
        state="Tamil Nadu",
        min_price=Decimal("22.00"),
        max_price=Decimal("42.00"),
        modal_price=Decimal("32.00"),
        raw_price=Decimal("3200"),
        raw_unit="quintal",
        price_date=date(2026, 9, 25),
        source="agmarknet",
    )
    stored_dup = service._store_records([rec_updated])
    assert stored_dup == 0  # Updated existing

    db.refresh(persisted)
    assert persisted.modal_price == Decimal("32.00")
