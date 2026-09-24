# Phase 9 — Statewide Data Network (v0.6): CONTEXT.md

> Strategic Architecture Contract for FPOLink TN Version 0.6.
> Transitions FPOLink from an architectural foundation (v0.5) into a live, continuously updated statewide data network with complete market registries, deterministic source mappings, reproducible raw ingestion, and an operational Ingestion Command Center.

---

## 1. Vision & Roadmap Positioning

```text
                         FPOLink TN

v0.1  Erode FPO Pilot
          │
          ▼
v0.5  Statewide Platform Foundation       ← COMPLETED
          │
          ├── v0.6 State Data Network     ← CURRENT (Phase 9)
          │
          ├── v0.7 Agricultural Intelligence (Phases 11-12)
          │
          ├── v0.8 Supply + Demand Network (Phases 13-15)
          │
          ├── v0.9 State Command Center (Phases 16-17)
          │
          ▼
v1.0  Tamil Nadu Agricultural Intelligence Platform (Phases 18-20)
```

### The Core Paradigm Shift
- **v0.5 solved architecture.** (Geography hierarchy, canonical ontology, multi-tenant RBAC, quality scoring skeleton, API v1 routing).
- **v0.6 solves data.** (Complete regulated market registry, source-specific external IDs, reproducible raw ingestion, multi-district OGD harvesting, data lineage, ingestion ops console).
- **v0.7 will solve intelligence.** (Forecasting, feature store, rolling price spreads, anomaly alerts).
- **v0.8 will solve coordination.** (Farmer harvest aggregation, supply heatmaps, buyer order matching).

### The Golden Rule of v0.6
> [!IMPORTANT]
> **"From v0.6 onward, never write a feature that assumes Erode. Erode is data, not code."**
> Districts, markets, and crop scopes must always be resolved dynamically via user tenant context or explicit API query parameters.

---

## 2. Locked Architectural Decisions

### D1: Reference-Data Invariant Assertions & CI Protection
- **Invariant Enforcement:** 38 revenue districts, 20 Tier-A commodities, 25 pilot taluks, 8 baseline markets, and 5 data sources must be validated via strict compile-time and runtime assertions.
- **CI Test Barrier:** `backend/tests/test_seed_reference_counts.py` asserts these exact counts and fails any CI build if master reference counts unexpectedly change or degrade.

### D2: Comprehensive Regulated Market Master Registry
- The current 8 pilot markets represent a tracer vertical slice. Phase 9 expands this to the full canonical network of regulated agricultural markets across Tamil Nadu.
- Every market must possess:
  - `market_code` (e.g. `TN-ERD-01`, `TN-CBE-01`)
  - `canonical_name` and `tamil_name`
  - `district_id` (foreign key) and `taluk_id` (foreign key where mapped)
  - `latitude` and `longitude` (validated decimal coordinates)
  - `market_type` (`regulated_market`, `uzhavar_sandhai`, `private_mandi`)
  - `is_regulated` (Boolean), `e_nam` (Boolean)
  - `operating_status` (`active`, `seasonal`, `inactive`)
  - Multi-provider aliases linked via `MarketAlias`

### D3: Source-Specific External Identifier Mappings (Zero-Fuzzy Priority)
- Instead of relying predominantly on fuzzy string matching (which breaks when government portals slightly alter spelling or punctuation), introduce explicit mapping entities:
  - `CropSourceMapping (id, crop_id, source_id, external_code, external_name, confidence, verified_at)`
  - `MarketSourceMapping (id, market_id, source_id, external_code, external_name, confidence, verified_at)`
  - `VarietySourceMapping (id, variety_id, source_id, external_code, external_name, confidence, verified_at)`
- **Multi-Stage Resolution Hierarchy:**
  1. Exact external source code/ID (e.g., OGD commodity code `23` -> Paddy)
  2. Exact canonical code/name match
  3. Source-specific alias lookup (`CropAlias` / `MarketAlias` with matching `source`)
  4. Regional/Tamil alias lookup
  5. Substring / normalized fuzzy match
  6. Flag for manual review in Ingestion Center

