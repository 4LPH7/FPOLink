# Community 31

> 16 nodes · cohesion 0.14

## Key Concepts

- **DataSourceRegistry** (17 connections) — `backend/app/data_sources/registry.py`
- **ManualProvider** (9 connections) — `backend/app/data_sources/manual.py`
- **.__init__()** (5 connections) — `backend/app/data_sources/registry.py`
- **.fetch_all()** (4 connections) — `backend/app/data_sources/registry.py`
- **.fetch_prices()** (4 connections) — `backend/app/data_sources/registry.py`
- **test_registry_and_ceda_provider_never_load_synthetic_in_normal_run()** (4 connections) — `backend/tests/test_source_safety.py`
- **.get_provider()** (3 connections) — `backend/app/data_sources/registry.py`
- **.__init__()** (3 connections) — `backend/app/services/ingestion.py`
- **date** (2 connections)
- **Handles manually-entered price data from FPO staff.** (1 connections) — `backend/app/data_sources/manual.py`
- **Manages data source providers with fallback chain. Priority: OGD (live API) →…** (1 connections) — `backend/app/data_sources/registry.py`
- **Get provider by source name.** (1 connections) — `backend/app/data_sources/registry.py`
- **Fetch prices from all available providers. Uses fallback chain: tries each…** (1 connections) — `backend/app/data_sources/registry.py`
- **Fetch from ALL available providers (not just first success).** (1 connections) — `backend/app/data_sources/registry.py`
- **Session** (1 connections)
- **Verify that CEDAProvider and DataSourceRegistry ignore synthetic files by…** (1 connections) — `backend/tests/test_source_safety.py`

## Relationships

- [Community 9](Community_9.md) (6 shared connections)
- [Community 30](Community_30.md) (6 shared connections)
- [Community 23](Community_23.md) (3 shared connections)
- [Community 44](Community_44.md) (2 shared connections)
- [Community 28](Community_28.md) (2 shared connections)
- [Community 36](Community_36.md) (2 shared connections)
- [Community 20](Community_20.md) (2 shared connections)
- [Community 15](Community_15.md) (1 shared connections)

## Source Files

- `backend/app/data_sources/manual.py`
- `backend/app/data_sources/registry.py`
- `backend/app/services/ingestion.py`
- `backend/tests/test_source_safety.py`

## Audit Trail

- EXTRACTED: 33 (80%)
- INFERRED: 8 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*