# FPOLink TN

**Tamil Nadu Agricultural Intelligence Platform & FPO Operating System**

A self-hostable, open-source platform for Farmer Producer Organizations (FPOs), district administrators, and state agricultural departments, with up-to-date mandi price intelligence, harvest aggregation, demand forecasting, multi-tenant governance, and automated farmer communication via Telegram and WhatsApp — designed for all 38 districts of Tamil Nadu.

[![CI](https://github.com/4LPH7/FPOLink/actions/workflows/ci.yml/badge.svg)](https://github.com/4LPH7/FPOLink/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791.svg)](https://www.postgresql.org)

---

## Architecture Overview

```text
                           STATE / DISTRICT / FPO ADMINS
                                         │
                                ┌────────▼────────┐
                                │  Web Dashboard  │
                                │  (Next.js PWA)  │
                                └────────┬────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
           Statewide Intel       Harvest & Members        Multi-Tenant RBAC
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         │
                               FastAPI Backend (v1)
                                         │
             ┌───────────────────────────┼───────────────────────────┐
             │                           │                           │
       PostgreSQL 16             APScheduler Worker            Notifications
    (31 Relational Tables)      (Container Isolation)      (Telegram & WhatsApp)
             │                           │                           │
    Statewide Foundation:       Ingestion & Quality:        At-Least-Once Sweeper:
    ├── 38 Revenue Districts    ├── OGD India Mandi Feed    ├── Telegram (Active Default)
    ├── 46 Regulated Markets    ├── CEDA Ashoka Mandi Feed  ├── Daily Price Digests
    ├── Canonical Crop Ontology ├── Source Mapping Layer    ├── Harvest Submissions
    ├── Pilot Taluk/Village Data ├── Raw Replay & Lineage   └── Price-Move Alerts
    └── Tamper-Evident Audit    └── Explainable QA (0–100)      (WhatsApp: Dormant)
```

---

## Key Modules & Implementation Status

| Module | Description | Verification Status |
|---|---|---|
| **Administrative Geography** | 5-tier relational schema (State, 38 Districts, Taluks, Blocks, Villages); 38 districts & 46 mandis reference-seeded; pilot taluks | **Implemented & Seeded** |
| **Agricultural Crop Ontology** | Canonical crop catalog with botanical classifications, Tamil names, and aliases | **Implemented & Seeded** |
| **Market Master Registry** | Normalized mandi master registry with geo-coordinates and regional aliases | **Implemented & Seeded** |
| **Source Mapping Layer** | Deterministic Stage 0 mapping (OGD, Agmarknet, CEDA) with confidence scoring | **Implemented & Tested** |
| **Raw Persistence & Replay** | Immutable raw packet storage with SHA-256 deduplication and offline replay harness | **Implemented & Tested** |
| **End-to-End Data Lineage** | Complete provenance tracking (`MarketPrice` -> `IngestionRun` -> `RawIngest`) | **Implemented & Tested** |
| **Commodity Registry UI** | Staff UI (`/admin/commodities`) to browse botanical cultivars, aliases & mappings | **Cloud Deployed** |
| **Ingestion Center Console** | Telemetry dashboard (`/admin`) tracking 38-district reporting freshness & runs | **Cloud Deployed** |
| **Multi-Tenant RBAC & Audit** | 9 discrete roles (`STATE_ADMIN`, `DISTRICT_ADMIN`, `FPO_ADMIN`, etc.) with strict tenant isolation and audit logging | **Implemented & Tested** |
| **Data Quality Engine** | Explainable scoring (0–100) based on Freshness, Source, Match, and Completeness | **Implemented & Tested** |
| **Mandi Price Ingestion** | Daily price feeds from data.gov.in (OGD), CEDA Ashoka, and manual mandi quotes; automated refreshes with stale warnings | **Implemented & Tested** |
| **Agricultural Feature Store** | 26 leak-free tabular features (lags, rolling stats, arrival momentum, Tamil festival flags) | **Implemented & Tested** |
| **Dual Forecasting Engine (v0.7 & M2)** | LightGBM quantile regression (p10/p50/p90) + Seasonal Naive & Median baselines with rolling-origin backtesting, automated champion promotion (≥3% MAE gain), nightly scoring, and bilingual disclaimers | **Implemented & Verified** |
| **Defensible Arbitrage Engine (M3)** | Inter-district net realization with commercial vehicle profiles (Pickup, LCV, Truck), commodity spoilage defaults, itemized deductions, like-for-like variety matching, and multi-factor uncertainty ratings | **Implemented & Verified** |
| **FPO Action Workspace** | Mobile-first operational cockpit (`/`) answering what is for sale, pending confirmations, matching buyers, and urgent tasks | **Cloud Deployed & Pilot** |
| **Prices & Intelligence UI** | 38-district selector, Recharts 7-day quantile confidence bands, interactive vehicle switcher, cost deduction sliders, and arbitrage matrix (`/prices`) with provenance badges | **Cloud Deployed** |
| **Demand & Matching Console** | 5-factor semi-automatic candidate ranking and 1-click staff confirmation (`/matching`, `/buyers`) | **Cloud Deployed & Pilot** |
| **FPO Operations Board** | Tenant-scoped task management with due dates, priorities, categories, and overdue tracking (`/tasks`) | **Cloud Deployed** |
| **Telegram Conversational Bot** | Free-tier conversational bot (`/telegram`) for farmer onboarding, price lookups, and harvest submission | **Cloud Deployed** |
| **WhatsApp Conversational Bot** | Meta Cloud API v23.0 integration with interactive buttons; dormant by default until Meta credentials are set | **Implemented (Dormant)** |
| **DPDP Act 2023 Compliance** | Digital Personal Data Protection Act compliance, consent ledger, 7-day raw purge | **Implemented & Tested** |
| **Zero-Cost Production Stack** | Cloudflare Tunnel sidecar + Oracle Cloud Always Free VM or Render + Vercel deployment | **Documented & Tested** |

---

## Tech Stack

| Layer | Technologies | Rationale |
|---|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, Tailwind CSS, shadcn/ui | High performance, responsive PWA, bilingual support (Tamil/English) |
| **Backend API** | FastAPI, Pydantic v2, Python 3.11 | Asynchronous capability, automated OpenAPI v3 documentation |
| **Database** | PostgreSQL 16 (`psycopg` 3 native driver), SQLAlchemy 2.0 | Transactional integrity, UUID primary keys, JSONB for telemetry |
| **Migrations** | Alembic | Strict, version-controlled schema migrations (`0001` through `0013`) |
| **Security & Auth** | `pwdlib[argon2]`, `PyJWT` | OWASP-recommended password hashing, scoped tenant auth, mandatory password rotation |
| **Background Worker** | APScheduler | Dedicated worker container for mandi ingestion and broadcast digests |
| **Quality & Anomaly** | Custom QA Scoring (0–100), Median Absolute Deviation (MAD) | Outlier detection robust against agricultural price volatility |
| **Messaging (Active)** | Telegram Bot API (via webhook/polling) | Zero-cost active conversational channel on Render/free tier |
| **Messaging (Optional)** | Meta WhatsApp Cloud API (Graph API v23.0) | Optional enterprise channel; disabled by default (`WHATSAPP_ENABLED=false`) |
| **Containerization** | Docker Engine & Docker Compose | Uniform local development and reproducible server deployments |

---

## Documentation Index

- [**Quickstart Guide**](docs/QUICKSTART.md) — Step-by-step setup from git clone to first API call.
- [**Forecast Backtest & Validation Report**](docs/FORECAST_BACKTEST.md) — Rolling-origin walk-forward evaluation, LightGBM vs. baseline benchmark tables, and promotion decisions.
- [**Arbitrage & Transport Realization Spec**](docs/ARBITRAGE_SPEC.md) — Mathematical cost equations, commercial vehicle presets, and uncertainty scoring rubrics.
- [**Statewide Foundation (v0.5 Architecture)**](docs/STATEWIDE_FOUNDATION.md) — Detailed architecture for statewide multi-tenancy, ontology, and quality scoring.
- [**Production Hosting Runbook**](docs/HOSTING.md) — Free-tier deployment on Oracle Cloud VM with Cloudflare Tunnel.
- [**Operations Runbook**](docs/OPS_RUNBOOK.md) — Incident response, kill-switch procedures, and log inspection.
- [**Meta Production Checklist**](docs/META_PRODUCTION_CHECKLIST.md) — Pre-flight requirements for WhatsApp Cloud API.
- [**Data Provenance & Isolation**](docs/data-provenance.md) — Verification ledger guaranteeing synthetic data isolation.
- [**Pilot Runbook**](docs/PILOT_RUNBOOK.md) — Operational guide for onboarding pilot farmers and staff.

---

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/4LPH7/FPOLink.git
cd FPOLink
cp .env.example .env
```

Review key configuration variables in `.env`:
- `DEFAULT_CROPS=turmeric,banana,coconut`
- `DEFAULT_DISTRICT=Erode`
- `POSTGRES_PORT=5432` *(use 5433 if port 5432 is occupied on the host)*
- `SEED_ADMIN_PASSWORD` — Choose a unique password for the development seed account; never reuse it in production.

### 2. Launch Stack with Docker Compose
```bash
docker compose up -d --build
```

Verify that all 4 containers are running and healthy:
```bash
docker compose ps
```
- `fpolink-postgres-1` (healthy on port 5432/5433)
- `fpolink-backend-1` (running on port 8000)
- `fpolink-worker-1` (running background cron jobs)
- `fpolink-frontend-1` (running on port 3000)

### 3. Seed Reference Data
Apply the initial baseline seed and the statewide platform reference seed:
```bash
# Baseline pilot data (Admin user, pilot FPO, initial crops, demo farmers)
docker compose exec backend python scripts/seed.py

# Statewide reference foundation (38 Districts, pilot taluks, 20 Tier-A crops, regulated mandis, telemetry)
docker compose exec backend python scripts/seed_statewide_foundation.py
```

Both seed scripts are **100% idempotent** and safe to execute repeatedly without duplicating records.

### 4. Create the First Admin
To bootstrap an administrator account in any environment (`development`, `staging`, or `production`):

```bash
# Set credentials in environment variables (never commit secrets to version control)
export ADMIN_PHONE="8072845239"
export ADMIN_PASSWORD="ChooseAStrongPassword@123"
export ADMIN_NAME="Chief Administrator"         # optional, defaults to "Admin"
export ADMIN_FPO_NAME="Erode Farmers Collective" # optional, defaults to "Erode Farmers Collective"

# Execute the admin creation script:
python backend/scripts/create_admin.py
```

On Windows PowerShell:
```powershell
$env:ADMIN_PHONE = "8072845239"
$env:ADMIN_PASSWORD = "ChooseAStrongPassword@123"
python backend\scripts\create_admin.py
```

Or via Docker Compose:
```bash
docker compose exec -e ADMIN_PHONE="8072845239" -e ADMIN_PASSWORD="StrongPassword@123" backend python scripts/create_admin.py
```

- **Idempotent**: If the admin phone already exists, it securely updates credentials and links.
- **Argon2id Hashing**: Uses the application's built-in OWASP-compliant password hashing; plain-text passwords are never logged or stored.
- **Auto-FPO Provisioning**: Creates and links an initial FPO if none exists.
- **Login Identifier**: Authentication at `/api/auth/login` uses the administrator's `phone` and `password`.

---

## Service Endpoints

| Service | Address | Description |
|---|---|---|
| **Frontend Dashboard** | `http://localhost:3000` | Staff and FPO web dashboard |
| **Backend API** | `http://localhost:8000` | FastAPI application server |
| **API Documentation** | `http://localhost:8000/docs` | Interactive Swagger UI |
| **System Health Check** | `http://localhost:8000/api/health` | Service and database probe |
| **PostgreSQL Database** | `localhost:5432` (or `5433`) | Relational database engine |

---

## API v1 Routing Matrix

FPOLink provides a unified `/api/v1/` route hierarchy alongside legacy `/api/` endpoints:

| Domain | Method | Endpoint | Description |
|---|---|---|---|
| **Geography** | `GET` | `/api/v1/geography/states` | List states (`Tamil Nadu`) |
| **Geography** | `GET` | `/api/v1/geography/districts` | List all 38 revenue districts of Tamil Nadu |
| **Geography** | `GET` | `/api/v1/geography/taluks` | Filter taluks by `district_id` |
| **Crops** | `GET` | `/api/v1/crops` | List canonical agricultural crops |
| **Crops** | `POST` | `/api/v1/crops/resolve` | Resolve raw/regional strings to canonical `Crop` |
| **Markets** | `GET` | `/api/v1/markets` | List registered regulated mandis |
| **Markets** | `POST` | `/api/v1/markets/resolve` | Resolve raw mandi strings to canonical `Market` |
| **Prices** | `GET` | `/api/v1/prices/latest` | Latest verified prices with quality scores |
| **Prices** | `GET` | `/api/v1/prices/history` | Historical price series with quality metrics |
| **Prices** | `GET` | `/api/v1/prices/quality-summary` | Aggregated data quality telemetry summary |
| **Farmers** | `GET` | `/api/v1/farmers/{fpo_id}` | Scoped farmer directory for an FPO |
| **Farmers** | `POST` | `/api/v1/farmers/{fpo_id}` | Register farmer with DPDP consent |
| **FPOs** | `GET` | `/api/v1/fpos/` | List registered Producer Organizations |
| **Audit** | `GET` | `/api/v1/audit/logs` | Tamper-evident administrative audit trail |

---

## Database Schema & Migrations

The platform database schema is managed via Alembic:

| Migration | Scope |
|---|---|
| `0001_initial_schema` | Core entities: Users, Crops, Varieties, Markets, MarketPrices, FPOs, Farmers, Harvests, Buyers |
| `0002_user_auth_fields` | Enhanced user authentication fields and consent flags |
| `0003_raw_ingest_payload` | Raw ingestion payload tracking for replayability |
| `0004_dpdp_consent` | DPDP Act 2023 compliance tracking and data retention flags |
| `0005_message_status_tracking` | WhatsApp outbound message status lifecycle and sweep tracking |
| `0006_statewide_foundation` | Relational geography hierarchy: `states`, `districts`, `taluks`, `blocks`, `villages` |
| `0007_crop_market_ontology` | Crop ontology fields, `crop_aliases`, `varieties`, `variety_aliases`, `market_aliases` |
| `0008_multitenant_rbac_audit` | 9 user roles, multi-tenant `fpo_id`/`district_id` scoping, and `audit_logs` |
| `0009_statewide_ingestion_quality` | Data quality telemetry (`data_sources`, `ingestion_runs`, `data_quality_events`), quality scores |
| `0010_source_mappings_markets` | Source-to-canonical mappings and market expansion |
| `0011_supply_demand_network` | Farm plots, buyer requirements, and supply matches |
| `0012_required_password_rotation` | Required password rotation for existing privileged accounts |
| `0013_fpo_tasks` | FPO-scoped operations to-do task board with roles and audit tracking |

To check migration status:
```bash
docker compose exec backend alembic current
docker compose exec backend alembic check
```

---

## What Works Today

FPOLink has verified end-to-end user workflows tested via automated integration and regression suites (264+ automated tests):

### 1. Verified Workflows
- **Administrator Bootstrap & Security Governance**:
  - Secure CLI admin bootstrapping via `python backend/scripts/create_admin.py` with Argon2id password hashing.
  - Strict JWT authentication boundary requiring immediate password rotation (`/change-password`) on first login before privileged tokens are issued.
  - Strict tenant isolation verified across all 9 roles: cross-FPO data mutation, unauthorized farmer access, and cross-district administrative leakage are completely blocked at the database layer.
- **Farmer Onboarding & DPDP Consent Ledger**:
  - Farmer enrollment capturing phone, acreages, language preference, and explicit DPDP Act 2023 consent records (`/farmers`).
- **Mandi Price Ingestion & Explainable Quality Scoring**:
  - Automated ingestion from official mandi portals (OGD India, CEDA Ashoka) with deterministic canonical entity resolution (`/api/v1/crops/resolve`, `/api/v1/markets/resolve`).
  - Explainable quality scoring (0–100) assessing freshness, canonical match confidence, source authority, and field completeness.
  - Full raw packet persistence (`raw_ingest_payloads`) ensuring complete provenance traceability and offline replayability.
- **Price Freshness, Stale Warnings & Demo Isolation**:
  - Every price record exposes its observation date, ingestion timestamp, raw source, unit, variety, and quality score.
  - Clear visual indicators distinguish **Fresh** ($\le 2$ days), **Stale** ($3\text{--}7$ days), **Outdated** ($> 7$ days), and **Demo Seed** records.
  - Ingestion outages display last-known observations with high-visibility stale warning banners—never disguising outdated data as fresh.
  - Demo seeds (`demo_seed`) are strictly banned from production farmer feeds, recommendations, and alert digests via startup checks and queries.
- **Defensible Machine Learning Forecasting (Phase M2)**:
  - Dual-engine architecture evaluating LightGBM quantile regression ($p_{10}, p_{50}, p_{90}$) against Seasonal Naive and Seasonal Median rolling baselines.
  - Strict walk-forward rolling-origin backtest CLI (`backend/scripts/backtest_forecaster.py`) evaluating MAE, RMSE, MAPE, and 80% prediction interval coverage across chronological splits.
  - Automated champion promotion rule requiring $\ge 3\%$ MAE improvement over baselines before ML models serve live inferences.
  - Continuous telemetry scoring (`score_past_forecasts`) running nightly in the background worker against realized ground-truth mandi prices.
  - Bilingual advisory disclaimers and input data freshness indicators protecting farmers from acting on cold-start or stale forecasts. See [docs/FORECAST_BACKTEST.md](docs/FORECAST_BACKTEST.md).
- **Defensible Inter-District Transport Arbitrage (Phase M3)**:
  - Inter-district net realization modeling accounting for commercial vehicle profiles (`pickup` 1.5T, `lcv` 3.5T default, `medium_truck` 10T, or custom capacity/mileage/fuel parameters).
  - Itemized deductions accounting for freight transport, labor/loading handling, APMC mandi commissions, and commodity-specific transit spoilage risk (e.g. 3.0% for banana, 1.0% for coconut, 0.0% for turmeric).
  - Like-for-like variety match indicator (`exact` vs. `cross_variety_approximate`) and observation date disparity tracking (`date_difference_days`).
  - Multi-factor uncertainty assessment (`low`, `moderate`, `high`) evaluating route distance, data latency, variety approximation, and margin cushion.
  - Interactive UI controls on `/prices` with commercial vehicle switcher, cost deduction sliders, itemized breakdown columns, and uncertainty tags.
  - Bilingual legal and advisory disclaimers (Tamil / English) explicitly clarifying that arbitrage estimates represent theoretical net margins subject to mandi cess, physical grade variance, and loading charges. See [docs/ARBITRAGE_SPEC.md](docs/ARBITRAGE_SPEC.md).
- **Harvest Aggregation & 1-Click Verification**:
  - Farmer-declared harvests logged via bot or web.
  - FPO staff verify submissions with 1 click from the action workspace, instantly locking them into pooled batches (`/`).
- **Commercial Demand & 5-Factor Supply Matching**:
  - Commercial buyer requirements registered with target grades, deadlines, and ceiling prices (`/buyers`).
  - 5-factor matching algorithm evaluates crop compatibility, geographic proximity (km), quantity fit ratio, harvest delivery timing, and minimum grade fit (`/matching`).
  - 1-click staff confirmation creates binding execution ledger entries.
- **FPO Action Workspace & Task Board**:
  - Single mobile-first home console (`/`) answering what is for sale, pending harvest confirmations, matching buyer orders, and urgent tasks.
  - Operational task tracker (`/tasks`) scoped to FPO staff with overdue deadlines.
- **Bilingual Conversational Interface**:
  - Zero-cost Telegram bot (`/telegram`) operating with Tamil and English menus for harvest logging and price inquiries.

### 2. Deployment Requirements
- **Compute**: Minimum 1 vCPU, 1 GB RAM (runs on Oracle Cloud Always Free VM or Render Free Tier).
- **Database**: PostgreSQL 16+ with UUID extensions (SQLite supported for rapid local testing).
- **Environment**: Node.js 18+ (frontend Next.js 14) and Python 3.11+ (FastAPI backend).

### 3. Known Pilot Limitations & Boundaries
- **Messaging Channel**: Telegram is the active default channel for cloud deployments. Meta WhatsApp Cloud API is fully implemented but requires enterprise Meta business verification and webhook setup (`WHATSAPP_ENABLED=true`).
- **Forecast Cold Starts**: Quantile forecasting models require at least 180 daily historical observations per crop-mandi pair. Rolling 14-day baselines are automatically used when observations are sparse.
- **Geography Coverage**: The relational schema supports the full 5-tier statewide administrative hierarchy (State -> 38 Districts -> Taluks -> Blocks -> Villages). Reference seed files populate all 38 revenue districts, 46 regulated markets, and 20 Tier-A crops; taluks and villages are currently populated for pilot agricultural clusters (Erode, Salem, Coimbatore).

---

## Testing & Quality Assurance

The test suite covers unit tests, integration tests, contract tests, security tenant isolation, and complete user journeys.

Execute the full regression test suite inside the container or virtual environment:
```bash
# Inside Docker
docker compose exec backend pytest -v --tb=short

# Or locally
pytest -v backend/tests
```

The CI workflow applies migrations, seeds required reference data, runs the PostgreSQL-backed suite (264+ tests), checks Ruff lint and formatting, builds the Next.js frontend, and exercises Docker health and authentication.

---

## Data Provenance & Live Data Verification

> [!IMPORTANT]
> A source label alone does not verify that a price came from a live provider. The development seed creates synthetic examples marked `demo_seed`; staging ingestion freshness, coverage, and farmer-facing isolation still need a live deployment check.
> - **Provider records** may be tagged `ogd`, `agmarknet`, or `ceda`; verify their ingestion run and raw lineage before treating them as current market observations.
> - **Development examples** are tagged `demo_seed` and must not be presented as verified market prices. In production (`ENVIRONMENT="production"`), synthetic records are rejected automatically at startup.
> - See [docs/data-provenance.md](docs/data-provenance.md) for the intended source and fixture handling.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

## Free Deployment (Render + Vercel)

**Backend (Render):** New → Blueprint → select this repo. `render.yaml` creates the
`fpolink-api` web service and a free PostgreSQL database. In the dashboard set:
- `TELEGRAM_BOT_TOKEN` – token from @BotFather (secret, never commit)
- `CORS_ORIGIN_REGEX` – `^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$` (tightly restricts access to official preview and production deployments, preventing unauthorized third-party origins)

Migrations run on every start (`alembic upgrade head`). Demo data: open the Render shell and run
`python scripts/seed_statewide_foundation.py` (prices tagged `demo_seed` are only served while `DEMO_MODE=true`).

**Frontend (Vercel):** Import repo, Root Directory `frontend`, env var
`API_INTERNAL_URL=https://<your-render-service>.onrender.com`. `/api/*` is proxied to the backend.

**Messaging:**
- **Telegram (Active)**: See `docs/TELEGRAM_SETUP.md`. Works immediately on free-tier deployments.
- **WhatsApp (Optional)**: Disabled by default (`WHATSAPP_ENABLED=false`). Enable by configuring Meta Cloud API credentials in `.env`.

**Local Dev:** `DATABASE_URL=sqlite:///./fpolink.db` works for quick runs; PostgreSQL 16 in production.

**Operational Modules & Interfaces:**
- `/` – Mobile-friendly FPO Action Workspace (Today's Work, Ready Supply, Buyer Matches, Market Freshness).
- `/tasks` – FPO-scoped operations to-do task board.
- `/matching` – 5-factor semi-automatic supply-demand matching console.
- `/buyers` – Commercial buyer directory and procurement requirement board.
- `/prices` – 38-district mandi price feed with data provenance, quantile bands, and defensible arbitrage matrix.
- `/telegram` – Free-tier conversational bot integration for farmers.

**Operational Scripts & CLIs:**
- `python backend/scripts/backtest_forecaster.py` – Walk-forward rolling-origin forecast model backtesting, baseline comparisons, and promotion evaluation.
- `python backend/scripts/evaluate_arbitrage.py` – CLI evaluation of inter-district transport arbitrage across commodities and vehicle profiles.
- `python backend/scripts/create_admin.py` – Bootstraps initial administrator account with mandatory password change enforcement.
- `python backend/scripts/seed_statewide_foundation.py` – Seeds 38 Tamil Nadu districts, regulated mandis, and commodity ontologies.
