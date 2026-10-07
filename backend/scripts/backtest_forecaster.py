"""Rolling-Origin Walk-Forward Backtest Harness and Model Promotion CLI.

Evaluates forecasting accuracy without lookahead bias using chronological train/test splits.
Compares Seasonal Moving-Average Baseline vs. LightGBM Quantile Regression on historical data.
Applies automated champion promotion rules and persists validation metrics to `model_versions`.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import lightgbm as lgb
import numpy as np
import pandas as pd

# Add backend directory to sys.path so app imports resolve
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal  # noqa: E402
from app.ml.features import (  # noqa: E402
    FEATURE_COLUMNS,
    extract_features_for_series,
    get_latest_feature_vector,
)
from app.models.crop import Crop  # noqa: E402
from app.models.market import Market  # noqa: E402
from app.models.model_version import ModelVersion  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backtest_forecaster")

DEFAULT_DATASET = backend_dir.parent / "ml" / "datasets" / "erode_agmarknet_historical_2026.csv"
DOCS_REPORT_PATH = backend_dir.parent / "docs" / "FORECAST_BACKTEST.md"


def evaluate_series_rolling_origin(
    df: pd.DataFrame,
    horizon: int = 7,
    step: int = 7,
    min_train: int = 35,
    promotion_threshold_pct: float = 3.0,
) -> Dict:
    """Run rolling-origin backtest on a single (crop, market) time series."""
    df = df.sort_values("price_date").reset_index(drop=True)
    n = len(df)
    if n < min_train + horizon:
        return {
            "error": f"Insufficient data: {n} observations (need at least {min_train + horizon})"
        }

    base_errors = []
    base_mapes = []
    base_covered = []

    lgb_errors = []
    lgb_mapes = []
    lgb_covered = []

    windows_evaluated = 0

    origin = min_train
    while origin + horizon <= n:
        train_df = df.iloc[:origin].copy()
        test_df = df.iloc[origin : origin + horizon].copy()
        actuals = test_df["modal_price"].values

        # 1. Baseline Evaluation (Rolling Median + Expanding Horizon Band)
        recent_window = train_df["modal_price"].tail(14)
        base_pred = float(recent_window.median())
        volatility = float(recent_window.std()) if len(recent_window) > 1 else base_pred * 0.05
        volatility = max(volatility, base_pred * 0.03)

        for h_step, actual in enumerate(actuals, start=1):
            base_err = abs(actual - base_pred)
            base_errors.append(base_err)
            base_mapes.append((base_err / max(actual, 1.0)) * 100.0)

            expansion = 1.0 + (h_step - 1) * 0.08
            p10 = max(0.0, base_pred - 1.645 * volatility * expansion)
            p90 = base_pred + 1.645 * volatility * expansion
            base_covered.append(1 if (p10 <= actual <= p90) else 0)

        # 2. LightGBM Quantile Evaluation
        feat_df = extract_features_for_series(train_df, target_horizon_days=1).dropna(
            subset=["target_price"]
        )
        if len(feat_df) >= 20:
            X_train = feat_df[FEATURE_COLUMNS]
            y_train = feat_df["target_price"]
            weights = feat_df["sample_weight"]

            models = {}
            for alpha in [0.10, 0.50, 0.90]:
                reg = lgb.LGBMRegressor(
                    objective="quantile",
                    alpha=alpha,
                    n_estimators=45,
                    learning_rate=0.08,
                    num_leaves=12,
                    min_child_samples=5,
                    verbose=-1,
                    random_state=42,
                )
                reg.fit(X_train, y_train, sample_weight=weights)
                models[f"p{int(alpha * 100)}"] = reg

            rolling_sim = train_df.copy()
            for h_step, actual in enumerate(actuals, start=1):
                X_feat = get_latest_feature_vector(rolling_sim)
                pred_p10 = float(models["p10"].predict(X_feat)[0])
                pred_p50 = float(models["p50"].predict(X_feat)[0])
                pred_p90 = float(models["p90"].predict(X_feat)[0])

                l_bound = min(pred_p10, pred_p50)
                u_bound = max(pred_p90, pred_p50)

                lgb_err = abs(actual - pred_p50)
                lgb_errors.append(lgb_err)
                lgb_mapes.append((lgb_err / max(actual, 1.0)) * 100.0)
                lgb_covered.append(1 if (l_bound <= actual <= u_bound) else 0)

                # Feed predicted value forward
                sim_row = pd.DataFrame(
                    [
                        {
                            "price_date": test_df["price_date"].iloc[h_step - 1],
                            "modal_price": pred_p50,
                            "min_price": l_bound,
                            "max_price": u_bound,
                            "arrival_quantity": float(rolling_sim["arrival_quantity"].iloc[-1])
                            if "arrival_quantity" in rolling_sim
                            else 0.0,
                            "quality_score": 100.0,
                        }
                    ]
                )
                rolling_sim = pd.concat([rolling_sim, sim_row], ignore_index=True)

        windows_evaluated += 1
        origin += step

    base_mae = float(np.mean(base_errors)) if base_errors else 0.0
    base_mape = float(np.mean(base_mapes)) if base_mapes else 0.0
    base_picp = (float(np.mean(base_covered)) * 100.0) if base_covered else 0.0

    lgb_mae = float(np.mean(lgb_errors)) if lgb_errors else base_mae
    lgb_mape = float(np.mean(lgb_mapes)) if lgb_mapes else base_mape
    lgb_picp = (float(np.mean(lgb_covered)) * 100.0) if lgb_covered else base_picp

    # Promotion Decision Rule:
    # Challenger (LightGBM) is promoted ONLY if out-of-sample MAE improves by at least promotion_threshold_pct
    mae_diff_pct = ((base_mae - lgb_mae) / max(base_mae, 1.0)) * 100.0
    is_promoted = (mae_diff_pct >= promotion_threshold_pct) and (len(lgb_errors) > 0)

    champion = "lightgbm_quantile" if is_promoted else "seasonal_median_baseline"

    return {
        "windows_evaluated": windows_evaluated,
        "total_test_points": len(base_errors),
        "baseline": {
            "mae": round(base_mae, 2),
            "mape": round(base_mape, 2),
            "picp": round(base_picp, 1),
        },
        "challenger_lgbm": {
            "mae": round(lgb_mae, 2),
            "mape": round(lgb_mape, 2),
            "picp": round(lgb_picp, 1),
        },
        "improvement_pct": round(mae_diff_pct, 2),
        "promoted_challenger": is_promoted,
        "champion_model": champion,
    }


def write_markdown_report(results: Dict[str, Dict], horizon: int) -> None:
    """Generate docs/FORECAST_BACKTEST.md report."""
    md = []
    md.append("# FPOLink TN — Price Forecasting Backtest & Model Validation Report\n")
    md.append(f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(
        f"> **Evaluation Strategy:** Rolling-Origin Walk-Forward Backtesting (Horizon = {horizon} Days)  "
    )
    md.append("> **Lookahead Leakage:** Zero (strictly chronological training origins)  \n")
    md.append("---\n")
    md.append("## 1. Executive Summary\n")
    md.append(
        "In accordance with **P2 Defensible Forecasting** requirements, all models are evaluated"
    )
    md.append(
        "using chronological backtests across multi-month historical records rather than random train/test splits."
    )
    md.append(
        "A challenger model (LightGBM Quantile Regression) is promoted to Champion only if it demonstrates an out-of-sample"
    )
    md.append("MAE improvement $\\ge 3\\%$ over the robust Seasonal Median Baseline.\n\n")

    md.append("## 2. Benchmark Evaluation Table\n\n")
    md.append(
        "| Commodity & Market | Windows | Baseline MAE (₹/kg) | Baseline MAPE | Baseline 80% PICP | Challenger MAE (₹/kg) | Challenger MAPE | Challenger 80% PICP | $\\Delta$ MAE | Designated Champion |"
    )
    md.append("|---|---|---|---|---|---|---|---|---|---|")

    for key, res in results.items():
        if "error" in res:
            continue
        b = res["baseline"]
        c = res["challenger_lgbm"]
        champ = "**LightGBM**" if res["promoted_challenger"] else "**Baseline (Robust)**"
        diff_str = f"{res['improvement_pct']:+.1f}%"
        md.append(
            f"| `{key}` | {res['windows_evaluated']} | ₹{b['mae']} | {b['mape']}% | {b['picp']}% | ₹{c['mae']} | {c['mape']}% | {c['picp']}% | {diff_str} | {champ} |"
        )

    md.append("\n---\n")
    md.append("## 3. Methodology & Guardrails\n\n")
    md.append(
        "1. **Rolling-Origin Windows**: Origin advances by 7-day increments. Training is restricted strictly to historical observations prior to origin."
    )
    md.append(
        "2. **Quantile Coverage (PICP)**: Evaluates empirical coverage of the $[p_{10}, p_{90}]$ prediction interval. Expected coverage for well-calibrated intervals is $\\approx 80\\%$."
    )
    md.append(
        "3. **Monotonicity Enforcement**: Quantile crossing is prevented by ensuring $p_{10} \\le p_{50} \\le p_{90}$ across all horizon steps."
    )
    md.append(
        "4. **Operational Fallback**: When series observations are sparse ($< 30$ records) or stale ($> 7$ days), the API defaults automatically to the Baseline with expanded uncertainty bounds."
    )
    md.append(
        "5. **Bilingual Disclaimer**: Every forecast carries explicit Tamil and English disclaimers (`இது மதிப்பீடு மட்டுமே, கொள்முதல் அல்லது விற்பனை ஆலோசனை அல்ல`).\n"
    )

    report_content = "\n".join(md)
    os.makedirs(DOCS_REPORT_PATH.parent, exist_ok=True)
    with open(DOCS_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nSaved backtest verification report to: {DOCS_REPORT_PATH}")


def run_backtest_cli(
    csv_file: Path,
    horizon: int = 7,
    step: int = 7,
    save_to_db: bool = True,
) -> int:
    """Run walk-forward evaluation across all commodity series in dataset."""
    if not csv_file.exists():
        print(f"Error: Dataset not found at {csv_file}")
        return 1

    print(f"\nRunning Rolling-Origin Backtest [Dataset: {csv_file.name}]")
    print(f"Horizon: {horizon} days | Walk-forward Step: {step} days\n")

    raw_df = pd.read_csv(csv_file)
    # Standardize column names
    col_map = {
        "date": "price_date",
        "commodity_name": "crop_name",
        "commodity": "crop_name",
        "market": "market_name",
    }
    for c, target in col_map.items():
        if c in raw_df.columns:
            raw_df[target] = raw_df[c]

    raw_df["price_date"] = pd.to_datetime(raw_df["price_date"]).dt.date
    raw_df["modal_price"] = pd.to_numeric(raw_df["modal_price"], errors="coerce")
    # If prices in raw are per quintal (> 500), convert to Rs/kg for consistent comparison
    if raw_df["modal_price"].median() > 500:
        raw_df["modal_price"] = raw_df["modal_price"] / 100.0

    series_groups = raw_df.groupby(["crop_name", "market_name"])
    all_results = {}

    db = SessionLocal() if save_to_db else None

    print("=" * 95)
    print(
        f"{'Commodity @ Mandi':<30} | {'Base MAE':<10} | {'LGBM MAE':<10} | {'Improvement':<12} | {'80% Coverage':<12} | {'Champion'}"
    )
    print("=" * 95)

    for (crop, market), group in series_groups:
        series_key = f"{crop.capitalize()} @ {market.capitalize()}"
        res = evaluate_series_rolling_origin(group, horizon=horizon, step=step)
        all_results[series_key] = res

        if "error" in res:
            print(f"{series_key:<30} | {res['error']}")
            continue

        b_mae = f"₹{res['baseline']['mae']}"
        l_mae = f"₹{res['challenger_lgbm']['mae']}"
        imp = f"{res['improvement_pct']:+.1f}%"
        picp = f"{res['challenger_lgbm']['picp']}%"
        champ = "LightGBM" if res["promoted_challenger"] else "Baseline"

        print(f"{series_key:<30} | {b_mae:<10} | {l_mae:<10} | {imp:<12} | {picp:<12} | {champ}")

        # Persist validation result to model_versions table
        if db:
            crop_obj = db.query(Crop).filter(Crop.name.ilike(crop.strip())).first()
            market_obj = db.query(Market).filter(Market.name.ilike(market.strip())).first()
            if crop_obj and market_obj:
                m_name = f"lgb_quantile_{crop_obj.id}_{market_obj.id}"
                # Record evaluation metrics
                mv = ModelVersion(
                    model_name=m_name,
                    model_type=res["champion_model"],
                    metrics={
                        "evaluation_type": "rolling_origin_backtest",
                        "horizon_days": horizon,
                        "windows_evaluated": res["windows_evaluated"],
                        "baseline_mae": res["baseline"]["mae"],
                        "baseline_mape": res["baseline"]["mape"],
                        "challenger_mae": res["challenger_lgbm"]["mae"],
                        "challenger_mape": res["challenger_lgbm"]["mape"],
                        "picp_80": res["challenger_lgbm"]["picp"],
                        "improvement_pct": res["improvement_pct"],
                        "promoted": res["promoted_challenger"],
                    },
                    is_active=True,
                    trained_at=datetime.utcnow(),
                )
                db.add(mv)
                db.commit()

    if db:
        db.close()

    print("=" * 95)
    write_markdown_report(all_results, horizon=horizon)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Rolling-Origin Forecast Backtest & Validation")
    parser.add_argument(
        "--csv-file", default=str(DEFAULT_DATASET), help="Path to historical CSV dataset"
    )
    parser.add_argument("--horizon", type=int, default=7, help="Forecast horizon days (default: 7)")
    parser.add_argument("--step", type=int, default=7, help="Walk-forward step days (default: 7)")
    parser.add_argument(
        "--no-db", action="store_true", help="Do not persist to model_versions table"
    )

    args = parser.parse_args()
    code = run_backtest_cli(
        csv_file=Path(args.csv_file),
        horizon=args.horizon,
        step=args.step,
        save_to_db=not args.no_db,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
