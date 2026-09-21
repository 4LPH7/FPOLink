"""Safety tests for source isolation and synthetic price prevention.

Guarantees:
1. Registry and CEDAProvider never load *_synthetic* CSV files in normal runs.
2. DbBotServices.latest_price and dashboard queries only read whitelisted real sources (ceda, ogd).
3. Seed script demo prices are never served to farmers as latest prices.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.data_sources.ceda import CEDAProvider
from app.data_sources.registry import DataSourceRegistry
from app.models.base import Base
from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.services.db_bot_services import DbBotServices
from app.services.prices import get_latest_prices


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def test_db_factory():
    """In-memory SQLite database factory for unit tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


def test_registry_and_ceda_provider_never_load_synthetic_in_normal_run(tmp_path):
    """Verify that CEDAProvider and DataSourceRegistry ignore synthetic files by default."""
    import csv
    import os

    # 1. Test with tempdir containing a synthetic file and a real file
    synthetic_csv = tmp_path / "ceda_turmeric_synthetic.csv"
    real_csv = tmp_path / "ceda_turmeric_real.csv"

    row_template = {
        "date": "2024-03-15",
        "state_name": "Tamil Nadu",
        "district_name": "Erode",
        "market_name": "Erode",
        "commodity_name": "Turmeric",
        "variety": "Finger",
        "grade": "FAQ",
        "min_price": "14000",
        "max_price": "16000",
        "modal_price": "15000",
    }

    with open(synthetic_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row_template.keys()))
        w.writeheader()
        w.writerow(row_template)

    # Provider with default allow_synthetic=False pointing to dir with only synthetic file
    provider_syn_only = CEDAProvider(data_dir=str(tmp_path))
    assert provider_syn_only.allow_synthetic is False

    records = provider_syn_only.fetch_prices("turmeric", "Erode")
    # Must be 0 because allow_synthetic is False and the file is synthetic
    assert len(records) == 0

    # Explicit allow_synthetic=True will load it
    provider_allowed = CEDAProvider(data_dir=str(tmp_path), allow_synthetic=True)
    records_allowed = provider_allowed.fetch_prices("turmeric", "Erode")
    assert len(records_allowed) == 1
    assert records_allowed[0].source == "ceda_synthetic"

    # Even if caller explicitly passes source_name="ceda", synthetic files must still be tagged as "ceda_synthetic"
    provider_explicit_source = CEDAProvider(
        data_dir=str(tmp_path), source_name="ceda", allow_synthetic=True
    )
    records_explicit = provider_explicit_source.fetch_prices("turmeric", "Erode")
    assert len(records_explicit) == 1
    assert records_explicit[0].source == "ceda_synthetic"

    # Now add a real CSV file
    with open(real_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row_template.keys()))
        w.writeheader()
        w.writerow(row_template)

    # Normal provider should find the real file and load it as ceda
    provider_real = CEDAProvider(data_dir=str(tmp_path), allow_synthetic=False)
    records_real = provider_real.fetch_prices("turmeric", "Erode")
    assert len(records_real) == 1
    assert records_real[0].source == "ceda"

    # 2. Test DataSourceRegistry defaults
    registry = DataSourceRegistry()
    assert registry.allow_synthetic is False
    ceda_prov = registry.get_provider("ceda")
    assert ceda_prov is not None
    assert getattr(ceda_prov, "allow_synthetic", False) is False

    # 3. Test workspace ml/datasets directory if present
    workspace_datasets = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "datasets")
    if os.path.exists(workspace_datasets):
        ws_provider = CEDAProvider(data_dir=workspace_datasets, allow_synthetic=False)
        ws_records = ws_provider.fetch_prices("turmeric", "Erode")
        assert len(ws_records) == 0, "Normal run must not load ml/datasets synthetic files!"


@pytest.mark.anyio
async def test_latest_price_and_dashboard_whitelist_real_sources_only(test_db_factory):
    """Verify that latest_price and dashboard only return prices from whitelisted sources (ceda, ogd)."""
    with test_db_factory() as db:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg", category="spice")
        market = Market(
            name="Erode Mandi",
            district="Erode",
            state="Tamil Nadu",
            market_type="mandi",
        )
        db.add_all([crop, market])
        db.commit()
        db.refresh(crop)
        db.refresh(market)

        today = date.today()

        # Insert synthetic price for today with high modal price
        synthetic_price = MarketPrice(
            crop_id=crop.id,
            market_id=market.id,
            district="Erode",
            min_price=Decimal("190.00"),
            max_price=Decimal("210.00"),
            modal_price=Decimal("200.00"),
            price_date=today,
            source="ceda_synthetic",
        )
        db.add(synthetic_price)
        db.commit()

        # 1. DbBotServices.latest_price must NOT return the synthetic price
        services = DbBotServices(db_factory=test_db_factory)
        price_info = await services.latest_price("turmeric", "Erode")
        assert price_info is None, "Bot must never return synthetic prices"

        # 2. Dashboard get_latest_prices must NOT return synthetic price
        dashboard_prices = get_latest_prices(db, "Erode")
        assert len(dashboard_prices) == 0, "Dashboard must never return synthetic prices"

        # 3. Add a real ceda price from yesterday
        yesterday = today - timedelta(days=1)
        real_price = MarketPrice(
            crop_id=crop.id,
            market_id=market.id,
            district="Erode",
            min_price=Decimal("140.00"),
            max_price=Decimal("160.00"),
            modal_price=Decimal("150.00"),
            price_date=yesterday,
            source="ceda",
        )
        db.add(real_price)
        db.commit()

        # Bot should now return the real price (from yesterday), ignoring the synthetic one from today
        price_info = await services.latest_price("turmeric", "Erode")
        assert price_info is not None
        assert price_info.modal_per_kg == Decimal("150.00")
        assert price_info.price_date == yesterday

        # Dashboard should also return the real price
        dashboard_prices = get_latest_prices(db, "Erode")
        assert len(dashboard_prices) == 1
        assert dashboard_prices[0]["modal_price"] == Decimal("150.00")
        assert dashboard_prices[0]["source"] == "ceda"


@pytest.mark.anyio
async def test_seed_script_prices_never_served_to_bot(test_db_factory):
    """Verify that seed demo prices are never picked up by DbBotServices.latest_price."""
    with test_db_factory() as db:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg", category="spice")
        market = Market(
            name="Erode Mandi",
            district="Erode",
            state="Tamil Nadu",
            market_type="mandi",
        )
        db.add_all([crop, market])
        db.commit()
        db.refresh(crop)
        db.refresh(market)

        today = date.today()

        # Insert prices tagged with seed and seed_demo
        demo_price_1 = MarketPrice(
            crop_id=crop.id,
            market_id=market.id,
            district="Erode",
            min_price=Decimal("140.00"),
            max_price=Decimal("160.00"),
            modal_price=Decimal("150.00"),
            price_date=today,
            source="seed_demo",
        )
        demo_price_2 = MarketPrice(
            crop_id=crop.id,
            market_id=market.id,
            district="Erode",
            min_price=Decimal("140.00"),
            max_price=Decimal("160.00"),
            modal_price=Decimal("150.00"),
            price_date=today - timedelta(days=1),
            source="seed",
        )
        db.add_all([demo_price_1, demo_price_2])
        db.commit()

        services = DbBotServices(db_factory=test_db_factory)
        price_info = await services.latest_price("turmeric", "Erode")

        # Bot must not pick up demo seed prices
        assert price_info is None, "Bot returned demo seed prices to user!"
