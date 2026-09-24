# FPOLink TN — Statewide Platform Foundation (v0.5 Architecture)

## Executive Summary
This document outlines the architectural transformation of FPOLink from an Erode-specific prototype into a multi-tenant Tamil Nadu Agricultural Intelligence Platform (**v0.5 Foundation**), preserving 100% backward compatibility for the Erode pilot while establishing statewide scalability across 38 districts and hundreds of commodities.

---

## 1. Architectural Pillars

### 1.1 Complete Administrative Geography Hierarchy
The platform models administrative boundaries as normalized relational entities:
- **`states`**: Master entity (`Tamil Nadu`, code: `TN`).
- **`districts`**: 38 Revenue Districts of Tamil Nadu (e.g., Erode, Coimbatore, Thanjavur, Dindigul, Salem) with ISO-style codes and geolocations.
- **`taluks`**: Sub-district administrative divisions linked to districts.
- **`blocks`**: Community development blocks.
- **`villages`**: Ground-level revenue settlements.

All core domain entities (`FPO`, `Farmer`, `Market`, `User`) are linked via `district_id`, `state_id`, `taluk_id`, and `village_id` foreign keys.

### 1.2 Unified Agricultural Crop & Varietal Ontology
- **`crops`**: Canonical crop entity storing `canonical_name`, `name`, `tamil_name` (e.g. `மஞ்சள்`), `scientific_name` (e.g. `Curcuma longa`), `category`, `unit`, `market_unit`, and agronomic flags.
- **`crop_aliases`**: Regional, colloquial, and provider-specific names (e.g. `haldi`, `tamatar`, `nellu`, `manjal`) mapped to canonical crops.
- **`varieties` & `variety_aliases`**: Specific commercial cultivars and grades (e.g., `Salem`, `Erode Local`, `Poovan`, `Nendran`, `Ponni`).
- **`CropResolver` service**: Provides deterministic 4-stage resolution from any external mandi string to a canonical `Crop` or `Variety`.

### 1.3 Regulated Market Master Registry
- **`markets`**: Normalized market master entity storing unique market code (e.g. `TN-ERD-01`), GPS coordinates (`latitude`, `longitude`), `district_id`, and `market_type`.
- **`market_aliases`**: Maps provider strings and colloquial names (e.g. `cbe mandi`, `semmampalayam mandi`, `erode regulated market committee`) to canonical markets.
- **`MarketResolver` service**: Resolves market strings scoped optionally by district.

### 1.4 Multi-Tenant RBAC & Organizational Scoping
- **Roles**:
  - `STATE_ADMIN`: Statewide oversight across all 38 districts.
  - `DISTRICT_ADMIN`: Scoped to a specific revenue district (`district_id`).
  - `FPO_ADMIN` & `FPO_STAFF`: Scoped strictly to their registered FPO (`fpo_id`).
  - `DATA_OPERATOR`: Authorized for mandi and telemetry data entry.
  - `ANALYST`: Read-only aggregate reporting.
  - `BUYER`: Verified institutional crop buyers.
  - `FIELD_AGENT`: Ground agents assisting farmer onboarding.
  - `FARMER`: Individual member access with DPDP consent tracking.
- **`AuditLog`**: Tamper-evident logging of administrative actions with before/after state snapshots.

### 1.5 Explainable Data Quality Engine
Each incoming market price observation is scored dynamically from 0.0 to 100.0 with a transparent breakdown:
1. **Freshness (30%)**: Decay based on days since observation date.
2. **Source Reliability (25%)**: Provenance ranking (`OGD`, `Agmarknet`, `CEDA`, `TN AgriNet`, `Manual`).
3. **Market Match (25%)**: Confidence of canonical crop and market alias resolution.
4. **Completeness (20%)**: Completeness of modal price, min/max spread, and arrival volume.
5. **Outlier Penalty**: Penalties for logical price inversions (`min > max` or `modal < min`) or extreme dispersion.
- Observations scoring `< 50.0` automatically generate a `DataQualityEvent`.

### 1.6 API v1 Unified Hierarchy
A versioned `/api/v1/` endpoint structure with 100% backward compatibility with legacy `/api/`:
- `GET /api/v1/geography/states`
- `GET /api/v1/geography/districts`
- `GET /api/v1/geography/taluks`
- `POST /api/v1/crops/resolve`
- `POST /api/v1/markets/resolve`
- `GET /api/v1/prices/latest`
- `GET /api/v1/prices/history`
- `GET /api/v1/prices/quality-summary`
- `GET /api/v1/commodities`
- `GET /api/v1/commodities/{crop_id}`
- `GET /api/v1/ingestion/runs`
- `GET /api/v1/ingestion/runs/{run_id}`
- `GET /api/v1/ingestion/freshness`
- `POST /api/v1/ingestion/trigger`
- `GET /api/v1/prices/{price_id}/lineage`
- `GET /api/v1/farmers/{fpo_id}`
- `GET /api/v1/fpos/`
- `GET /api/v1/audit/logs`

### 1.7 Deterministic External Source Mapping Layer (v0.6)
Eliminates reliance on fragile fuzzy string matching by storing deterministic mappings between external provider IDs (OGD, Agmarknet, CEDA) and canonical entities:
- **`CropSourceMapping`**: Maps external crop codes/names (e.g., `TURMERIC`, `Shallot (Small Onion)`) to canonical `crops.id` with confidence scores.
- **`MarketSourceMapping`**: Maps external mandi codes/names (e.g., `OGD_MDU`, `AGM_TRY`) to canonical `markets.id` across all 38 districts.
- **`VarietySourceMapping`**: Maps external cultivar names to canonical `varieties.id`.
- Resolvers (`CropResolver`, `MarketResolver`) prioritize deterministic Stage 0 lookup with case-insensitive matching before falling back to aliases or text matching.

