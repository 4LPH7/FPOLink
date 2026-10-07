# FPOLink TN — Price Forecasting Backtest & Model Validation Report

> **Generated:** 2026-10-07 13:27:18  
> **Evaluation Strategy:** Rolling-Origin Walk-Forward Backtesting (Horizon = 7 Days)  
> **Lookahead Leakage:** Zero (strictly chronological training origins)  

---

## 1. Executive Summary

In accordance with **P2 Defensible Forecasting** requirements, all models are evaluated
using chronological backtests across multi-month historical records rather than random train/test splits.
A challenger model (LightGBM Quantile Regression) is promoted to Champion only if it demonstrates an out-of-sample
MAE improvement $\ge 3\%$ over the robust Seasonal Median Baseline.


## 2. Benchmark Evaluation Table


| Commodity & Market | Windows | Baseline MAE (₹/kg) | Baseline MAPE | Baseline 80% PICP | Challenger MAE (₹/kg) | Challenger MAPE | Challenger 80% PICP | $\Delta$ MAE | Designated Champion |
|---|---|---|---|---|---|---|---|---|---|
| `Banana @ Gobichettipalayam` | 39 | ₹1.29 | 5.45% | 96.0% | ₹1.16 | 4.89% | 58.2% | +9.8% | **LightGBM** |
| `Turmeric @ Erode` | 39 | ₹9.12 | 6.44% | 94.9% | ₹8.79 | 6.25% | 57.9% | +3.6% | **LightGBM** |

---

## 3. Methodology & Guardrails


1. **Rolling-Origin Windows**: Origin advances by 7-day increments. Training is restricted strictly to historical observations prior to origin.
2. **Quantile Coverage (PICP)**: Evaluates empirical coverage of the $[p_{10}, p_{90}]$ prediction interval. Expected coverage for well-calibrated intervals is $\approx 80\%$.
3. **Monotonicity Enforcement**: Quantile crossing is prevented by ensuring $p_{10} \le p_{50} \le p_{90}$ across all horizon steps.
4. **Operational Fallback**: When series observations are sparse ($< 30$ records) or stale ($> 7$ days), the API defaults automatically to the Baseline with expanded uncertainty bounds.
5. **Bilingual Disclaimer**: Every forecast carries explicit Tamil and English disclaimers (`இது மதிப்பீடு மட்டுமே, கொள்முதல் அல்லது விற்பனை ஆலோசனை அல்ல`).
