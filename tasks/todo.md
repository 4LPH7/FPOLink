# WhatsApp Integration: Task List

Details, acceptance criteria and verification for each task are in `tasks/plan.md`.

## Phase 0: De-risk external dependencies (start now, in parallel)
- [x] T0.1 Answer the open questions (number, Meta owner, pilot FPO: resolved in `docs/PILOT_SPEC.md`)
- [ ] T0.2 Meta test setup and first successful send (CLI verification tool: `backend/scripts/verify_meta_send.py`)
- [x] T0.3 Sanitized fixtures derived from captured real Meta webhook payloads (`backend/tests/fixtures/whatsapp/`, `tests/test_whatsapp_fixtures.py`, `docs/data-provenance.md`)
- [x] T0.4 Submit `daily_price_digest` templates (ta, en) for approval (`docs/meta_templates.json`, `backend/scripts/register_whatsapp_templates.py`)
- [x] T0.5 Real price data loaded (verified Agmarknet Erode baseline + `backend/scripts/check_market_coverage.py` audit in `docs/MARKET_COVERAGE_REPORT.md`)

## Phase 1: Vertical slice, PRICE returns a real price (Code-Complete, Pending Live Verification)
- [x] T1.1 Import skeleton into the repo, CI green
- [x] T1.2 Migration: phone/lang/consent fields + bot tables
- [x] T1.3 `DbBotServices` (farmers, prices, atomic dedup, state TTL)
- [x] T1.4 Wire engine, settings validation, kill switch
- [x] T1.5 Contract tests for outgoing payloads
### Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo
> [!NOTE]
> Detailed 5-minute testing protocol in `docs/CHECKPOINTS_GUIDE.md`. Prerequisites T0.3 and T0.5 are code-complete. Requires human verification with real phone in Meta Sandbox.
- [ ] Checkpoint A verified by human with real phone testing (protocol: `docs/CHECKPOINTS_GUIDE.md`)

## Phase 2: Onboarding, identity, consent
- [x] T2.1 wa.me invite link endpoint
- [x] T2.2 First-contact notice
- [x] T2.3 ALERTS ON/OFF and STOP from any state
- [x] T2.4 FPO/district scoping

## Phase 3: Harvest by chat
- [x] T3.1 Harvest service + API (idempotent by message id)
- [x] T3.2 Wire harvest flow to the service
- [x] T3.3 Rate limit, unsupported types, retry caps
### Checkpoint B: harvest submitted by chat is visible to FPO staff
- [ ] Reviewed by human (protocol: `docs/CHECKPOINTS_GUIDE.md`)

## Phase 4: Digest and alerts with cost control
- [x] T4.1 Status webhooks and unreachable numbers
- [x] T4.2 Daily digest worker job
- [x] T4.3 Price-move alert (max 1 per farmer per day)
- [x] T4.4 Usage report, monthly cap, circuit breaker
### Checkpoint C: dry run with 3 test farmers
- [ ] Reviewed by human (protocol: `docs/CHECKPOINTS_GUIDE.md`)

## Phase 5: Production readiness
- [x] T5.1 Deploy webhook behind stable HTTPS (Cloudflare Tunnel + production compose override)
- [x] T5.2 Meta production setup (META_PRODUCTION_CHECKLIST.md runbook)
- [x] T5.3 Security and privacy pass (DPDP retention purge: inbound 7d, state 24h, outbound 12mo)
- [x] T5.4 At-least-once processing sweep (migration 0005, status lifecycle, 10-min worker sweep)
- [x] T5.5 Observability and runbook (Sentry init, DB health check, OPS_RUNBOOK.md)
### Checkpoint D: staging E2E with a real phone
- [ ] Reviewed by human (protocol: `docs/CHECKPOINTS_GUIDE.md`)

## Phase 6: Frontend UX Foundation
- [x] T6.1 Install Tailwind + shadcn/ui (copy-in primitives: Button, Card, Badge, Table, Input, Tabs, Separator, Sheet)
- [x] T6.2 Define design tokens (emerald palette, HSL variables, Tamil typography line-height scale 1.7)
- [x] T6.3 Build responsive App Shell (collapsible desktop sidebar, sticky header with district/bot badge, content frame)
- [x] T6.4 Persistent Language Switcher (Tamil default, English toggle, localStorage persisted via useLanguage())
- [x] T6.5 Responsive breakpoints (desktop-first layout, tablet slide-over drawer down to 768px)
- [x] T6.6 Exit criteria wireframe shell routes (`/`, `/prices`, `/farmers`, `/admin`, `/whatsapp`)

