# FPOLink TN

**Tamil Nadu Agricultural Intelligence Platform & FPO Operating System**

A self-hostable, production-ready, open-source platform that empowers Farmer Producer Organizations (FPOs), district administrators, and state agricultural departments with real-time price intelligence, harvest aggregation, demand forecasting, multi-tenant governance, and automated farmer communication via WhatsApp — spanning all 38 districts of Tamil Nadu.

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
    (31 Relational Tables)      (Container Isolation)      (WhatsApp Cloud API)
             │                           │                           │
    Statewide Foundation:       Ingestion & Quality:        At-Least-Once Sweeper:
    ├── 38 Revenue Districts    ├── OGD India Mandi Feed    ├── Interactive Menus
    ├── Taluk/Block/Village     ├── CEDA Ashoka Mandi Feed  ├── Daily Price Digest
    ├── Canonical Crop Ontology ├── Source Mapping Layer    └── Price-Move Alerts
    ├── Regulated Market Master ├── Raw Replay & Lineage
    └── Tamper-Evident Audit    └── Explainable QA (0–100)
```

---

## Key Modules

| Module | Description | Status |
|---|---|---|
| **Administrative Geography** | Full 5-tier relational hierarchy: State, 38 Districts, Taluks, Blocks, and Villages | **Active** |
| **Agricultural Crop Ontology** | Canonical crop catalog with botanical classifications, Tamil names, and aliases | **Active** |
| **Market Master Registry** | Normalized mandi master registry with geo-coordinates and regional aliases | **Active** |
| **Source Mapping Layer** | Deterministic Stage 0 mapping (OGD, Agmarknet, CEDA) with confidence scoring | **Active** |
| **Raw Persistence & Replay** | Immutable raw packet storage with SHA-256 deduplication and offline replay harness | **Active** |
| **End-to-End Data Lineage** | Complete provenance tracking (MarketPrice -> IngestionRun -> RawIngest) | **Active** |
| **Commodity Registry UI** | Staff UI (/admin/commodities) to browse botanical cultivars, aliases & mappings | **Active** |
| **Ingestion Center Console** | Telemetry dashboard (/admin) tracking 38-district reporting freshness & runs | **Active** |
| **Multi-Tenant RBAC & Audit** | 9 discrete roles (`STATE_ADMIN`, `DISTRICT_ADMIN`, `FPO_ADMIN`, etc.) with audit logging | **Active** |
| **Data Quality Engine** | Explainable scoring (0–100) based on Freshness, Source, Match, and Completeness | **Active** |
| **Mandi Price Ingestion** | Real-time adapters for data.gov.in (OGD), CEDA Ashoka, and manual mandi quotes | **Active** |
| **Agricultural Feature Store** | 26 leak-free tabular features (lags, rolling stats, arrival momentum, Tamil festival flags) | **Active** |
| **Dual Forecasting Engine (v0.7)** | LightGBM quantile regression (p10/p50/p90) + rolling baseline + actionable signals | **Active** |
| **Geospatial Arbitrage Engine** | Haversine distance matrix across mandis with freight deduction (₹50 + ₹1.20/km/qtl) | **Active** |
| **Prices & Intelligence UI** | 38-district selector, Recharts 7-day quantile confidence bands, and arbitrage matrix | **Active** |
| **Staff Web Dashboard** | Next.js 14 PWA, Tailwind CSS, shadcn/ui, Tamil typography, 30-day price trends | **Active** |
| **WhatsApp Conversational Bot** | Meta Cloud API v23.0, 3-button interactive menu, idempotent harvest logging | **Active** |
| **DPDP Act 2023 Compliance** | Digital Personal Data Protection Act compliance, consent ledger, 7-day raw purge | **Active** |
| **Zero-Cost Production Stack** | Cloudflare Tunnel sidecar + Oracle Cloud Always Free VM deployment guide | **Active** |

---

## Tech Stack

| Layer | Technologies | Rationale |
|---|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, Tailwind CSS, shadcn/ui | High performance, responsive PWA, bilingual support (Tamil/English) |
| **Backend API** | FastAPI, Pydantic v2, Python 3.11 | Asynchronous capability, automated OpenAPI v3 documentation |
| **Database** | PostgreSQL 16 (`psycopg` 3 native driver), SQLAlchemy 2.0 | Transactional integrity, UUID primary keys, JSONB for telemetry |
| **Migrations** | Alembic | Strict, version-controlled schema migrations (`0001` through `0010`) |
| **Security & Auth** | `pwdlib[argon2]`, `PyJWT` | OWASP-recommended password hashing and stateless JWT bearer tokens |
| **Background Worker** | APScheduler | Dedicated worker container for mandi ingestion and broadcast digests |
| **Quality & Anomaly** | Custom QA Scoring (0–100), Median Absolute Deviation (MAD) | Outlier detection robust against agricultural price volatility |
| **Messaging** | Meta WhatsApp Cloud API (Graph API v23.0) | Zero-cost official API integration, interactive quick-reply buttons |
| **Containerization** | Docker Engine & Docker Compose | Uniform local development and reproducible server deployments |

---

## Documentation Index

- [**Quickstart Guide**](docs/QUICKSTART.md) — Step-by-step setup from git clone to first API call.
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
- `SEED_ADMIN_PASSWORD=admin123`

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

To check migration status:
```bash
docker compose exec backend alembic current
docker compose exec backend alembic check
```

---

## Testing & Quality Assurance

The test suite covers unit tests, integration tests, contract tests, and compatibility shims.

Execute the full regression test suite inside the container:
```bash
docker compose exec backend pytest -v --tb=short
```

**Results:**
- **162 passing tests**
- 1 skipped test (production webhook verification requiring live Meta token)
- 0 failures

---

## Data Provenance & Real Data Guarantee

> [!IMPORTANT]
> FPOLink strictly distinguishes between verified agricultural observations and test fixtures:
> - **Real Ingestion Feeds**: Tagged as `ogd`, `agmarknet`, or `ceda`. These are verified, scored, and served to farmers.
> - **Synthetic / Test Data**: Tagged as `ceda_synthetic`, `seed_demo`, or `test`. They are blocked from reaching farmer notifications, WhatsApp digests, or production forecasting models.
> - See [docs/data-provenance.md](docs/data-provenance.md) for complete dataset isolation guarantees.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
