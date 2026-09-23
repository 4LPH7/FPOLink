# Crop

> God node · 31 connections · `backend/app/models/crop.py`

**Community:** [Community 8](Community_8.md)

## Connections by Relation

### calls
- create_harvest() `EXTRACTED`
- seed_data() `EXTRACTED`
- test_ingestion_and_deduplication() `EXTRACTED`
- .submit_harvest() `EXTRACTED`
- test_prices_and_crops_api() `EXTRACTED`

### contains
- models/crop.py `EXTRACTED`

### imports
- test_whatsapp_harvest_flow.py `EXTRACTED`
- models/__init__.py `EXTRACTED`
- test_harvest_service_and_api.py `EXTRACTED`
- db_bot_services.py `EXTRACTED`
- test_db_bot_services.py `EXTRACTED`
- test_source_safety.py `EXTRACTED`
- seed.py `EXTRACTED`
- fpo_service.py `EXTRACTED`
- services/prices.py `EXTRACTED`
- harvest_service.py `EXTRACTED`
- ingestion.py `EXTRACTED`
- test_ingestion.py `EXTRACTED`
- crops.py `EXTRACTED`
- test_prices_api.py `EXTRACTED`

### inherits
- Base `EXTRACTED`

### uses
- [DbBotServices](DbBotServices.md) `INFERRED`
- IngestionService `INFERRED`
- get_latest_prices() `INFERRED`
- get_dashboard_stats() `INFERRED`
- test_db_bot_services_submit_harvest_persistence() `INFERRED`
- test_latest_price_and_dashboard_whitelist_real_sources_only() `INFERRED`
- test_latest_price_and_staleness() `INFERRED`
- seed_data() `INFERRED`
- test_seed_script_prices_never_served_to_bot() `INFERRED`
- list_crops() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*