## Phase 7: Core Screens (100% Real Data, Zero Mocks)
- [x] T7.1 Price/market dashboard (forecast chart, CEDA/OGD freshness indicator, primary price front-and-center: `/prices`)
- [x] T7.2 Farmer records (list/search/filter, DPDP consent status prominent per record: `/farmers`)
- [x] T7.3 Ingestion/admin status (CEDA/weather/NASA POWER adapter health, last-run telemetry: `/admin`)
- [x] T7.4 WhatsApp bot activity (read-only view into conversation_state and inbound logs: `/whatsapp`)


## Phase 8: Statewide Platform Foundation (v0.5 Architecture)
- [x] T8.1 Tracer Vertical Slice: Geography Hierarchy (State/District/Taluk/Block/Village) + Migration 0006
- [x] T8.2 Agricultural Ontology & Canonical Crop/Variety Registry with Aliases
- [x] T8.3 Market Master Registry & Canonical Market Aliases
- [x] T8.4 Multi-Tenant RBAC, Organization Scoping & Audit Logging
- [x] T8.5 Statewide Market Ingestion & Explainable Quality Scoring Framework
- [x] T8.6 API v1 Routing & Backward-Compatibility Shims
- [x] T8.7 Statewide Reference Seed & Verification Checkpoint E
### Checkpoint E: Statewide Foundation Sign-Off
- [x] Migration 0006-0009 applied, 38 TN districts queryable, Tier-A crops resolved, existing pilot 100% green

## Phase 9: Statewide Data Network (v0.6 Data Layer)
- [x] T9.1 Reference Invariants & Automated Count Assertions (38 districts, 20 crops, 25 taluks, 8 markets, 5 data sources)
- [x] T9.2 Complete Regulated Market Master Registry across all 38 districts
- [x] T9.3 External Source Mapping Models (`CropSourceMapping`, `MarketSourceMapping`, `VarietySourceMapping`) + Migration 0010
- [x] T9.4 Commodity Registry UI (`/admin/commodities`) & Admin API (`/api/v1/commodities`)
- [x] T9.5 Raw Ingestion Persistence & Replay Harness (`raw_ingest` with checksum)
- [x] T9.6 8-Stage Statewide Ingestion Pipeline
- [x] T9.7 Ingestion Center Telemetry Console (`/admin/ingestion` & `/api/v1/ingestion/runs`)
- [x] T9.8 End-to-End Price Data Lineage Tracking (`MarketPrice` -> `IngestionRun` -> `RawIngest`)
- [x] T9.9 Statewide Integration & Multi-District Regression Test Suite
- [x] T9.10 Checkpoint F: Statewide Data Network Sign-Off
### Checkpoint F: Statewide Data Network Sign-Off
- [x] Migration 0010 applied, 38 districts with registered mandis, deterministic source mappings, raw replay verified, 0 Erode regressions

## Phase 11: Agricultural Intelligence (v0.7 Intelligence Layer)
- [x] T11.1 Agricultural Feature Store Engine (`backend/app/ml/features.py`)
- [x] T11.2 Feature Store Unit & Verification Test Suite (`backend/tests/test_feature_store.py`)
- [x] T11.3 Dual Forecasting Engine: LightGBM Quantile Regression + Baseline (`backend/app/ml/forecasting.py`)
- [x] T11.4 Actionable Signal Engine & Prediction Persistence (`predictions`, `model_versions`, `forecast_log`)
- [x] T11.5 Worker Automated Prediction Pipeline Integration (`backend/app/worker.py`)
- [x] T11.6 Geospatial Market Arbitrage & Net Freight Engine (`backend/app/services/arbitrage.py`)
- [x] T11.7 Agricultural Intelligence API v1 Endpoints (`/api/v1/intelligence/*`)
- [x] T11.8 Frontend Price & Intelligence Dashboard Updates (Confidence envelopes, arbitrage matrix, 38-district selector)
- [x] T11.9 End-to-End Intelligence Integration Test Suite (`backend/tests/test_agricultural_intelligence.py`)
- [x] T11.10 Checkpoint G: Agricultural Intelligence Sign-Off
### Checkpoint G: Agricultural Intelligence Sign-Off
- [x] Dual-engine forecasting verified, feature store tested, arbitrage net freight calculated, 189 tests green (100%), 0 regressions

