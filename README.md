# FPOLink TN

**FPO Digital Operating System for Tamil Nadu**

A self-hostable, open-source platform that provides Farmer Producer Organizations (FPOs) with price intelligence, harvest aggregation, demand forecasting, and buyer matching — focused on Erode district and key Tamil Nadu crops.

[![CI](https://github.com/4LPH7/FPOLink/actions/workflows/ci.yml/badge.svg)](https://github.com/4LPH7/FPOLink/actions/workflows/ci.yml)

---

## Architecture

```text
                    FPO ADMIN / STAFF
                           │
                  ┌────────▼────────┐
                  │   Web Dashboard │
                  │   (Next.js PWA) │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       Price Intel    Aggregation      Members
            │              │              │
            └──────────────┼──────────────┘
                           │
                     FastAPI Backend
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
  PostgreSQL 16     Background Worker     Notifications
   (21 Tables)        (APScheduler)       (Telegram Bot)
       │                   │
       │              Daily ETL:
       │              ├── data.gov.in (OGD)
       │              ├── CEDA Agri-Market (Ashoka Univ)
       │              ├── Open-Meteo & NASA POWER
       │              └── TN Festival Features
       │
   ML Forecasting
   ├── Baselines (Seasonal Naive)
   ├── statsforecast (ETS / ARIMA)
   └── LightGBM (Quantile intervals)
```

## Modules

| Module | Description | Status |
|---|---|---|
| **Auth & DPDP Consent** | Phone auth with Argon2id + PyJWT and DPDP Act consent tracking | **Active** |
| **Market Intelligence** | Daily mandi prices, normalized markets/varieties, MAD anomaly detection | **Active** |
| **FPO Management** | Organization registration, staff administration, member statistics | **Active** |
| **Farmer Directory** | Farmer registration, farm land tracking, bilingual preferences | **Active** |
| **Data Ingestion (ETL)** | CEDA historical backfill, OGD API, Open-Meteo & NASA POWER weather | **Active** |
| **Harvest Aggregation** | Aggregate individual farmer harvests into bulk batches | In Progress |
| **Telegram Bot** | Free verified phone authentication, price checks, alerts | Planned (W2) |
| **Price Forecasting** | Model ladder (statsforecast → LightGBM) with hold/sell ranges | Planned (W4) |
| **Buyer Module** | Purchase requirements and order matching | Deferred (v0.2) |

## Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| Frontend | Next.js (App Router) + Tailwind CSS | Fast, PWA support, Tamil i18n |
| Backend | FastAPI + SQLAlchemy 2.0 (async-ready) | High performance, auto OpenAPI docs |
| Database | PostgreSQL 16 (psycopg 3 driver) | Robust relational engine, JSONB support |
| Migrations | Alembic | Version-controlled schema migrations |
| Auth | `pwdlib[argon2]` + `PyJWT` | Actively maintained, OWASP recommended |
| Worker | Standalone APScheduler Container | Process isolation, prevents duplicate jobs |
| ML & Stats | `statsforecast`, `lightgbm`, `mapie` | Scalable forecasting with prediction intervals |
| Feature Eng | `holidays` + curated TN festival calendar | Seasonal demand & arrival indicators |
| Anomaly Detection | Median Absolute Deviation (MAD) | Robust against spiky agricultural price data |
| External Feeds | OGD API, CEDA bulk data, Open-Meteo | Zero mandatory paid APIs |
| Containers | Docker Compose | Reproducible development & deployment |

## Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose (recommended)
- Or **PostgreSQL 15+** if running standalone (PostgreSQL 15+ is strictly required for `NULLS NOT DISTINCT` unique constraints on variety-aware price dedup).
- Python 3.11+ / 3.12+
- Git

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/4LPH7/FPOLink.git
cd FPOLink

# 2. Copy environment file
cp .env.example .env

# 3. Start stack (PostgreSQL 16, Backend API, Scheduler Worker)
docker compose up -d --build postgres backend worker

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Seed initial reference data (Admin, Crops, Varieties, Markets, Prices)
# Optionally set SEED_ADMIN_PASSWORD in .env or pass as env var
docker compose exec backend python scripts/seed.py

# 6. (Optional) Check mandi price reporting coverage
docker compose exec backend python scripts/check_market_coverage.py --crop turmeric --district Erode
```

### Access

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Swagger Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |
| Frontend Dashboard | http://localhost:3000 (after Day 8) |
| PostgreSQL | localhost:5432 |

### Default Credentials (Development Only)

| Role | Phone | Password |
|---|---|---|
| Admin | `9999900000` | `admin123` (development only) |
| Farmer 1 | `9876543210` | `farmer123` |

> [!IMPORTANT]
> **Production Security Rules**:
> - If `ENVIRONMENT=production`, the application **strictly refuses to start** if `SECRET_KEY` remains the default `'change-me-in-production'`.
> - If `ENVIRONMENT=production`, `seed.py` **refuses to use any default admin password**. If `SEED_ADMIN_PASSWORD` is not set in the environment, a cryptographically secure 16-character password is generated, printed once to standard output, and never saved in plaintext.

## Data Sourcing: Real vs. Synthetic Fixtures

> [!NOTE]
> All files in `backend/tests/fixtures/*_synthetic.*` and `ml/datasets/*_synthetic.*` are **synthetic fixtures** crafted to model published government and academic schemas for deterministic unit testing. They must not be mistaken for verified ground-truth agricultural observations.
> See [docs/data-provenance.md](docs/data-provenance.md) for the complete provenance verification ledger, dataset isolation guarantees, and step-by-step instructions.

### Obtaining Real Mandi Data
1. **Daily Agmarknet Prices (Live Ingestion)**:
   - Register for a free developer account at [data.gov.in](https://data.gov.in/).
   - Obtain your user API key from your data.gov.in dashboard.
   - Configure `OGD_API_KEY=your_key_here` in your `.env` file.
   - The default Agmarknet mandi daily price resource is `9ef84268-d588-465a-a308-a864a43d0070`.
2. **Historical Training Data (CEDA Ashoka University)**:
   - Visit the official [CEDA Agri Market Data Portal](https://agrimarket.ceda.ashoka.edu.in/).
   - Filter by State: *Tamil Nadu*, District: *Erode*, Commodities: *Turmeric, Banana*.
   - Export the CSV file and place it in `ml/datasets/ceda_erode_turmeric.csv`.
   - Run the backfill script:
     ```bash
     python backend/scripts/backfill_ceda.py --csv-path ml/datasets/ceda_erode_turmeric.csv --crop turmeric --district Erode --source ceda
     ```
   - The ingestion service tags real extracts as `source='ceda'` and synthetic samples as `source='ceda_synthetic'` to guarantee that test/sample records never contaminate ML training series.

```text
fpolink/
├── .github/workflows/ci.yml # Automated CI (pytest, alembic check, ruff, docker smoke)
├── backend/
│   ├── alembic/             # Versioned schema migrations
│   │   └── versions/        # Migration scripts (0001_initial_schema.py)
│   ├── app/
│   │   ├── api/             # Routers: auth, prices, fpos, farmers, crops, admin
│   │   ├── data_sources/    # Adapters: CEDA, OGD, Open-Meteo, NASA POWER, holidays
│   │   ├── models/          # 21 SQLAlchemy models with single declarative base
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic: auth, prices, ingestion, weather
│   │   ├── utils/           # Unit conversions (Rs/quintal -> Rs/kg)
│   │   ├── config.py        # Settings with automatic postgresql+psycopg normalization
│   │   ├── database.py      # Engine and SessionLocal
│   │   ├── main.py          # FastAPI application entrypoint
│   │   └── worker.py        # Dedicated background scheduler process
│   ├── scripts/
│   │   ├── backfill_ceda.py # Historical data backfill script
│   │   └── seed.py          # Idempotent development database seeder
│   ├── tests/               # Pytest suite (auth, units, parsers, ingestion, APIs)
│   ├── Dockerfile
│   └── entrypoint.sh        # DB health wait check + alembic auto-upgrade
├── frontend/
│   └── lib/i18n/            # English (en.json) & Tamil (ta.json) translation dictionaries
├── config/fpolink.yaml      # Regional config (Erode, crops, data feeds)
├── database/init.sql        # Database initialization with UTF-8 and extensions
└── docker-compose.yml
```

## Language Support

The UI and messaging layers support **English** and **Tamil (தமிழ்)** from the ground up.

## License

MIT License — see [LICENSE](LICENSE) for details.
