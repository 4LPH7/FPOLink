# Community 10

> 29 nodes · cohesion 0.10

## Key Concepts

- **main.py** (20 connections) — `backend/app/main.py`
- **database.py** (19 connections) — `backend/app/database.py`
- **FastAPI** (18 connections)
- **api/prices.py** (16 connections) — `backend/app/api/prices.py`
- **conftest.py** (15 connections) — `backend/tests/conftest.py`
- **get_db()** (14 connections) — `backend/app/database.py`
- **admin.py** (13 connections) — `backend/app/api/admin.py`
- **db()** (6 connections) — `backend/tests/conftest.py`
- **buyers.py** (3 connections) — `backend/app/api/buyers.py`
- **predictions.py** (3 connections) — `backend/app/api/predictions.py`
- **create_tables()** (3 connections) — `backend/tests/conftest.py`
- **fixture** (3 connections)
- **get_buyers()** (2 connections) — `backend/app/api/buyers.py`
- **get_forecast()** (2 connections) — `backend/app/api/predictions.py`
- **health_check()** (2 connections) — `backend/app/main.py`
- **lifespan()** (2 connections) — `backend/app/main.py`
- **Admin endpoints — manual ingestion trigger, system status.** (1 connections) — `backend/app/api/admin.py`
- **get** (1 connections)
- **get** (1 connections)
- **Price endpoints — latest prices, history, trends, anomalies.** (1 connections) — `backend/app/api/prices.py`
- **Session** (1 connections)
- **FastAPI dependency that provides a database session.** (1 connections) — `backend/app/database.py`
- **get** (1 connections)
- **_override_get_db()** (1 connections) — `backend/tests/conftest.py`
- **Test configuration and fixtures.** (1 connections) — `backend/tests/conftest.py`
- *... and 4 more nodes in this community*

## Relationships

- [Community 0](Community_0.md) (9 shared connections)
- [Community 9](Community_9.md) (6 shared connections)
- [Community 25](Community_25.md) (5 shared connections)
- [Community 8](Community_8.md) (5 shared connections)
- [Community 35](Community_35.md) (4 shared connections)
- [Community 2](Community_2.md) (4 shared connections)
- [Community 19](Community_19.md) (4 shared connections)
- [Community 39](Community_39.md) (4 shared connections)
- [Community 7](Community_7.md) (4 shared connections)
- [Community 16](Community_16.md) (4 shared connections)
- [Community 5](Community_5.md) (4 shared connections)
- [Community 14](Community_14.md) (4 shared connections)

## Source Files

- `backend/app/api/admin.py`
- `backend/app/api/buyers.py`
- `backend/app/api/predictions.py`
- `backend/app/api/prices.py`
- `backend/app/database.py`
- `backend/app/main.py`
- `backend/tests/conftest.py`

## Audit Trail

- EXTRACTED: 111 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*