## Phase 13: Supply + Demand Network (v0.8 Network Layer)
- [x] T13.1 Model Expansion: Discrete `Farm/Plot`, staff-mediated `Buyer`, `BuyerRequirement`, and `SupplyMatch` models
- [x] T13.2 Database Migration: Alembic `0011_supply_demand_network`
- [x] T13.3 Schemas: `schemas/farm.py`, `schemas/buyer.py`, `schemas/matching.py`
- [x] T13.4 Rule-Based Yield Estimator: Agro-climatic benchmarks + soil/irrigation factors (`backend/app/services/yield_estimator.py`)
- [x] T13.5 Farm & Buyer Management Services with CSV Import Harness (`backend/app/services/farm_service.py`, `backend/app/services/buyer_service.py`, `backend/app/services/csv_import.py`)
- [x] T13.6 Semi-Automatic Demand-Supply Matching Engine (`backend/app/services/matching_service.py`)
- [x] T13.7 REST API v1 Routing: `/api/v1/farms`, `/api/v1/buyers`, `/api/v1/matching`
- [x] T13.8 WhatsApp Zero-Cost Inbound Match Queries & Staff-Confirmed Utility Nudges (`backend/app/services/bot.py`)
- [x] T13.9 Synthetic Erode Pilot Dataset: Multi-plot farms, commercial buyers, and requirements (`backend/scripts/seed_supply_demand.py`)
- [x] T13.10 Frontend Supply-Demand Management UI: Buyer registry, plot manager, and candidate matching drawer
- [x] T13.11 Comprehensive Integration & Regression Test Suite (`backend/tests/test_supply_demand_api_and_bot.py`)
- [x] T13.12 Checkpoint H: Supply + Demand Network Sign-Off
### Checkpoint H: Supply + Demand Network Sign-Off
- [x] Migration 0011 applied, multi-plot farms operational, semi-automatic matching verified, zero Erode pilot regressions

## Future Strategic Roadmap (v0.9 to v1.0)
- **Phase 16–17 (v0.9 State Command Center)**: State Agricultural Pulse dashboard, role-specific views (State Admin, District Admin, FPO, Analyst, Buyer, Farmer).
- **Phase 18–20 (v1.0 Tamil Nadu Agricultural Intelligence Platform)**: Integrated farmer PWA & WhatsApp intelligence network, province-wide scaling.

## Pilot Deployment
- [ ] 2-week pilot with 10–20 farmers from one FPO (runbook: `docs/PILOT_RUNBOOK.md`)
- [ ] Native-speaker review of Tamil copy and expand/adjust/stop decision (evaluation rubric: `docs/PILOT_RUNBOOK.md`)

# FPOLink MVP Sprint — Tasks M1–M4

Append to `tasks/todo.md`. IDs use the `M` prefix to avoid clashing with T0–T6.

Scope: Erode district, turmeric + banana, free sources only, WhatsApp-only bot.

**MVP definition:** one FPO admin logs in (Tamil-first), sees today's prices + 30-day trend + a forecast,

records harvests and sees the aggregate batch; a farmer asks the WhatsApp bot for a price and gets a Tamil/English reply.

**Out of scope for MVP:** buyer matching, maps, demand forecasting, anomaly detection, coconut, XGBoost tuning.

---

## Phase M0 — Pre-flight (do first, ~1 hour)

- [ ] **M0.1 Confirm latest work is pushed**

  - Run `git status` and `git log origin/main -3`; push anything unpushed.

  - Accept: public GitHub shows `tasks/`, `docs/`, Phase 5 files, CI green.

- [ ] **M0.2 Remove stale Telegram/legacy bits**

  - Delete `bot/` folder if empty, Telegram refs in README/config/`notifications/`, `python-jose` mentions.

  - Update GitHub repo description (drop "Telegram Bot").

  - Accept: `grep -ri telegram .` returns nothing outside git history/changelog.

## Phase M1 — Real price data (blocker)

- [ ] **M1.1 Verify OGD (data.gov.in Agmarknet) adapter against the live API**

  - Accept: one command fetches latest records for Erode-area markets and writes `raw_ingest` rows.

- [ ] **M1.2 Backfill history**

  - Backfill as many months as the source provides for turmeric + banana; use the manual CSV adapter for gaps.

  - Accept: ≥ 6 months of cleaned rows per crop per market with data; gap report printed.

- [ ] **M1.3 Normalize units and varieties**

  - Quintal vs kg, turmeric variety (finger/bulb), banana variety mapped via `varieties`.

  - Accept: every price row has a canonical unit (₹/quintal) and variety; tests cover conversions.

