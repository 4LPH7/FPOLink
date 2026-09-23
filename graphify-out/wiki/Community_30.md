# Community 30

> 16 nodes · cohesion 0.21

## Key Concepts

- **PriceRecord** (35 connections) — `backend/app/data_sources/base.py`
- **IngestionService** (20 connections) — `backend/app/services/ingestion.py`
- **test_ingestion.py** (14 connections) — `backend/tests/test_ingestion.py`
- **RawIngest** (8 connections) — `backend/app/models/raw_ingest.py`
- **._store_records()** (7 connections) — `backend/app/services/ingestion.py`
- **test_ingestion_and_deduplication()** (6 connections) — `backend/tests/test_ingestion.py`
- **._resolve_market()** (5 connections) — `backend/app/services/ingestion.py`
- **.run_ingestion()** (5 connections) — `backend/app/services/ingestion.py`
- **Standardized price record from any data source.** (1 connections) — `backend/app/data_sources/base.py`
- **Base** (1 connections)
- **date** (1 connections)
- **Store price records in the database, deduplicating by unique constraint.** (1 connections) — `backend/app/services/ingestion.py`
- **Find or create a market entry.** (1 connections) — `backend/app/services/ingestion.py`
- **Handles price data ingestion from all configured sources.** (1 connections) — `backend/app/services/ingestion.py`
- **Run price ingestion for configured crops and districts. Returns a summary dict…** (1 connections) — `backend/app/services/ingestion.py`
- **Tests for data ingestion, deduplication, and upsert.** (1 connections) — `backend/tests/test_ingestion.py`

## Relationships

- [Community 9](Community_9.md) (9 shared connections)
- [Community 15](Community_15.md) (9 shared connections)
- [Community 0](Community_0.md) (6 shared connections)
- [Community 31](Community_31.md) (6 shared connections)
- [Community 23](Community_23.md) (5 shared connections)
- [Community 2](Community_2.md) (4 shared connections)
- [Community 8](Community_8.md) (4 shared connections)
- [Community 28](Community_28.md) (4 shared connections)
- [Community 20](Community_20.md) (3 shared connections)
- [Community 36](Community_36.md) (3 shared connections)
- [Community 44](Community_44.md) (2 shared connections)
- [Community 48](Community_48.md) (1 shared connections)

## Source Files

- `backend/app/data_sources/base.py`
- `backend/app/models/raw_ingest.py`
- `backend/app/services/ingestion.py`
- `backend/tests/test_ingestion.py`

## Audit Trail

- EXTRACTED: 64 (77%)
- INFERRED: 19 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*