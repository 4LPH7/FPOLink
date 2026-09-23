# PriceRecord

> God node · 35 connections · `backend/app/data_sources/base.py`

**Community:** [Community 30](Community_30.md)

## Connections by Relation

### calls
- test_ingestion_and_deduplication() `EXTRACTED`
- test_clean_price_records_validation() `EXTRACTED`

### contains
- data_sources/base.py `EXTRACTED`

### imports
- ingestion.py `EXTRACTED`
- registry.py `EXTRACTED`
- ceda.py `EXTRACTED`
- ceda_api.py `EXTRACTED`
- ogd.py `EXTRACTED`
- test_ingestion.py `EXTRACTED`
- data_cleaning.py `EXTRACTED`
- test_data_cleaning.py `EXTRACTED`
- manual.py `EXTRACTED`

### rationale_for
- Standardized price record from any data source. `EXTRACTED`

### references
- ._parse_row() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- ._parse_record() `EXTRACTED`
- ._store_records() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- ._resolve_market() `EXTRACTED`
- .create_manual_record() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- ._parse_api_item() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- .fetch_all() `EXTRACTED`
- .fetch_prices() `EXTRACTED`

### uses
- [CEDAProvider](CEDAProvider.md) `INFERRED`
- CEDAAPIProvider `INFERRED`
- IngestionService `INFERRED`
- OGDProvider `INFERRED`
- DataSourceRegistry `INFERRED`
- ManualProvider `INFERRED`
- clean_price_records() `INFERRED`
- _validate_record() `INFERRED`
- _normalize_record() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*