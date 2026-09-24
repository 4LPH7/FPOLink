# FPOLink TN — Quickstart Guide

This guide walks you through setting up and running the entire FPOLink TN stack locally using Docker Compose, from cloning the repository to verifying your first successful API and dashboard requests.

---

## 1. Prerequisites

Ensure you have the following installed:
- **Docker Engine** (v24.0+) & **Docker Compose** (v2.20+)
- **Git**
- Optional (for local non-docker testing): Python 3.11+ / Node.js 20+

---

## 2. Step-by-Step Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/4LPH7/FPOLink.git
cd FPOLink
```

### Step 2: Configure Environment Variables
Copy the default environment template:
```bash
cp .env.example .env
```

Review the key settings in `.env`:
- `DEFAULT_CROPS=turmeric,banana,coconut` — Comma-separated list of target commodities.
- `POSTGRES_PORT=5432` — If your host already runs PostgreSQL locally, set `POSTGRES_PORT=5433` to prevent port collisions.
- `DATABASE_URL=postgresql+psycopg://fpolink:fpolink@postgres:5432/fpolink` — Internal connection string for backend container.
- `SEED_ADMIN_PASSWORD=admin123` — Initial administrative password for seed data.

### Step 3: Launch the Stack
Start all 4 services (PostgreSQL 16, FastAPI backend, APScheduler worker, and Next.js frontend):
```bash
docker compose up -d --build
```

Verify that all containers are healthy:
```bash
docker compose ps
```

You should see:
- `fpolink-postgres-1` (healthy on port `5432` or `5433`)
- `fpolink-backend-1` (running on port `8000`)
- `fpolink-worker-1` (running background cron jobs)
- `fpolink-frontend-1` (running on port `3000`)

### Step 4: Seed the Database
Populate initial reference data (admin user, crops, varieties, mandis, and demo farmers):
```bash
# 1. Baseline pilot data
docker compose exec backend python scripts/seed.py

# 2. Statewide platform reference foundation (38 districts, 20 crops, mandis, data sources)
docker compose exec backend python scripts/seed_statewide_foundation.py
```

Expected output includes:
- Admin user and pilot FPO created
- All 38 Tamil Nadu districts registered
- 25 Pilot Taluks created across Erode, Coimbatore, and Thanjavur
- 20 Tier-A commodities with Tamil and botanical names, 67 aliases, and 40 varieties
- 8 Regulated Mandis with geo-coordinates and aliases
- 5 Verified Ingestion Data Sources

---

## 3. Verify First Successful Requests

### 1. Backend Health Probe
```bash
curl -s http://localhost:8000/api/health
```
**Expected Response:**
```json
{"status":"ok","service":"fpolink-api","version":"0.1.0","db":"ok"}
```

### 2. Statewide Districts Probe (v1)
```bash
curl -s http://localhost:8000/api/v1/geography/districts
```
Returns all 38 districts of Tamil Nadu (Ariyalur through Virudhunagar).

### 3. Latest Verified Mandi Prices (v1)
```bash
curl -s "http://localhost:8000/api/v1/prices/latest?district=Erode"
```
Returns latest verified prices with explainable data quality scores.

### 2. Verified Crops Feed
```bash
curl -s http://localhost:8000/api/crops/
```
**Expected Response:**
```json
{
  "crops": [
    {"id":"...","name":"banana","tamil_name":"வாழைப்பழம்","category":"fruit","unit":"kg"},
    {"id":"...","name":"coconut","tamil_name":"தேங்காய்","category":"plantation","unit":"unit"},
    {"id":"...","name":"turmeric","tamil_name":"மஞ்சள்","category":"spice","unit":"kg"}
  ]
}
```

### 3. Staff Web Dashboard
Open your browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

- **Home**: View FPO membership, crop summary, and agricultural signals.
- **Prices (`/prices`)**: Inspect 30-day mandi price trends and hold/sell indicators.
- **Farmers (`/farmers`)**: Search member farmers and verify DPDP consent status.
- **Admin (`/admin`)**: Verify real-time backend and database operational health.
- **WhatsApp (`/whatsapp`)**: Monitor inbound webhook activity and access the emergency kill switch runbook.

---

## 4. Running the Automated Test Suite

To run the complete test suite inside the container environment:
```bash
docker compose exec backend pytest -v --tb=short
```

Expected result: **162 passed, 1 skipped, 0 failed** in ~10 seconds.

---

## 5. Troubleshooting & Useful Commands

| Action | Command |
|---|---|
| View backend live logs | `docker compose logs -f backend` |
| View worker scheduled jobs | `docker compose logs -f worker` |
| Restart backend / worker | `docker compose restart backend worker` |
| Run database migrations | `docker compose exec backend alembic upgrade head` |
| Reset database | `docker compose down -v && docker compose up -d` |