- [ ] **M1.4 Freshness metadata**

  - API returns `last_updated` and `source` per price.

  - Accept: `/prices/latest` includes both fields; test added.

- [ ] **M1.5 Scheduled daily ingest in worker**

  - Accept: worker ingests daily at configured IST time; failure logged to Sentry; idempotent re-runs.

- [ ] **M1.6 Data-health endpoint**

  - Rows per market per day, gaps, outliers removed.

  - Accept: `/admin/data-health` returns JSON; covered by a test.

**Checkpoint A:** `curl /prices/latest?crop=turmeric&market=erode` returns real, fresh, correctly-united data.

## Phase M2 — Honest forecasting

- [ ] **M2.1 Baseline forecaster**

  - Seasonal-naive + moving average with a simple confidence band, 7 and 30 day horizons.

  - Accept: `/forecast?crop=…` returns point + lower/upper; unit tests on synthetic data.

- [ ] **M2.2 Backtest harness**

  - Rolling-origin evaluation (MAE/MAPE) on a held-out window; store results in `model_versions`.

  - Accept: one command prints baseline metrics per crop.

- [ ] **M2.3 Optional: XGBoost/RandomForest challenger**

  - Only promoted if it beats the baseline on the backtest by a clear margin.

  - Accept: promotion rule coded; baseline stays default otherwise.

- [ ] **M2.4 Forecast logging and scoring**

  - Log every prediction to `forecast_log`; nightly job fills in actuals and error.

  - Accept: scored rows appear the day after actuals arrive.

- [ ] **M2.5 UI/API disclaimer text**

  - "Estimate, not advice" string in Tamil and English returned with every forecast.

**Checkpoint B:** backtest report committed to `docs/FORECAST_BACKTEST.md`.

## Phase M3 — Tamil-first dashboard on Vercel

- [ ] **M3.1 API client + auth flow** (login, token refresh, logout)

- [ ] **M3.2 Prices screen**: crop/market selector, 30-day chart, today's table, freshness badge, forecast band

- [ ] **M3.3 Harvest entry screen**: member picker, crop, quantity, expected date; validation in Tamil/English

- [ ] **M3.4 Batch summary screen**: aggregated harvest per crop/week, total quantity, member breakdown

- [ ] **M3.5 i18n pass**: Tamil default, English toggle, no untranslated strings (script that fails CI on missing keys)

- [ ] **M3.6 Mobile polish**: ≥ 44px touch targets, readable charts at 360px width, loading/empty/error states

- [ ] **M3.7 Deploy to Vercel**: `NEXT_PUBLIC_API_URL` env var, CORS allowlist on backend

  - Accept: public Vercel URL logs in against the hosted backend.

**Checkpoint C:** admin completes login → view price → add harvest → see batch on a phone.

## Phase M4 — Hosting, WhatsApp and pilot

- [ ] **M4.1 Pick and set up always-on backend host** (prod compose from T5.1; verify free-tier terms first)

  - Accept: `/health` green externally; retention + sweep jobs running.

- [ ] **M4.2 Seed admin from env vars, remove `admin123`; force password change on first login**

- [ ] **M4.3 WhatsApp price lookup (test number)**

  - Intents: price for crop (Tamil/English), "no data yet" reply, help text.

  - Accept: a real phone gets a correct Tamil reply for "மஞ்சள் விலை" within seconds; replies include date and source.

- [ ] **M4.4 DPDP basics**: consent text at registration, member data delete, WhatsApp opt-out handling

- [ ] **M4.5 End-to-end smoke test**: ingest → forecast → API → WhatsApp reply (CI job)

- [ ] **M4.6 README + screenshots**: WhatsApp-only, Argon2/PyJWT, correct clone URL, real setup steps

- [ ] **M4.7 Kill-switch drill**: trigger once per `docs/OPS_RUNBOOK.md`, confirm bot stops and recovers

- [ ] **M4.8 Pilot onboarding**: 1 FPO admin + 5–10 farmers, short Tamil how-to, feedback log

**Checkpoint D (MVP done):** pilot farmers receive real prices on WhatsApp; admin uses the dashboard; CI green; no secrets or default passwords in repo.

---

## Suggested order and timing

| Days | Work |

|------|------|

| 0 | M0 |

| 1–3 | M1 |

| 3–5 | M2 |

| 5–10 | M3 |

| 10–12 | M4.1–M4.3 |

| 12–14 | M4.4–M4.8 |

Parallelizable with subagents: M2 with M3.1–M3.2, and M4.4 with M4.6.
