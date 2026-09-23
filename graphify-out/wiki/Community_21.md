# Community 21

> 24 nodes · cohesion 0.09

## Key Concepts

- **WeatherProvider** (8 connections) — `backend/app/data_sources/weather.py`
- **WeatherService** (8 connections) — `backend/app/services/weather_service.py`
- **NASAPowerProvider** (6 connections) — `backend/app/data_sources/nasa_power.py`
- **.fetch_history()** (4 connections) — `backend/app/data_sources/nasa_power.py`
- **.fetch_history()** (4 connections) — `backend/app/data_sources/weather.py`
- **.backfill_history()** (4 connections) — `backend/app/services/weather_service.py`
- **.__init__()** (4 connections) — `backend/app/services/weather_service.py`
- **.fetch_forecast()** (3 connections) — `backend/app/data_sources/weather.py`
- **.ingest_forecast()** (3 connections) — `backend/app/services/weather_service.py`
- **Any** (2 connections)
- **Any** (1 connections)
- **date** (1 connections)
- **Fetch long-term weather history from NASA POWER.** (1 connections) — `backend/app/data_sources/nasa_power.py`
- **Fetch daily weather data from NASA POWER.** (1 connections) — `backend/app/data_sources/nasa_power.py`
- **date** (1 connections)
- **Fetch weather data from Open-Meteo API.** (1 connections) — `backend/app/data_sources/weather.py`
- **Fetch weather forecast for the next N days.** (1 connections) — `backend/app/data_sources/weather.py`
- **Fetch historical weather data.** (1 connections) — `backend/app/data_sources/weather.py`
- **.__init__()** (1 connections) — `backend/app/data_sources/weather.py`
- **date** (1 connections)
- **Session** (1 connections)
- **Manages weather data ingestion and retrieval.** (1 connections) — `backend/app/services/weather_service.py`
- **Fetch and store weather forecast.** (1 connections) — `backend/app/services/weather_service.py`
- **Backfill weather history from NASA POWER.** (1 connections) — `backend/app/services/weather_service.py`

## Relationships

- [Community 9](Community_9.md) (5 shared connections)
- [Community 15](Community_15.md) (3 shared connections)

## Source Files

- `backend/app/data_sources/nasa_power.py`
- `backend/app/data_sources/weather.py`
- `backend/app/services/weather_service.py`

## Audit Trail

- EXTRACTED: 31 (91%)
- INFERRED: 3 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*