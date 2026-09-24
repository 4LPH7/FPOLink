# Phase 11 — Agricultural Intelligence (v0.7): CONTEXT.md

> Strategic Architecture Contract for FPOLink TN Version 0.7.
> Transitions FPOLink from a data layer network (v0.6) into an active **Agricultural Intelligence Platform** with multi-market price forecasting, automated feature engineering, inter-district price arbitrage, and actionable harvest/selling signals.

---

## 1. Vision & Roadmap Positioning

```text
                         FPOLink TN

v0.1  Erode FPO Pilot                         [COMPLETED]
          │
          ▼
v0.5  Statewide Platform Foundation            [COMPLETED & SIGNED OFF]
          │
          ▼
v0.6  Statewide Data Network (Phase 9)        [COMPLETED & SIGNED OFF]
          │
          ├──► v0.7 Agricultural Intelligence (Phase 11)   ← ACTIVE PHASE
          │
          ├──► v0.8 Supply + Demand Network (Phases 13-15)
          │
          ├──► v0.9 State Command Center (Phases 16-17)
          │
          └──► v1.0 Statewide Intelligence Platform (Phases 18-20)
```

### The Core Paradigm Shift
- **v0.5 solved architecture:** (Geography hierarchy, canonical ontology, multi-tenant RBAC, quality scoring skeleton, API v1 routing).
- **v0.6 solved data:** (Complete 38-district market registry, source mappings, raw replay, data lineage, Ingestion Center).
- **v0.7 solves intelligence:** (Automated feature extraction, LightGBM quantile regression + seasonal baseline forecasting, inter-district price arbitrage, transport net margin calculations, and actionable farmer selling signals).

### The Golden Rule of v0.7
> [!IMPORTANT]
> **"Never output an unexplainable point prediction. Agricultural decisions require confidence bounds and net economics."**
> Forecasts must always provide $\text{p10} - \text{p90}$ uncertainty intervals, and inter-market price comparisons must deduct estimated transport costs to reflect true realized return.

---

## 2. Locked Architectural Decisions

### D1: Dual-Engine Forecasting Architecture (LightGBM Quantile Regression + Robust Baseline)
- **Primary Engine:** LightGBM Quantile Regression with three quantile objectives ($\alpha \in \{0.10, 0.50, 0.90\}$) to provide point forecasts ($\text{p50}$) and uncertainty confidence intervals ($\text{p10}, \text{p90}$).
- **Fallback Engine:** Empirical Seasonal Naive / Rolling Window Median for sparse commodity-market series ($< 30$ historical observations), ensuring predictions never fail or return errors for newer or seasonal mandis.
- **Explainable Signals:**
  - `signal = "hold"` if $\text{predicted}_{\text{p50}} > \text{current} \times 1.05$
  - `signal = "sell"` if $\text{predicted}_{\text{p50}} < \text{current} \times 0.95$
  - `signal = "neutral"` otherwise

### D2: Unified Agricultural Feature Store (`backend/app/ml/features.py`)
- Standardized tabular feature vectors computed on the fly or pre-materialized:
  - **Price Lags:** $t-1, t-2, t-3, t-7, t-14, t-30$ days modal prices.
  - **Rolling Statistics:** 7-day, 14-day, 30-day moving averages, standard deviation (volatility), and min/max price spread.
  - **Arrival Volume Momentum:** 7-day rolling arrival volume and ratio of current volume to 7-day baseline ($A_t / \bar{A}_{7d}$).
  - **Tamil Calendar & Festivals:** `is_festival`, `days_to_nearest_festival` (Pongal, Puthandu, Deepavali, etc.).
  - **Agro-Climatic Features:** 7-day forecast rainfall (mm), max/min temperature from Open-Meteo, indexed by market district coordinates.
  - **Data Quality Weighting:** Ingestion `quality_score` down-weights noisy or outlier observations during model training.

### D3: Inter-District Arbitrage & Net Realized Margin Engine (`backend/app/services/arbitrage.py`)
- Calculates price differences across markets for identical commodities.
- Evaluates Haversine geographical distance between mandis using validated GPS coordinates from the Market Master.
- Incorporates dynamic transport rate estimation ($\text{cost} = \text{base\_cost} + \text{rate\_per\_km\_quintal} \times \text{distance}$).
- Surfaces **Net Price Advantage**:
  $$\text{Net Spread} = \text{ModalPrice}_{\text{target}} - \text{ModalPrice}_{\text{origin}} - \text{TransportCost}$$

### D4: Model Versioning & Provenance Tracking
- Every trained model artifact and inference run is tracked in Postgres:
  - `ModelVersion`: Name, model type, evaluation metrics (MASE, MAE, RMSE), feature set hash, file path, active state.
  - `Prediction`: Target date, predicted price, lower bound, upper bound, confidence, signal, linked `model_version_id`.
  - `ForecastLog`: Daily automated backtest evaluation recording actual vs predicted prices when realized.

### D5: Scheduled Autonomous Intelligence Worker
- Dedicated daily job in APScheduler (`backend/app/worker.py`):
  - Ingestion run executes at 06:00 IST.
  - Prediction pipeline executes at 07:00 IST for active commodity-market pairs.
  - WhatsApp daily digest & price move alerts execute at 07:30–07:45 IST leveraging fresh forecasts.

---

## 3. Scope Boundaries

### In Scope (Phase 11)
1. Agricultural Feature Store engine (`backend/app/ml/features.py`).
2. Dual forecasting engine (LightGBM quantile regression + seasonal baseline).
3. Prediction persistence, evaluation logging, and model versioning.
4. Inter-district price arbitrage & transport cost calculation engine.
5. REST API v1 endpoints (`/api/v1/intelligence/*`).
6. Background worker automation for scheduled forecast generation.
7. Frontend Price & Intelligence Dashboard updates with confidence bands and arbitrage tables.
8. Comprehensive test suite (`test_agricultural_intelligence.py`) and Checkpoint G sign-off.

### Deferred to Phase 13–15 (v0.8)
- Individual farmer acreage tracking and farm-level yield forecasts.
- Buyer purchase requirement bidding and automated matchmaking engine.
- Supply aggregation heatmaps across community blocks and taluks.
