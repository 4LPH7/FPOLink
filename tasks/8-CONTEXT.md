# Phase 8 — Statewide Platform Foundation: CONTEXT.md

> Strategic Architecture Contract for FPOLink TN Version 0.5.
> Transitions FPOLink from an Erode-specific prototype into a multi-tenant Tamil Nadu Agricultural Intelligence Platform while retaining Erode/Kodumudi as the verified production anchor.

---

## 1. Vision & Architectural Transformation

### What FPOLink Is Becoming
Not just a website showing mandi prices, but a **statewide agricultural operating system** connecting:
`Farmers / FPOs ── Market Network ── Buyers ── Government / Agrinet Data ── Intelligence Layer`

### Transformation Vector
```
CURRENT Application (v0.1)             TARGET Platform (v0.5 Foundation → v1.0 State Network)
──────────────────────────             ───────────────────────────────────────────────────────
Erode District (Hardcoded)     ───►    Tamil Nadu (38 Districts, Taluks, Villages as Data)
Turmeric / Banana only         ───►    Agricultural Ontology (Tier A Priority: 20+ Commodities)
Single-FPO / Flat Scoping      ───►    Multi-Tenant Scoping (State, District, FPO, Staff RBAC)
Single-District Ingestion      ───►    Statewide Ingestion Orchestrator with Quality Scoring
Ad-hoc string names            ───►    Canonical Registries with Source-Specific Aliases
Unversioned API                ───►    API v1 (`/api/v1/...`) with Backward-Compatibility Shims
```

---

## 2. Locked Decisions & Core Tenets

### D1: Geography as First-Class Entities (No More Hardcoded District Strings)
- **Hierarchy:** `State` (Tamil Nadu) ──► `District` (38 districts) ──► `Taluk` ──► `Block` ──► `Village`.
- **References:** `FPO`, `Farmer`, and `Market` will reference `district_id`, `taluk_id`, and `state_id`.
- **Backward Compatibility:** Existing string columns (`district`, `taluk`, `village`) are retained and synchronized during migration to prevent breaking existing pilot code, WhatsApp bot queries, and tests.

### D2: Multi-Tenant RBAC & Organization Scoping
- **Roles:**
  - `STATE_ADMIN` — Statewide visibility across all 38 districts, system-wide configuration.
  - `DISTRICT_ADMIN` — Scoped to a specific district (e.g. Erode District Collectorate or Joint Director of Agriculture).
  - `FPO_ADMIN` — Scoped to a specific FPO entity (manages FPO profile, staff, farmers).
  - `FPO_STAFF` — Operational staff of an FPO (farmer onboarding, harvest aggregation, dispatch).
  - `DATA_OPERATOR` — Ingestion operations, manual mandi price entry, quality verification.
  - `ANALYST` — Read-only statewide price intelligence, forecasts, and arrival trends.
  - `BUYER` — Wholesale buyers submitting purchase requirements.
  - `FIELD_AGENT` — Extension officers / field staff verifying on-ground farm holdings.
  - `FARMER` — WhatsApp & mobile interface users.
- **Audit Logging:** An immutable `audit_logs` table records actor, action, target entity, state before/after, IP, and timestamp for all administrative and operational changes.

### D3: Agricultural Crop Ontology & Canonical Alias Registry
- **Crop Master:** Canonical identifier, Tamil name, scientific name, category, subcategory, default unit, market unit, seasonality, water requirement, perishability, storage days, horticulture/commercial flags.
- **CropAlias Master:** Maps dirty names ("Manjal", "Turmeric Finger", "மஞ்சள்", CEDA codes, Agmarknet codes) to canonical crops.
- **Variety Master & VarietyAlias:** Supports specific varietal lines (e.g., Paddy ──► Ponni, ADT 36, CO 51, BPT; Banana ──► Grand Naine, Poovan, Nendran).
- **Tier-A Commodities Seeded First:**
  - *Cereals:* Paddy, Maize, Sorghum, Ragi
  - *Pulses:* Black Gram, Green Gram, Red Gram
  - *Oilseeds:* Groundnut, Sesame, Sunflower
  - *Commercial:* Sugarcane, Cotton, Turmeric, Tapioca
  - *Horticulture:* Banana, Tomato, Onion, Chilli, Brinjal, Okra, Moringa
  - *Plantation:* Coconut, Arecanut, Cashew

### D4: Market Registry & Canonical Market Aliases
- **Market Master:** Normalized with `district_id`, `taluk_id`, `market_type` (regulated_market, uzhavar_sandhai, private_mandi), and latitude/longitude.
- **MarketAlias Master:** Maps upstream strings ("Erode Mandi", "ERODE", "Erode Regulated Market", Agmarknet IDs) to canonical market UUIDs.

### D5: Ingestion Orchestration & Explainable Data Quality Framework
- **Models:** `data_sources`, `ingestion_runs`, `data_quality_events`.
- **Explainable Quality Score (0–100):** Every `MarketPrice` row receives an explainable score derived from:
  - `freshness` (penalty for aging observations)
  - `source_reliability` (based on source priority)
  - `market_match` (confidence of alias resolution)
  - `outlier_penalty` (MAD z-score deviation)
  - `completeness` (presence of min, max, modal, and arrival quantities)
- Score and breakdown JSON are persisted directly with the price record.

### D6: API Versioning (v1) & Seamless Compatibility
- New standard prefix: `/api/v1/...`
- Existing `/api/*` endpoints continue to function as shims delegating to the unified services.
- The WhatsApp bot, existing frontend dashboard, and 145 unit tests continue running with zero downtime or regressions.

---

## 3. Explicitly Out of Scope for Phase 8

- Training complex multi-variable ML models (TFT, DeepAR, N-BEATS) — deferred to Phase 11.
- Statewide frontend map visualization — deferred to Phase 9.
- Farmer PWA (`farmer.fpolink.tn`) — deferred to Phase 13.
- Redis / distributed message queues — APScheduler remains sufficient for current worker scale.