### D4: Commodity Registry UI & Administrative Portal
- Frontend route: `/admin/commodities`
- Backend API: `GET /api/v1/commodities`, `GET /api/v1/commodities/{id}`
- Interactive commodity registry displaying:
  - Canonical English, Tamil, and botanical names
  - Varietal catalog with grades and maturity
  - Registered regional and provider aliases
  - Active reporting markets and recent arrival volumes
  - Data source mapping coverage

### D5: Reproducible Raw Ingestion Persistence & Replayability
- Every external observation fetched from OGD, Agmarknet, CEDA, or web feeds must be recorded immutably in `raw_ingest`:
  - `source`: Provider identifier (`ogd`, `ceda`, `agmarknet`)
  - `source_record_id`: Provider's native row ID or composite hash
  - `checksum`: SHA-256 hash of payload to guarantee idempotency
  - `payload`: Full JSONB raw record
  - `retrieved_at`: Timestamp of HTTP capture
- Allows complete downstream reprocessing and schema re-migrations without re-fetching historical external APIs.

### D6: Real Statewide Ingestion Pipeline (8-Stage Flow)
```text
External Source (OGD / CEDA)
       │
       ▼ [1. Raw Ingest & Checksum]
RawIngest (Immutable JSONB)
       │
       ▼ [2. Schema Validation]
Pydantic PriceRecord
       │
       ▼ [3. Source Mapping / External ID]
CropSourceMapping / MarketSourceMapping
       │
       ▼ [4. Canonical Entity Resolution]
Canonical Crop & Market
       │
       ▼ [5. Unit & Currency Normalization]
Modal / Min / Max in ₹/kg (Raw preserved)
       │
       ▼ [6. Geographic Validation]
District / State Boundary Verification
       │
       ▼ [7. Duplicate & MAD Outlier Detection]
Unique constraint check & Volatility penalty
       │
       ▼ [8. Explainable Quality Scoring]
Quality score (0–100) & breakdown
       │
       ▼
MarketPrice (Live Platform Record)
```

### D7: Ingestion Center Telemetry & Operations Console
- Upgraded Admin route: `/admin/ingestion`
- Backend API: `GET /api/v1/ingestion/runs`, `GET /api/v1/ingestion/runs/{run_id}`
- Metrics surfaced:
  - Run status (`success`, `warning`, `failed`)
  - Total records received, accepted, and rejected
  - Rejection taxonomy: `unknown_market`, `unknown_crop`, `invalid_price`, `duplicate`, `invalid_date`, `outlier`
  - Statewide freshness gauges (districts active, markets reporting, commodities active)

### D8: Full Data Lineage Tracking
- Every price displayed across web dashboards or sent via WhatsApp must carry complete provenance:
  - `MarketPrice.ingestion_run_id` -> FK to `ingestion_runs.id`
  - `MarketPrice.raw_ingest_id` -> FK to `raw_ingest.id`
  - Enables auditability: any farmer or regulator can trace a price back to the raw OGD packet and timestamp.

---

## 3. Scope Boundaries

### In Scope (Phase 9)
1. Automated reference invariant assertions and CI fail-safes.
2. Comprehensive Tamil Nadu regulated market master registry import (all 38 districts).
3. Source mapping models (`CropSourceMapping`, `MarketSourceMapping`, `VarietySourceMapping`) and Alembic migration `0010`.
4. Commodity Registry UI (`/admin/commodities`) and API (`/api/v1/commodities`).
5. Immutable raw ingestion persistence with SHA-256 checksums and replay harness.
6. 8-stage statewide ingestion pipeline with multi-district OGD execution.
7. Ingestion Center Telemetry Dashboard (`/admin/ingestion`) and run inspection API.
8. End-to-end data lineage linking `MarketPrice` to `IngestionRun` and `RawIngest`.
9. Full integration test suite and Checkpoint F sign-off.

### Deferred to Phase 10 & 11
- Multi-market LightGBM / XGBoost price forecasting (Phase 12).
- Farmer crop acreage and supply aggregation heatmaps (Phase 13).
- Buyer purchase requirements and automated order matching (Phases 14–15).
- State Command Center multi-role dashboards (Phases 16–17).
