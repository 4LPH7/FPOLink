# Community 20

> 24 nodes · cohesion 0.13

## Key Concepts

- **CEDAAPIProvider** (22 connections) — `backend/app/data_sources/ceda_api.py`
- **._request_with_retry()** (10 connections) — `backend/app/data_sources/ceda_api.py`
- **.fetch_prices()** (8 connections) — `backend/app/data_sources/ceda_api.py`
- **.get_commodities()** (6 connections) — `backend/app/data_sources/ceda_api.py`
- **.get_geographies()** (5 connections) — `backend/app/data_sources/ceda_api.py`
- **.is_available()** (4 connections) — `backend/app/data_sources/ceda_api.py`
- **._parse_api_item()** (4 connections) — `backend/app/data_sources/ceda_api.py`
- **.is_circuit_open()** (3 connections) — `backend/app/data_sources/ceda_api.py`
- **._headers()** (2 connections) — `backend/app/data_sources/ceda_api.py`
- **._record_failure()** (2 connections) — `backend/app/data_sources/ceda_api.py`
- **._record_success()** (2 connections) — `backend/app/data_sources/ceda_api.py`
- **.reset_circuit()** (2 connections) — `backend/app/data_sources/ceda_api.py`
- **Any** (2 connections)
- **.__init__()** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **date** (1 connections)
- **Execute HTTP request with short timeout, retries, and circuit breaker.** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Retrieve list of all commodities: [{"id": int, "name": str}].** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}]** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Fetch prices from CEDA API with narrow query targeting.** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Parse CEDA API JSON item into standardized PriceRecord.** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Fetch live or historical prices from CEDA Agmarknet Data Portal API.** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Check if circuit breaker is currently tripped.** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Reset circuit breaker state (useful for tests or recovery).** (1 connections) — `backend/app/data_sources/ceda_api.py`
- **Response** (1 connections)

## Relationships

- [Community 9](Community_9.md) (3 shared connections)
- [Community 3](Community_3.md) (3 shared connections)
- [Community 30](Community_30.md) (3 shared connections)
- [Community 31](Community_31.md) (2 shared connections)

## Source Files

- `backend/app/data_sources/ceda_api.py`

## Audit Trail

- EXTRACTED: 43 (91%)
- INFERRED: 4 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*