### 1.8 Immutable Raw Ingestion Persistence & Replay Harness
- Every external payload received from OGD, Agmarknet, CEDA, or manual entry is persisted immutably in `raw_ingest` with an algorithmic SHA-256 checksum.
- Duplicate payloads within the same source are automatically deduplicated.
- **`scripts/replay_raw_ingestion.py`**: Standalone replay harness that can replay unparsed or historical raw packets through updated normalization pipelines without re-querying external provider APIs.

### 1.9 End-to-End Data Lineage Tracking
- Complete traceability from front-facing prices down to raw provider packets:
  $$\text{MarketPrice} \longrightarrow \text{IngestionRun} \longrightarrow \text{RawIngest}$$
- Every `MarketPrice` record stores foreign keys `ingestion_run_id` and `raw_ingest_id`.
- The `/api/v1/prices/{id}/lineage` endpoint exposes full provenance details: canonical crop, market, raw payload, execution timestamp, and provider checksum.

### 1.10 Statewide Telemetry Console & Commodity Registry UI
- **Commodity Registry (`/admin/commodities`)**: Staff and administrator interface to search, inspect, and filter all 20 Tier-A crops across categories (spice, fruit, vegetable, cereal, fiber, commercial), view registered botanical cultivars, aliases, and external source mappings.
- **Ingestion Center Console (`/admin`)**: Telemetry hub showing statewide reporting freshness across all 38 revenue districts, active market counts, ingestion run history, and real-time ingestion trigger controls.

---

## 2. Database Migrations

| Migration Version | Description |
|-------------------|-------------|
| `0006_statewide_foundation` | Added `states`, `districts`, `taluks`, `blocks`, `villages`, and foreign keys on `fpos`, `farmers`, and `markets`. |
| `0007_crop_market_ontology` | Added crop ontology fields, `crop_aliases`, `varieties`, `variety_aliases`, market code/geo fields, and `market_aliases`. |
| `0008_multitenant_rbac_audit` | Added 9 user roles, `fpo_id` and `district_id` scoping on `users`, and the `audit_logs` table. |
| `0009_statewide_ingestion_quality` | Added `data_sources`, `ingestion_runs`, `data_quality_events`, and `quality_score`/`quality_breakdown` on `market_prices`. |
| `0010_source_mappings_markets` | Added `crop_source_mappings`, `market_source_mappings`, `variety_source_mappings`, and expanded `markets` with `canonical_name`, `tamil_name`, `is_regulated`, `e_nam`, `operating_status`. |

---

## 3. Seed Reference Datasets
Run the idempotent seed script at any time:
```bash
python scripts/seed_statewide_foundation.py
```
This populates:
- 1 State (`Tamil Nadu`, code: `TN`)
- 38 Revenue Districts
- 25 Pilot Taluks (Erode, Coimbatore, Thanjavur)
- 20 Tier-A Commodities:
  1. Turmeric (*Curcuma longa*, மஞ்சள்)
  2. Banana (*Musa acuminata*, வாழை)
  3. Coconut (*Cocos nucifera*, தேங்காய்)
  4. Paddy (*Oryza sativa*, நெல்)
  5. Groundnut (*Arachis hypogaea*, நிலக்கடலை)
  6. Tomato (*Solanum lycopersicum*, தக்காளி)
  7. Small Onion (*Allium cepa var. aggregatum*, சின்ன வெங்காயம்)
  8. Onion (*Allium cepa*, பெரிய வெங்காயம்)
  9. Green Chilli (*Capsicum annuum*, பச்சை மிளகாய்)
  10. Red Chilli (*Capsicum annuum*, காய்ந்த மிளகாய்)
  11. Maize (*Zea mays*, மக்காச்சோளம்)
  12. Cotton (*Gossypium hirsutum*, பருத்தி)
  13. Sugarcane (*Saccharum officinarum*, கரும்பு)
  14. Black Gram (*Vigna mungo*, உளுந்து)
  15. Green Gram (*Vigna radiata*, பாசிப்பயறு)
  16. Tapioca (*Manihot esculenta*, மரவள்ளிக்கிழங்கு)
  17. Mango (*Mangifera indica*, மாம்பழம்)
  18. Brinjal (*Solanum melongena*, கத்தரிக்காய்)
  19. Ladies Finger (*Abelmoschus esculentus*, வெண்டைக்காய்)
  20. Ginger (*Zingiber officinale*, இஞ்சி)
- 67 Canonical Crop Aliases
- 40 Cultivar Varieties & Aliases
- 43 Regulated Mandis covering all 38 districts with geocoordinates, tamil names, and e-NAM status
- 110 Canonical Market Aliases
- 64 Deterministic Source Mappings (40 crop mappings, 24 market mappings)
- 5 Verified Ingestion Data Sources

---

## 4. Verification Checkpoint Sign-Off

### Checkpoint E (v0.5 Foundation):
All 164 automated tests in the regression suite passed without errors.

### Checkpoint F (v0.6 Statewide Data Network):
All 181 automated unit and integration tests pass with 100% green status:
- `tests/test_source_mappings.py` (Deterministic resolution precedence)
- `tests/test_raw_replay.py` (Immutable raw persistence & offline replay)
- `tests/test_data_lineage.py` (End-to-end price to raw packet lineage)
- `tests/test_ingestion_center_api.py` (Telemetry endpoints & statewide freshness)
- `tests/test_statewide_coverage.py` (Multi-district cross-validation across TN)
- All 145 baseline Erode pilot tests (WhatsApp bot, parsers, auth, forecasts, digest worker, zero regressions).
