"""Integration and unit tests for Agricultural Intelligence (Phase 11 v0.7).

Verifies:
1. Forecasting service fallback on sparse data (< 30 observations).
2. LightGBM quantile regression training and inference with p10 <= p50 <= p90 bounds.
3. Actionable signal generation (hold, sell, neutral).
4. Geospatial distance and transport net arbitrage math.
5. All REST API v1 endpoints under /api/v1/intelligence/*.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.forecasting import ForecastingService
from app.models.crop import Crop
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.prediction import Prediction
from app.services.arbitrage import find_market_arbitrage, haversine_distance_km

client = TestClient(app)


@pytest.fixture
def intelligence_fixture(db):
    """Setup test state, district, markets, and crop for intelligence tests."""
    state = db.query(State).filter(State.code == "TN").first()
    if not state:
        state = State(name="Tamil Nadu", code="TN")
        db.add(state)
        db.commit()
        db.refresh(state)

    dist_erode = db.query(District).filter(District.name == "Erode").first()
    if not dist_erode:
        dist_erode = District(name="Erode", state_id=state.id, code="ERD")
        db.add(dist_erode)
        db.commit()
        db.refresh(dist_erode)

    dist_cbe = db.query(District).filter(District.name == "Coimbatore").first()
    if not dist_cbe:
        dist_cbe = District(name="Coimbatore", state_id=state.id, code="CBE")
        db.add(dist_cbe)
        db.commit()
        db.refresh(dist_cbe)

    # Market 1: Erode (Origin)
    m_erode = db.query(Market).filter(Market.code == "TN-ERD-TEST").first()
    if not m_erode:
        m_erode = Market(
            name="Erode Test Mandi",
            code="TN-ERD-TEST",
            district="Erode",
            district_id=dist_erode.id,
            state="Tamil Nadu",
            latitude=11.3410,
            longitude=77.7172,
            is_active=True,
            is_regulated=True,
        )
        db.add(m_erode)
        db.commit()
        db.refresh(m_erode)

    # Market 2: Coimbatore (Destination)
    m_cbe = db.query(Market).filter(Market.code == "TN-CBE-TEST").first()
    if not m_cbe:
        m_cbe = Market(
            name="Coimbatore Test Mandi",
            code="TN-CBE-TEST",
            district="Coimbatore",
            district_id=dist_cbe.id,
            state="Tamil Nadu",
            latitude=11.0168,
            longitude=76.9558,
            is_active=True,
            is_regulated=True,
        )
        db.add(m_cbe)
        db.commit()
        db.refresh(m_cbe)

    # Crop: Turmeric
    crop = db.query(Crop).filter(Crop.name == "test_turmeric").first()
    if not crop:
        crop = Crop(
            name="test_turmeric",
            canonical_name="test_turmeric",
            tamil_name="மஞ்சள்",
            unit="quintal",
            category="spice",
            is_active=True,
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    return {
        "crop": crop,
        "m_erode": m_erode,
        "m_cbe": m_cbe,
    }


def test_haversine_distance_and_arbitrage_calculation(db, intelligence_fixture):
    """Verify distance math and transport net spread calculations."""
    m_erode = intelligence_fixture["m_erode"]
    m_cbe = intelligence_fixture["m_cbe"]
    crop = intelligence_fixture["crop"]

    # Calculate distance: Erode to Coimbatore ~ 89 km
    dist = haversine_distance_km(
        float(m_erode.latitude),
        float(m_erode.longitude),
        float(m_cbe.latitude),
        float(m_cbe.longitude),
    )
    assert 80.0 <= dist <= 100.0

    today = date.today()
    # Add origin price: ₹14,000/quintal in Erode
    db.add(
        MarketPrice(
            crop_id=crop.id,
            market_id=m_erode.id,
            district="Erode",
            modal_price=Decimal("14000.00"),
            min_price=Decimal("13500.00"),
            max_price=Decimal("14500.00"),
            price_date=today,
            source="ogd",
            quality_score=Decimal("95.0"),
        )
    )

    # Add destination price: ₹15,500/quintal in Coimbatore
    db.add(
        MarketPrice(
            crop_id=crop.id,
            market_id=m_cbe.id,
            district="Coimbatore",
            modal_price=Decimal("15500.00"),
            min_price=Decimal("15000.00"),
            max_price=Decimal("16000.00"),
            price_date=today,
            source="ogd",
            quality_score=Decimal("92.0"),
        )
    )
    db.commit()

    # Calculate arbitrage
    arb = find_market_arbitrage(db, crop_id=crop.id, origin_market_id=m_erode.id)
    assert arb["origin_price"] == 14000.0
    assert len(arb["opportunities"]) >= 1

    opp = arb["opportunities"][0]
    assert opp["target_market_id"] == str(m_cbe.id)
    assert opp["gross_spread"] == 1500.0  # 15500 - 14000
    # transport_cost = 50 + (dist * 1.20)
    expected_transport = round(50.0 + (dist * 1.20), 2)
    assert opp["transport_cost"] == expected_transport
    assert opp["net_spread"] == round(1500.0 - expected_transport, 2)
    assert opp["recommendation"] == "strong_arbitrage"


def test_forecasting_fallback_baseline_on_sparse_series(db, intelligence_fixture):
    """Verify that sparse series (<30 records) gracefully uses empirical median baseline."""
    crop = intelligence_fixture["crop"]
    m_erode = intelligence_fixture["m_erode"]

    today = date.today()
    # Insert 10 records (sparse series)
    for i in range(10):
        d = today - timedelta(days=10 - i)
        price_val = 10000 + i * 20
        db.add(
            MarketPrice(
                crop_id=crop.id,
                market_id=m_erode.id,
                district="Erode",
                modal_price=Decimal(str(price_val)),
                min_price=Decimal(str(price_val - 50)),
                max_price=Decimal(str(price_val + 50)),
                price_date=d,
                source="ogd",
            )
        )
    db.commit()

    service = ForecastingService(db)
    forecast = service.generate_forecast(crop.id, m_erode.id, horizon_days=7, persist=True)

    assert len(forecast) == 7
    for pt in forecast:
        assert pt["model_type"] == "seasonal_median_baseline"
        assert pt["lower_bound"] <= pt["predicted_price"] <= pt["upper_bound"]
        assert pt["signal"] in ["hold", "sell", "neutral"]
        assert 0.5 <= pt["confidence"] <= 1.0

    # Verify persisted in database
    db_preds = (
        db.query(Prediction)
        .filter(
            Prediction.crop_id == crop.id,
            Prediction.market_id == m_erode.id,
        )
        .all()
    )
    assert len(db_preds) >= 7


def test_forecasting_lightgbm_training_and_inference(db, intelligence_fixture):
    """Verify LightGBM quantile regression training, signal generation, and confidence bounds."""
    crop = intelligence_fixture["crop"]
    m_cbe = intelligence_fixture["m_cbe"]

    today = date.today()
    # Insert 35 records with strong upward trend (+10% total)
    base_price = 8000.0
    for i in range(35):
        d = today - timedelta(days=35 - i)
        price = base_price + (i * 30.0)
        db.add(
            MarketPrice(
                crop_id=crop.id,
                market_id=m_cbe.id,
                district="Coimbatore",
                modal_price=Decimal(str(round(price, 2))),
                min_price=Decimal(str(round(price - 50, 2))),
                max_price=Decimal(str(round(price + 50, 2))),
                arrival_quantity=60.0 + (i % 5) * 10,
                quality_score=Decimal("95.0"),
                price_date=d,
                source="ogd",
            )
        )
    db.commit()

    service = ForecastingService(db)
    # Train model
    mv = service.train_or_update_model(crop.id, m_cbe.id)
    assert mv is not None
    assert mv.model_type == "lightgbm_quantile"
    assert mv.is_active is True
    assert "mae" in mv.metrics

    # Generate forecast
    forecast = service.generate_forecast(crop.id, m_cbe.id, horizon_days=7, persist=True)
    assert len(forecast) == 7

    for pt in forecast:
        assert pt["model_type"] == "lightgbm_quantile"
        assert pt["lower_bound"] <= pt["predicted_price"] <= pt["upper_bound"]
        assert pt["confidence"] > 0.0

    # Due to upward trend, signal should be "hold" or "neutral"
    signals = [pt["signal"] for pt in forecast]
    assert "hold" in signals or "neutral" in signals


def test_intelligence_api_endpoints(db, intelligence_fixture):
    """Test REST API endpoints under /api/v1/intelligence/."""
    crop = intelligence_fixture["crop"]
    m_erode = intelligence_fixture["m_erode"]
    m_cbe = intelligence_fixture["m_cbe"]

    today = date.today()
    # Add prices so endpoints have data
    db.add(
        MarketPrice(
            crop_id=crop.id,
            market_id=m_erode.id,
            district="Erode",
            modal_price=Decimal("12000.00"),
            min_price=Decimal("11500.00"),
            max_price=Decimal("12500.00"),
            price_date=today,
            source="ogd",
        )
    )
    db.add(
        MarketPrice(
            crop_id=crop.id,
            market_id=m_cbe.id,
            district="Coimbatore",
            modal_price=Decimal("13000.00"),
            min_price=Decimal("12500.00"),
            max_price=Decimal("13500.00"),
            price_date=today,
            source="ogd",
        )
    )
    db.commit()

    # 1. Test Forecast API
    resp_fc = client.get(
        f"/api/v1/intelligence/forecast?crop_id={crop.id}&market_id={m_erode.id}&days=7"
    )
    assert resp_fc.status_code == 200
    fc_data = resp_fc.json()
    assert fc_data["crop_id"] == str(crop.id)
    assert fc_data["market_id"] == str(m_erode.id)
    assert len(fc_data["forecast"]) == 7

    # 2. Test Arbitrage API
    resp_arb = client.get(
        f"/api/v1/intelligence/arbitrage?crop_id={crop.id}&origin_market_id={m_erode.id}"
    )
    assert resp_arb.status_code == 200
    arb_data = resp_arb.json()
    assert arb_data["crop_id"] == str(crop.id)
    assert "opportunities" in arb_data

    # 3. Test Spreads API
    resp_sp = client.get(f"/api/v1/intelligence/spreads?crop_id={crop.id}")
    assert resp_sp.status_code == 200
    sp_data = resp_sp.json()
    assert sp_data["crop_id"] == str(crop.id)
    assert "price_spread" in sp_data
    assert "markets" in sp_data

    # 4. Test Train Model Trigger API
    resp_tr = client.post(
        "/api/v1/intelligence/train",
        json={"crop_id": str(crop.id), "market_id": str(m_erode.id)},
    )
    assert resp_tr.status_code == 200
    tr_data = resp_tr.json()
    assert "status" in tr_data
