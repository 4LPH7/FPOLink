# CEDAProvider

> God node · 25 connections · `backend/app/data_sources/ceda.py`

**Community:** [Community 23](Community_23.md)

## Connections by Relation

### calls
- .__init__() `EXTRACTED`
- test_registry_and_ceda_provider_never_load_synthetic_in_normal_run() `EXTRACTED`
- main() `EXTRACTED`
- test_ceda_parser_with_published_schema() `EXTRACTED`
- test_ceda_parser_with_sample_csv() `EXTRACTED`
- test_ceda_parser_with_synthetic_fixture() `EXTRACTED`

### contains
- ceda.py `EXTRACTED`

### imports
- test_source_safety.py `EXTRACTED`
- test_parsers.py `EXTRACTED`
- registry.py `EXTRACTED`
- ogd.py `EXTRACTED`
- backfill_ceda.py `EXTRACTED`

### inherits
- MarketDataProvider `EXTRACTED`

### method
- ._parse_row() `EXTRACTED`
- .fetch_prices() `EXTRACTED`
- ._parse_date() `EXTRACTED`
- ._parse_decimal() `EXTRACTED`
- ._find_csv() `EXTRACTED`
- ._get_field() `EXTRACTED`
- ._parse_float() `EXTRACTED`
- .__init__() `EXTRACTED`

### rationale_for
- Parse CEDA historical CSV data for price backfill. `EXTRACTED`

### uses
- [PriceRecord](PriceRecord.md) `INFERRED`
- OGDProvider `INFERRED`
- DataSourceRegistry `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*