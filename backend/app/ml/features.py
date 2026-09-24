"""Agricultural Feature Store Engine for FPOLink TN.

Extracts tabular feature vectors from historical mandi price observations,
arrival records, Tamil Nadu agricultural calendar attributes, and agro-climatic signals.
"""

from datetime import date, datetime
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd

from app.data_sources.holidays_tn import days_to_nearest_festival, is_festival


FEATURE_COLUMNS = [
    # Lags
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_7",
    "lag_14",
    "lag_30",
    # Rolling Price Stats
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_min_7",
    "rolling_max_7",
    "rolling_mean_14",
    "rolling_std_14",
    "rolling_mean_30",
    "rolling_std_30",
    "price_spread_7",
    "daily_spread",
    # Arrival Volume Momentum
    "arrival_rolling_mean_7",
    "arrival_momentum_7",
    # Calendar & Festival Features
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "is_festival",
    "days_to_festival",
    # Weather Signals (if available)
    "rainfall_lag_3d",
    "temp_max_lag_3d",
]


def extract_features_for_series(
    df: pd.DataFrame,
    target_horizon_days: int = 1,
    weather_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Transform historical price observations into an ML feature matrix.

    Args:
        df: DataFrame containing at least:
            - 'price_date': date or string date
            - 'modal_price': numeric
            - 'min_price': numeric (optional)
            - 'max_price': numeric (optional)
            - 'arrival_quantity': numeric (optional)
            - 'quality_score': numeric (optional, 0-100)
        target_horizon_days: Number of days forward to predict (default: 1 day).
        weather_df: Optional DataFrame with 'date', 'rainfall_mm', 'temperature_max'.

    Returns:
        DataFrame containing all feature columns, sample_weight, and 'target_price'.
    """
    if df.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS + ["sample_weight", "target_price"])

    df = df.copy()

    # Standardize date column
    if not np.issubdtype(df["price_date"].dtype, np.datetime64):
        df["price_date"] = pd.to_datetime(df["price_date"])

    df = df.sort_values("price_date").reset_index(drop=True)

    # Convert numeric fields
    for col in ["modal_price", "min_price", "max_price", "arrival_quantity", "quality_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    # Fill default min/max if missing
    df["min_price"] = df["min_price"].fillna(df["modal_price"])
    df["max_price"] = df["max_price"].fillna(df["modal_price"])
    df["arrival_quantity"] = df["arrival_quantity"].fillna(0.0)
    df["quality_score"] = df["quality_score"].fillna(100.0)

    # 1. Price Lags
    for lag in [1, 2, 3, 7, 14, 30]:
        df[f"lag_{lag}"] = df["modal_price"].shift(lag)

    # 2. Rolling Price Statistics (closed='left' to avoid data leakage)
    rolling_7 = df["modal_price"].shift(1).rolling(window=7, min_periods=1)
    df["rolling_mean_7"] = rolling_7.mean()
    df["rolling_std_7"] = rolling_7.std().fillna(0.0)
    df["rolling_min_7"] = rolling_7.min()
    df["rolling_max_7"] = rolling_7.max()
    df["price_spread_7"] = df["rolling_max_7"] - df["rolling_min_7"]

    rolling_14 = df["modal_price"].shift(1).rolling(window=14, min_periods=1)
    df["rolling_mean_14"] = rolling_14.mean()
    df["rolling_std_14"] = rolling_14.std().fillna(0.0)

    rolling_30 = df["modal_price"].shift(1).rolling(window=30, min_periods=1)
    df["rolling_mean_30"] = rolling_30.mean()
    df["rolling_std_30"] = rolling_30.std().fillna(0.0)

    df["daily_spread"] = (df["max_price"] - df["min_price"]).shift(1).fillna(0.0)

    # 3. Arrival Volume Momentum
    rolling_arr_7 = df["arrival_quantity"].shift(1).rolling(window=7, min_periods=1)
    df["arrival_rolling_mean_7"] = rolling_arr_7.mean().fillna(0.0)
    prev_arrival = df["arrival_quantity"].shift(1).fillna(0.0)
    df["arrival_momentum_7"] = (prev_arrival / (df["arrival_rolling_mean_7"] + 1e-4)).clip(0.0, 10.0)

    # 4. Calendar & Tamil Festival Features
    df["day_of_week"] = df["price_date"].dt.dayofweek
    df["day_of_month"] = df["price_date"].dt.day
    df["month"] = df["price_date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    dates = df["price_date"].dt.date
    df["is_festival"] = [1 if is_festival(d) else 0 for d in dates]
    df["days_to_festival"] = [days_to_nearest_festival(d, window=30) for d in dates]

    # 5. Weather Features (Lagged to prevent future leakage)
    if weather_df is not None and not weather_df.empty:
        weather_df = weather_df.copy()
        if not np.issubdtype(weather_df["date"].dtype, np.datetime64):
            weather_df["date"] = pd.to_datetime(weather_df["date"])
        w_merged = pd.merge(df[["price_date"]], weather_df, left_on="price_date", right_on="date", how="left")
        df["rainfall_lag_3d"] = w_merged["rainfall_mm"].shift(1).rolling(3, min_periods=1).sum().fillna(0.0)
        df["temp_max_lag_3d"] = w_merged["temperature_max"].shift(1).rolling(3, min_periods=1).mean().fillna(30.0)
    else:
        df["rainfall_lag_3d"] = 0.0
        df["temp_max_lag_3d"] = 30.0

    # 6. Sample Weights from Ingestion Data Quality Score (0 to 100 normalized to 0.1 to 1.0)
    df["sample_weight"] = (df["quality_score"].clip(10.0, 100.0) / 100.0)

    # 7. Target Price (Forward Horizon)
    df["target_price"] = df["modal_price"].shift(-target_horizon_days)

    # Impute missing initial lags with the earliest available modal price
    first_modal = df["modal_price"].dropna().iloc[0] if not df["modal_price"].dropna().empty else 0.0
    for lag in [1, 2, 3, 7, 14, 30]:
        df[f"lag_{lag}"] = df[f"lag_{lag}"].bfill().fillna(first_modal)

    for col in [
        "rolling_mean_7", "rolling_min_7", "rolling_max_7",
        "rolling_mean_14", "rolling_mean_30",
    ]:
        df[col] = df[col].bfill().fillna(first_modal)

    return df


def get_latest_feature_vector(df: pd.DataFrame, weather_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Generate the single inference feature vector for the most recent observation to predict tomorrow."""
    features_df = extract_features_for_series(df, target_horizon_days=1, weather_df=weather_df)
    if features_df.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS)
    return features_df.iloc[[-1]][FEATURE_COLUMNS]
