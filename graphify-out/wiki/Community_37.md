# Community 37

> 13 nodes · cohesion 0.19

## Key Concepts

- **worker.py** (10 connections) — `backend/app/worker.py`
- **main()** (4 connections) — `backend/app/worker.py`
- **run_predictions()** (3 connections) — `backend/app/worker.py`
- **run_price_ingestion()** (3 connections) — `backend/app/worker.py`
- **run_weather_ingestion()** (3 connections) — `backend/app/worker.py`
- **apscheduler_schedulers_blocking** (1 connections)
- **FPOLink TN — Background Worker Runs scheduled tasks in a separate container.…** (1 connections) — `backend/app/worker.py`
- **Fetch daily prices from configured data sources.** (1 connections) — `backend/app/worker.py`
- **# TODO: Import and call ingestion service** (1 connections) — `backend/app/worker.py`
- **Fetch weather data from Open-Meteo / NASA POWER.** (1 connections) — `backend/app/worker.py`
- **# TODO: Import and call weather service** (1 connections) — `backend/app/worker.py`
- **Generate price forecasts using the active model.** (1 connections) — `backend/app/worker.py`
- **# TODO: Import and call prediction service** (1 connections) — `backend/app/worker.py`

## Relationships

- [Community 9](Community_9.md) (1 shared connections)

## Source Files

- `backend/app/worker.py`

## Audit Trail

- EXTRACTED: 13 (81%)
- INFERRED: 3 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*