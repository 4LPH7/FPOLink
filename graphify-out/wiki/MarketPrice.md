# MarketPrice

> God node · 24 connections · `backend/app/models/market_price.py`

**Community:** [Community 28](Community_28.md)

## Connections by Relation

### calls
- seed_data() `EXTRACTED`
- ._store_records() `EXTRACTED`
- test_prices_and_crops_api() `EXTRACTED`

### contains
- market_price.py `EXTRACTED`

### imports
- models/__init__.py `EXTRACTED`
- db_bot_services.py `EXTRACTED`
- test_db_bot_services.py `EXTRACTED`
- test_source_safety.py `EXTRACTED`
- seed.py `EXTRACTED`
- services/prices.py `EXTRACTED`
- ingestion.py `EXTRACTED`
- test_ingestion.py `EXTRACTED`
- test_prices_api.py `EXTRACTED`

### inherits
- Base `EXTRACTED`

### uses
- [DbBotServices](DbBotServices.md) `INFERRED`
- IngestionService `INFERRED`
- get_latest_prices() `INFERRED`
- test_latest_price_and_dashboard_whitelist_real_sources_only() `INFERRED`
- _get_price_on_date() `INFERRED`
- test_latest_price_and_staleness() `INFERRED`
- test_seed_script_prices_never_served_to_bot() `INFERRED`
- check_anomalies() `INFERRED`
- get_price_history() `INFERRED`
- test_ingestion_and_deduplication() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*