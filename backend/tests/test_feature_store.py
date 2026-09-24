"""Unit tests for the Agricultural Feature Store engine."""

from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
import pytest

from app.ml.features import (
    FEATURE_COLUMNS,
    extract_features_for_series,
    get_latest_feature_vector,
)


def test_feature_store_empty_dataframe():
    """Verify empty DataFrame returns schema-compliant empty output."""
    empty_df = pd.DataFrame()
    res = extract_features_for_series(empty_df)
    assert res.empty
    assert "target_price" in res.columns
    assert "sample_weight" in res.columns
    for col in FEATURE_COLUMNS:
        assert col in res.columns


def test_feature_store_no_data_leakage():
    """Verify that lag and rolling features at row t only depend on past rows (< t)."""
    base_date = date(2026, 9, 1)
    dates = [base_date + timedelta(days=i) for i in range(20)]
    prices = [100.0 + i * 10 for i in range(20)]  # 100, 110, 120, ...

    df = pd.DataFrame({
        "price_date": dates,
        "modal_price": prices,
        "min_price": [p - 5 for p in prices],
        "max_price": [p + 5 for p in prices],
        "arrival_quantity": [50.0] * 20,
        "quality_score": [95.0] * 20,
    })

    feats = extract_features_for_series(df, target_horizon_days=1)

    # For row index 5 (date = 2026-09-06, price = 150):
    # lag_1 MUST be price of row 4 (140), NOT row 5 (150)
    assert feats.loc[5, "lag_1"] == 140.0
    assert feats.loc[5, "lag_2"] == 130.0

    # rolling_mean_7 at row 5 must be mean of rows 0..4 (100, 110, 120, 130, 140) = 120.0
    assert feats.loc[5, "rolling_mean_7"] == pytest.approx(120.0)

    # target_price at row 5 MUST be price of row 6 (160)
    assert feats.loc[5, "target_price"] == 160.0


def test_feature_store_tamil_calendar_festival_flags():
    """Verify Tamil festivals (e.g. Pongal on Jan 14-16) are correctly identified."""
    test_dates = [
        date(2026, 1, 10),
        date(2026, 1, 14),  # Bhogi / Pongal
        date(2026, 1, 15),  # Thai Pongal
        date(2026, 4, 14),  # Tamil New Year (Puthandu)
        date(2026, 6, 15),  # Non-festival date
    ]

    df = pd.DataFrame({
        "price_date": test_dates,
        "modal_price": [7000.0, 7500.0, 7800.0, 8000.0, 6800.0],
    })

    feats = extract_features_for_series(df)

    # Row 1 (Jan 14) and Row 2 (Jan 15) must be marked as festivals
    assert feats.loc[1, "is_festival"] == 1
    assert feats.loc[2, "is_festival"] == 1
    assert feats.loc[3, "is_festival"] == 1  # Puthandu
    assert feats.loc[4, "is_festival"] == 0  # Non-festival

    # Row 0 (Jan 10) is 4 days before Jan 14 Pongal
    assert feats.loc[0, "days_to_festival"] <= 4


def test_feature_store_weather_merging():
    """Verify agro-climatic signals are merged and lagged properly."""
    dates = [date(2026, 9, 1) + timedelta(days=i) for i in range(10)]
    df = pd.DataFrame({
        "price_date": dates,
        "modal_price": [50.0] * 10,
    })

    weather_df = pd.DataFrame({
        "date": dates,
        "rainfall_mm": [0.0, 10.0, 25.0, 5.0, 0.0, 0.0, 12.0, 0.0, 0.0, 0.0],
        "temperature_max": [32.0, 31.0, 28.0, 30.0, 33.0, 34.0, 29.0, 32.0, 33.0, 32.0],
    })

    feats = extract_features_for_series(df, weather_df=weather_df)
    assert "rainfall_lag_3d" in feats.columns
    assert "temp_max_lag_3d" in feats.columns
    # Check that lagged rainfall at row 3 reflects prior rain
    assert feats.loc[3, "rainfall_lag_3d"] > 0.0


def test_get_latest_feature_vector():
    """Verify single-row feature vector generation for live inference."""
    dates = [date(2026, 9, 1) + timedelta(days=i) for i in range(15)]
    df = pd.DataFrame({
        "price_date": dates,
        "modal_price": [2000.0 + i * 50 for i in range(15)],
    })

    vec = get_latest_feature_vector(df)
    assert vec.shape[0] == 1
    assert list(vec.columns) == FEATURE_COLUMNS
    assert not vec.isnull().values.any()
