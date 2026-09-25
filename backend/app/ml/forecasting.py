"""Dual-Engine Agricultural Price Forecasting for FPOLink TN.

Primary Engine: LightGBM Quantile Regression (p10, p50, p90)
Fallback Engine: Robust Empirical Rolling Median Baseline for sparse series (< 30 observations).
"""

import logging
import os
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ml.features import (
    FEATURE_COLUMNS,
    extract_features_for_series,
    get_latest_feature_vector,
)
from app.models.market_price import MarketPrice
from app.models.model_version import ModelVersion
from app.models.prediction import Prediction

logger = logging.getLogger(__name__)

MODELS_DIR = "/tmp/fpolink_models"
os.makedirs(MODELS_DIR, exist_ok=True)


def load_price_series(
    db: Session,
    crop_id: UUID,
    market_id: UUID,
    limit: int = 365,
) -> pd.DataFrame:
    """Fetch chronological price history for a given crop and market."""
    records = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
        )
        .order_by(MarketPrice.price_date.asc())
        .limit(limit)
        .all()
    )

    if not records:
        return pd.DataFrame()

    data = [
        {
            "price_date": r.price_date,
            "modal_price": float(r.modal_price),
            "min_price": float(r.min_price) if r.min_price is not None else float(r.modal_price),
            "max_price": float(r.max_price) if r.max_price is not None else float(r.modal_price),
            "arrival_quantity": float(r.arrival_quantity)
            if r.arrival_quantity is not None
            else 0.0,
            "quality_score": float(r.quality_score) if r.quality_score is not None else 100.0,
        }
        for r in records
    ]
    return pd.DataFrame(data)


def compute_forecast_signal(current_price: float, predicted_price: float) -> str:
    """Determine actionable selling signal based on expected price change."""
    if current_price <= 0:
        return "neutral"
    ratio = predicted_price / current_price
    if ratio >= 1.05:
        return "hold"
    elif ratio <= 0.95:
        return "sell"
    return "neutral"


