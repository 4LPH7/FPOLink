# FPOLink TN — Product Requirements Document (PRD)

Structured functional and non-functional requirements catalog for FPOLink TN.

---

## 1. Authentication & Security (AUTH)

- **REQ-AUTH-1**: User accounts must support four explicit roles: `admin`, `fpo_staff`, `farmer`, and `buyer`.
- **REQ-AUTH-2**: Authentication must use JSON Web Tokens (PyJWT) with configurable access token TTL and refresh token rotation.
- **REQ-AUTH-3**: Passwords must be securely hashed with Argon2id / Bcrypt salt; minimum 8 characters required.
- **REQ-AUTH-4**: Initial seed and staff accounts must enforce a mandatory password change on first login before accessing privileged endpoints (`password_change_required=true`).
- **REQ-AUTH-5**: Multitenant scoping must strictly isolate FPO staff operations to their assigned `fpo_id`.

---

## 2. Market Prices & Agricultural Intelligence (PRICE)

- **REQ-PRICE-1**: Automated ingestion must support OGD Agmarknet (daily mandi quotes) and CEDA Ashoka feeds.
- **REQ-PRICE-2**: All price records must be normalized to canonical ₹/quintal and ₹/kg with standard ISO dates.
- **REQ-PRICE-3**: Raw payloads must be stored in `raw_ingest` with SHA-256 checksums to support auditability and deterministic replay.
- **REQ-PRICE-4**: Outlier prices must be automatically detected using MAD (Median Absolute Deviation) z-scores.
- **REQ-PRICE-5**: Price forecasting must predict 7-day future price trajectories using LightGBM with graceful heuristic baseline fallbacks when series history is sparse.
- **REQ-PRICE-6**: Weather integration must fetch 7-day temperature, rainfall, and humidity forecasts via Open-Meteo for district headquarters.

---

## 3. Multi-Channel Messaging & Farmer Chat (BOT)

- **REQ-BOT-1**: Both WhatsApp Cloud API and Telegram Bot (`@Fpo_Link_Bot`) must be supported via a shared, transport-agnostic `BotEngine`.
- **REQ-BOT-2**: Conversations must default to Tamil (`ta`) with full native keyword recognition (e.g. `விலை`, `அறுவடை`, `வானிலை`), with dynamic switching to English (`en`).
- **REQ-BOT-3**: Farmers must be able to submit harvest notifications via a conversational step-by-step flow (crop, quantity, unit, expected date).
- **REQ-BOT-4**: Telegram bot must support seamless phone verification via native contact cards and auto-provisioning under default FPOs.
- **REQ-BOT-5**: DPDP Act compliance must enforce explicit opt-in consent and provide immediate opt-out via `நிறுத்து` / `STOP`.
- **REQ-BOT-6**: Inbound message retention must automatically purge chat messages older than 7 days, and conversation state older than 24 hours.

---

## 4. Supply & Demand Matching (SUPPLY_DEMAND)

- **REQ-SUPPLY-1**: Farmers must be able to register multiple land plots with acreage, crop variety, irrigation type, and soil profile.
- **REQ-SUPPLY-2**: Expected plot yields must be automatically calculated using agro-climatic norms and regional benchmarks.
- **REQ-SUPPLY-3**: Harvest batches must transition through audited states: `submitted` → `inspected` → `aggregated` → `sold`.
- **REQ-DEMAND-1**: FPO staff must be able to catalog verified institutional buyers and their active volume requirements.
- **REQ-MATCH-1**: The matching engine must score and rank candidate farm plots against buyer requirements using crop variety compatibility, delivery window overlap, and Haversine geographic distance.
- **REQ-MATCH-2**: Match suggestions must require human staff confirmation before notifying farmers.

---

## 5. FPO Cooperative Operations (TASKS)

- **REQ-TASK-1**: FPO staff must have an operational task board to assign, track, and resolve daily field activities.
- **REQ-TASK-2**: Tasks must support priority levels (`low`, `medium`, `high`, `urgent`), due dates, and statuses (`todo`, `in_progress`, `completed`, `cancelled`).
- **REQ-TASK-3**: Task actions must be audited and tenant-scoped to the active FPO.

---

## 6. Infrastructure & Deployment (INFRA)

- **REQ-INFRA-1**: The backend API must be deployed with HTTPS on an always-on cloud provider (Render / OCI).
- **REQ-INFRA-2**: Database must run on managed PostgreSQL 16 with zero migration drift across all Alembic revisions.
- **REQ-INFRA-3**: Automated test suite must maintain >90% coverage on critical paths with zero failing tests.
