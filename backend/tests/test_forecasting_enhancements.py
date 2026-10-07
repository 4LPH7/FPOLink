"""Tests for Phase M2 Forecasting Enhancements.

Verifies:
1. Baseline forecasters (seasonal_naive and seasonal_median_baseline) selectable via API.
2. Querying forecast via crop and market name resolution.
3. Bilingual disclaimer inclusion in ForecastResponse schema.
4. Legacy /api/predictions/forecast route compatibility.
5. Continuous telemetry and score_past_forecasts evaluation.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.forecasting import ForecastingService
from app.models.crop import Crop
from app.models.forecast_log import ForecastLog
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.prediction import Prediction

client = TestClient(app)


@pytest.fixture
def forecast_test_env(db):
    """Sets up state, district, crop, market, and seeded prices for testing."""
    state = db.query(State).filter(State.code == "TN").first()
    if not state:
        state = State(name="Tamil Nadu", code="TN")
        db.add(state)
        db.commit()
        db.refresh(state)

    dist = db.query(District).filter(District.name == "Erode").first()
    if not dist:
        dist = District(name="Erode", state_id=state.id, code="ERD")
        db.add(dist)
        db.commit()
        db.refresh(dist)

    mandi = db.query(Market).filter(Market.code == "TN-ERD-FORECAST").first()
    if not mandi:
        mandi = Market(
            name="Erode Regulated Mandi",
            code="TN-ERD-FORECAST",
            district="Erode",
            district_id=dist.id,
            state="Tamil Nadu",
            latitude=11.3410,
            longitude=77.7172,
            is_active=True,
            is_regulated=True,
        )
        db.add(mandi)
        db.commit()
        db.refresh(mandi)

    crop = db.query(Crop).filter(Crop.name == "Turmeric Test").first()
    if not crop:
        crop = Crop(
            name="Turmeric Test",
            canonical_name="turmeric_test",
            tamil_name="மஞ்சள் டெஸ்ட்",
            category="spices",
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    # Seed 35 daily market price records to allow baseline forecasting
    today = date.today()
    for i in range(35, 0, -1):
        p_date = today - timedelta(days=i)
        existing = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.crop_id == crop.id,
                MarketPrice.market_id == mandi.id,
                MarketPrice.price_date == p_date,
            )
            .first()
        )
        if not existing:
            price_val = Decimal(str(85.0 + (i % 5)))
            mp = MarketPrice(
                crop_id=crop.id,
                market_id=mandi.id,
                district=mandi.district or "Erode",
                price_date=p_date,
                modal_price=price_val,
                min_price=price_val - Decimal("2.0"),
                max_price=price_val + Decimal("2.0"),
                source="agmarknet",
                raw_price=price_val * 100,
                raw_unit="quintal",
            )
            db.add(mp)
    db.commit()

    return {
        "state": state,
        "district": dist,
        "crop": crop,
        "market": mandi,
    }


def test_forecast_name_resolution_and_disclaimer(forecast_test_env):
    """Test resolution of crop & market names, and presence of bilingual disclaimers."""
    crop_name = forecast_test_env["crop"].name
    market_name = forecast_test_env["market"].name

    resp = client.get(
        "/api/v1/intelligence/forecast",
        params={"crop": crop_name, "market": market_name, "days": 7},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["crop_name"] == crop_name
    assert data["market_name"] == market_name
    assert "disclaimer_ta" in data
    assert "disclaimer_en" in data
    assert "மதிப்பீடு" in data["disclaimer_ta"]
    assert "Estimate only" in data["disclaimer_en"]
    assert len(data["forecast"]) == 7


def test_forecast_baseline_model_selection(forecast_test_env):
    """Test explicitly requesting seasonal_naive and baseline models."""
    crop_id = str(forecast_test_env["crop"].id)
    market_id = str(forecast_test_env["market"].id)

    # 1. Seasonal Naive
    resp_naive = client.get(
        "/api/v1/intelligence/forecast",
        params={
            "crop_id": crop_id,
            "market_id": market_id,
            "days": 5,
            "model_type": "seasonal_naive",
        },
    )
    assert resp_naive.status_code == 200
    data_naive = resp_naive.json()
    assert len(data_naive["forecast"]) == 5
    for pt in data_naive["forecast"]:
        assert pt["model_type"] == "seasonal_naive_baseline"

    # 2. Seasonal Median Baseline
    resp_base = client.get(
        "/api/v1/intelligence/forecast",
        params={
            "crop_id": crop_id,
            "market_id": market_id,
            "days": 5,
            "model_type": "baseline",
        },
    )
    assert resp_base.status_code == 200
    data_base = resp_base.json()
    assert len(data_base["forecast"]) == 5
    for pt in data_base["forecast"]:
        assert pt["model_type"] == "seasonal_median_baseline"


def test_legacy_predictions_endpoint(forecast_test_env):
    """Test legacy /api/predictions/forecast endpoint."""
    crop_name = forecast_test_env["crop"].name
    market_name = forecast_test_env["market"].name

    resp = client.get(
        "/api/predictions/forecast",
        params={"crop": crop_name, "market": market_name, "days": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "forecast" in data
    assert len(data["forecast"]) == 3


def test_score_past_forecasts(db, forecast_test_env):
    """Test continuous scoring telemetry of past predictions against ground truth."""
    crop = forecast_test_env["crop"]
    market = forecast_test_env["market"]
    past_date = date.today() - timedelta(days=2)

    # 1. Create a historical prediction
    pred = Prediction(
        crop_id=crop.id,
        market_id=market.id,
        prediction_date=past_date - timedelta(days=7),
        target_date=past_date,
        predicted_price=Decimal("88.50"),
        lower_bound=Decimal("85.00"),
        upper_bound=Decimal("92.00"),
        confidence=Decimal("0.80"),
        model_version_id=None,
        signal="neutral",
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    # 2. Add un-scored forecast_log
    f_log = ForecastLog(prediction_id=pred.id)
    db.add(f_log)
    db.commit()
    db.refresh(f_log)

    # 3. Ensure actual market price exists for past_date
    actual_mp = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop.id,
            MarketPrice.market_id == market.id,
            MarketPrice.price_date == past_date,
        )
        .first()
    )
    if not actual_mp:
        actual_mp = MarketPrice(
            crop_id=crop.id,
            market_id=market.id,
            district=market.district or "Erode",
            price_date=past_date,
            modal_price=Decimal("86.50"),
            min_price=Decimal("84.50"),
            max_price=Decimal("88.50"),
            source="agmarknet",
            raw_price=Decimal("8650.00"),
            raw_unit="quintal",
        )
        db.add(actual_mp)
        db.commit()

    # 4. Run score_past_forecasts
    service = ForecastingService(db)
    result = service.score_past_forecasts()

    assert result["evaluated_count"] >= 1
    assert result["mean_absolute_error"] >= 0.0

    # 5. Check f_log has been evaluated
    db.refresh(f_log)
    assert f_log.evaluated_at is not None
    assert f_log.actual_price is not None
    assert f_log.error is not None
    expected_error = abs(Decimal("88.50") - Decimal(str(actual_mp.modal_price)))
    assert f_log.error == round(expected_error, 2)
