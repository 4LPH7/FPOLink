# FPOLink TN

**FPO Digital Operating System for Tamil Nadu**

A self-hostable, open-source platform that provides Farmer Producer Organizations (FPOs) with price intelligence, harvest aggregation, demand forecasting, and buyer matching — focused on Erode district and key Tamil Nadu crops.

---

## Architecture

```text
                    FPO ADMIN
                       │
              ┌────────▼────────┐
              │   Web Dashboard │
              │   (Next.js)     │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   Price Intel     Aggregation     Members
        │              │              │
        └──────────────┼──────────────┘
                       │
                 FastAPI Backend
                       │
       ┌───────────────┼────────────────┐
       │               │                │
   PostgreSQL       ML Engine       Notifications
       │               │                │
       │          Price Forecast      Telegram Bot
       │          Demand Forecast
       │          Anomaly Detection
       │
       ├── TN Agriculture Marketing data
       ├── AGMARKNET
       ├── FPO-entered data
       └── Open-Meteo weather data
```

## Modules

| Module | Description |
|--------|-------------|
| **FPO Dashboard** | Real-time stats, market prices, forecasts, alerts |
| **Farmer Management** | Member registration, farm tracking, harvest submissions |
| **Market Intelligence** | Price ingestion from TN Agri Marketing + AGMARKNET, trend analysis |
| **Harvest Aggregation** | Aggregate individual harvests into bulk batches |
| **Price Prediction** | ML-based price forecasting with confidence intervals |
| **Buyer Module** | Buyer directory, purchase requirements, supply matching |
| **Telegram Bot** | Low-tech interface for farmers — price lookups, harvest submission |

## Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Frontend | Next.js + Tailwind CSS | Free |
| Backend | FastAPI (Python) | Free |
| Database | PostgreSQL 16 | Free |
| ORM | SQLAlchemy + Alembic | Free |
| Auth | JWT (python-jose) | Free |
| ML | scikit-learn + XGBoost | Free |
| Charts | Recharts | Free |
| Maps | OpenStreetMap + Leaflet | Free |
| Weather | Open-Meteo API | Free |
| Market Data | TN Agri Marketing + AGMARKNET | Free/Public |
| Notifications | Telegram Bot API | Free |
| Containers | Docker Compose | Free |

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- Git

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/fpolink.git
cd fpolink

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker compose up -d

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Seed initial data
docker compose exec backend python scripts/seed.py
```

### Access

| Service | URL |
|---------|-----|
| Frontend (Dashboard) | http://localhost:3000 |
| Backend (API) | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### Default Login

| Role | Phone | Password |
|------|-------|----------|
| Admin | 9999900000 | admin123 |

## Project Structure

```text
fpolink/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   ├── data_sources/  # Market data adapters
│   │   ├── ml/        # ML model integration
│   │   └── notifications/ # Telegram/notification logic
│   ├── alembic/       # Database migrations
│   ├── scripts/       # Seed data, utilities
│   └── Dockerfile
├── frontend/          # Next.js dashboard
│   ├── app/           # App router pages
│   ├── components/    # Reusable UI components
│   └── lib/           # Utilities, i18n, API client
├── ml/                # ML training & inference
│   ├── datasets/      # Training data
│   ├── notebooks/     # Jupyter notebooks
│   ├── training/      # Model training scripts
│   ├── models/        # Saved model artifacts
│   └── inference/     # Prediction pipeline
├── bot/               # Telegram bot
│   └── handlers/      # Bot command handlers
├── config/            # Project configuration (YAML)
├── database/          # DB init scripts
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration

Edit `config/fpolink.yaml` to configure:

- **Geography**: State, districts, markets (default: Erode, Tamil Nadu)
- **Crops**: Tracked commodities with Tamil names (default: turmeric, banana, coconut)
- **Data Sources**: Enable/disable TN Agri, AGMARKNET, Open-Meteo
- **Scheduler**: Cron schedules for data ingestion and predictions

## Language Support

The UI supports **English** and **Tamil (தமிழ்)**. Translation files are in `frontend/lib/i18n/`.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

> **Note**: This is decision-support software. Price forecasts and demand estimates are model-generated and should not be treated as guaranteed agricultural advice.