class ForecastingService:
    """Dual-engine forecasting and signal generation service."""

    def __init__(self, db: Session):
        self.db = db

    def train_or_update_model(
        self,
        crop_id: UUID,
        market_id: UUID,
    ) -> Optional[ModelVersion]:
        """Train LightGBM Quantile Regressors (p10, p50, p90) if sufficient data exists."""
        df = load_price_series(self.db, crop_id, market_id)
        if len(df) < 30:
            logger.info(
                f"Insufficient data ({len(df)} records) for LightGBM; fallback baseline will be used."
            )
            return None

        # Build feature matrix
        feat_df = extract_features_for_series(df, target_horizon_days=1)
        feat_df = feat_df.dropna(subset=["target_price"])
        if len(feat_df) < 20:
            return None

        X = feat_df[FEATURE_COLUMNS]
        y = feat_df["target_price"]
        weights = feat_df["sample_weight"]

        # Train 3 quantile models
        models = {}
        for alpha in [0.10, 0.50, 0.90]:
            reg = lgb.LGBMRegressor(
                objective="quantile",
                alpha=alpha,
                n_estimators=60,
                learning_rate=0.08,
                num_leaves=15,
                min_child_samples=5,
                verbose=-1,
                random_state=42,
            )
            reg.fit(X, y, sample_weight=weights)
            models[f"p{int(alpha * 100)}"] = reg

        # Evaluate p50 MAE / MAPE
        preds_p50 = models["p50"].predict(X)
        mae = float(np.mean(np.abs(y - preds_p50)))
        mape = float(np.mean(np.abs((y - preds_p50) / np.maximum(y, 1.0)))) * 100.0

        model_name = f"lgb_quantile_{crop_id}_{market_id}"
        file_path = os.path.join(MODELS_DIR, f"{model_name}.joblib")
        joblib.dump(models, file_path)

        # Deactivate previous versions
        self.db.query(ModelVersion).filter(ModelVersion.model_name == model_name).update(
            {"is_active": False}
        )

        mv = ModelVersion(
            model_name=model_name,
            model_type="lightgbm_quantile",
            metrics={"mae": round(mae, 2), "mape": round(mape, 2), "train_samples": len(X)},
            file_path=file_path,
            is_active=True,
            trained_at=func.now(),
        )
        self.db.add(mv)
        self.db.commit()
        self.db.refresh(mv)
        return mv

    def generate_forecast(
        self,
        crop_id: UUID,
        market_id: UUID,
        horizon_days: int = 7,
        persist: bool = True,
    ) -> List[Dict]:
        """Generate N-day price forecast with p10/p50/p90 intervals and actionable signals."""
        df = load_price_series(self.db, crop_id, market_id)
        if df.empty:
            return []

        current_price = float(df["modal_price"].iloc[-1])
        last_date = df["price_date"].iloc[-1]
        if isinstance(last_date, str):
            last_date = date.fromisoformat(last_date)
        elif isinstance(last_date, pd.Timestamp):
            last_date = last_date.date()

        model_name = f"lgb_quantile_{crop_id}_{market_id}"
        active_model = (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_name == model_name, ModelVersion.is_active.is_(True))
            .first()
        )

        models = None
        if active_model and active_model.file_path and os.path.exists(active_model.file_path):
            try:
                models = joblib.load(active_model.file_path)
            except Exception as e:
                logger.warning(f"Failed to load model file: {e}")

        # Check if we can run ML or need Baseline
        forecast_points = []
        running_df = df.copy()

        for step in range(1, horizon_days + 1):
            target_date = last_date + timedelta(days=step)

            if models is not None:
                # Use trained LightGBM Quantile Models
                X_latest = get_latest_feature_vector(running_df)
                p10 = float(models["p10"].predict(X_latest)[0])
                p50 = float(models["p50"].predict(X_latest)[0])
                p90 = float(models["p90"].predict(X_latest)[0])

                # Quantile monotonicity guarantee: p10 <= p50 <= p90
                lower_bound = round(min(p10, p50), 2)
                predicted_price = round(p50, 2)
                upper_bound = round(max(p90, p50), 2)
                confidence = float(
                    np.clip(
                        1.0 - (upper_bound - lower_bound) / max(predicted_price, 1.0), 0.5, 0.95
                    )
                )
                model_type = "lightgbm_quantile"
                model_version_id = active_model.id
            else:
                # Robust Baseline: Rolling Median + Interquartile / Empirical Spread
                recent_window = running_df["modal_price"].tail(14)
                predicted_price = round(float(recent_window.median()), 2)
                volatility = (
                    float(recent_window.std()) if len(recent_window) > 1 else predicted_price * 0.05
                )
                volatility = max(volatility, predicted_price * 0.03)

                # Uncertainty expands with prediction horizon
                spread_expansion = 1.0 + (step - 1) * 0.08
                lower_bound = round(
                    max(0.0, predicted_price - 1.645 * volatility * spread_expansion), 2
                )
                upper_bound = round(predicted_price + 1.645 * volatility * spread_expansion, 2)
                confidence = round(min(0.80, max(0.50, len(running_df) / 35.0)), 2)
                model_type = "seasonal_median_baseline"
                model_version_id = None

            signal = compute_forecast_signal(current_price, predicted_price)

            point = {
                "crop_id": str(crop_id),
                "market_id": str(market_id),
                "target_date": target_date.isoformat(),
                "predicted_price": predicted_price,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence": round(confidence, 2),
                "signal": signal,
                "model_type": model_type,
            }
            forecast_points.append(point)

            if persist:
                pred_record = Prediction(
                    crop_id=crop_id,
                    market_id=market_id,
                    predicted_price=Decimal(str(predicted_price)),
                    lower_bound=Decimal(str(lower_bound)),
                    upper_bound=Decimal(str(upper_bound)),
                    confidence=confidence,
                    model_version_id=model_version_id,
                    prediction_date=last_date,
                    target_date=target_date,
                    signal=signal,
                )
                self.db.add(pred_record)

            # Append synthetic prediction into running_df for autoregressive rolling steps
            new_row = pd.DataFrame(
                [
                    {
                        "price_date": pd.to_datetime(target_date),
                        "modal_price": predicted_price,
                        "min_price": lower_bound,
                        "max_price": upper_bound,
                        "arrival_quantity": float(running_df["arrival_quantity"].iloc[-1]),
                        "quality_score": 100.0,
                    }
                ]
            )
            running_df = pd.concat([running_df, new_row], ignore_index=True)

        if persist:
            self.db.commit()

        return forecast_points
