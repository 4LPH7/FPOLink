# Phase 5 — Production Readiness: CONTEXT.md

> Decisions extracted through discuss-phase on 2026-09-23. All gray areas resolved.
> Downstream agents (researcher, planner, executor) should treat these as locked constraints.

---

## Prior Decisions Carried Forward

These are already implemented and tested — **do not re-ask or re-decide**:

| Decision | Evidence |
|---|---|
| WhatsApp only (no Telegram) | `tasks/plan.md` constraint #2 |
| HMAC SHA-256 signature verification on webhook POST | `app/messaging/whatsapp_cloud.py:verify_signature()` |
| PII masking via `mask(wa_id)` across all WhatsApp services | 17 call sites in 6 service files |
| Production secret validation refuses defaults | `Settings.validate_production_secrets()` |
| `SENTRY_DSN` config placeholder exists | `app/config.py` L94 |
| Docker Compose: 4 services (postgres, backend, worker, frontend) | `docker-compose.yml` |
| Health check at `GET /api/health` | `app/main.py` L60-62 |
| CI: test + docker-smoke + alembic check + ruff | `.github/workflows/ci.yml` |
| Worker runs APScheduler in dedicated container | `app/worker.py`, `docker-compose.yml` worker service |
| Kill switch: `WHATSAPP_ENABLED` flag + 503 on webhook | `app/config.py` L61, `app/api/whatsapp.py` |
| WhatsApp inbound dedup via `WhatsAppInbound.message_id` PK | `app/services/db_bot_services.py:first_time()` |
| Alembic migrations: 5 revisions, linear chain, all ≤ 32 chars | `backend/alembic/versions/` |

---

## Decisions Made in This Discussion

### D1: Deployment Strategy — Cloudflare Tunnel

- **Choice:** Cloudflare Tunnel (`cloudflared`) as a sidecar container in docker-compose
- **Rationale:** Free, no VM ports to open, zero TLS config, ideal for pilot phase
- **Scope:** Full deployment kit:
  1. `docker-compose.prod.yml` — production override (no `--reload`, no volume mounts, healthchecks on backend/worker)
  2. Cloudflare Tunnel sidecar service in the production compose
  3. Setup script / documentation for tunnel configuration
- **Route:** `api.<domain>` → `backend:8000`

### D2: Meta Production Checklist

- **Choice:** Generate `docs/META_PRODUCTION_CHECKLIST.md`
- **Content:** Step-by-step human runbook with links for:
  - WABA registration and phone number setup
  - Business verification document submission
  - System User permanent token creation
  - Template submission (`daily_price_digest` in ta/en)
  - Payment method setup
  - Webhook URL configuration pointing at the Cloudflare Tunnel endpoint

### D3: Data Retention Policy

- **Choice:** Confirm plan defaults with worker cron implementation
- **Retention windows:**
  | Table | Retention | Reason |
  |---|---|---|
  | `whatsapp_inbound` | 7 days | DPDP minimization; dedup only needs recent rows |
  | `conversation_state` | 24-hour TTL sweep | Abandoned flows; lazy on-read already has 30-min TTL |
  | `outbound_messages` | 12 months | Billing audit trail and usage reports |
- **Implementation:** New `run_data_retention()` function in `app/worker.py`, scheduled daily at 03:00 IST
- **Deletion strategy:** Hard DELETE with batch size to avoid long locks

### D4: At-Least-Once Processing Sweep

- **Choice:** 10-minute interval sweep, 5-minute age threshold, max 3 retries
- **Two-part fix required:**
  1. **Status lifecycle:** Update `WhatsAppInbound.status` from `received` → `processed` after successful handling, or `received` → `failed` on exception in `BotEngine._handle()`
  2. **Sweep job:** New `run_inbound_sweep()` in worker, every 10 minutes:
     - Query `whatsapp_inbound WHERE status = 'received' AND received_at < now() - 5 minutes`
     - Add `retry_count` column (INTEGER DEFAULT 0) to `WhatsAppInbound`
     - Reprocess each row (increment retry_count); if retry_count ≥ 3, mark `failed`
- **Migration:** New Alembic migration `0005_phase5_production` adding `retry_count` to `whatsapp_inbound`

### D5: Observability — Sentry Init + DB Health Check

- **Choice:** Two items only (keeping it minimal for pilot):
  1. **Sentry:** Call `sentry_sdk.init(dsn=settings.SENTRY_DSN)` in both `app/main.py` and `app/worker.py`. Only initializes if `SENTRY_DSN` is non-empty.
  2. **Health check upgrade:** `GET /api/health` should execute `SELECT 1` against Postgres and return `{"status": "ok", "db": "ok"}` or `{"status": "degraded", "db": "error", "detail": "..."}`.
- **Explicitly deferred:** Prometheus counters, structlog, `/metrics` endpoint — revisit after pilot.

### D6: Ops Runbook — Kill Switch Procedure

- **Choice:** Minimal `docs/OPS_RUNBOOK.md` with kill switch section only
- **Content:**
  - How to disable WhatsApp instantly (`WHATSAPP_ENABLED=false` → restart backend/worker containers)
  - What the kill switch affects (webhook returns 503, digest/alert jobs skip sending, inbound messages are not processed)
  - How to re-enable and verify

### D7: `.env.example` Update

- **Choice:** Complete `.env.example` with ALL current `Settings` fields
- **Additions needed** (missing from current file):
  - `ENVIRONMENT=development`
  - `WHATSAPP_ENABLED=true`
  - `WHATSAPP_VERIFY_TOKEN=`
  - `WHATSAPP_APP_SECRET=`
  - `WHATSAPP_ACCESS_TOKEN=`
  - `WHATSAPP_PHONE_NUMBER_ID=`
  - `WHATSAPP_BOT_PHONE=919876543210`
  - `WHATSAPP_API_VERSION=v23.0`
  - `WHATSAPP_RATE_SERVICE_INR=0.00`
  - `WHATSAPP_RATE_UTILITY_INR=0.35`
  - `WHATSAPP_RATE_MARKETING_INR=0.85`
  - `WHATSAPP_RATE_AUTH_INR=0.15`
  - `WHATSAPP_MONTHLY_SEND_CAP=5000`
  - `WHATSAPP_MONTHLY_BUDGET_INR=2000.0`
  - `WHATSAPP_MAX_CONSECUTIVE_FAILURES=3`
  - `WHATSAPP_PRICE_MOVE_THRESHOLD_PCT=5.0`
  - `CORS_ORIGINS=http://localhost:3000`
  - `DEFAULT_CROPS=turmeric,banana,coconut`
- **Removals:** `TELEGRAM_BOT_TOKEN` (WhatsApp only, no Telegram)
- **Comments:** Group by section with descriptive comments

---

## Codebase Assets to Reuse

| Asset | Location | Reuse |
|---|---|---|
| `mask(wa_id)` PII helper | `app/messaging/base.py` | Use in any new logging |
| `Settings.validate_production_secrets()` | `app/config.py` | Extend if adding new required production vars |
| Worker scheduler pattern | `app/worker.py` | Add retention and sweep jobs in same pattern |
| Dedup `first_time()` | `app/services/db_bot_services.py` | Extend with status lifecycle |
| `sentry-sdk[fastapi]` | `requirements.txt` | Already installed, just needs init call |
| `WhatsAppInbound.status` column | `app/models/whatsapp.py` | Lifecycle: received → processed/failed |

---

## Deferred Ideas (out of Phase 5 scope)

- Prometheus metrics / `/metrics` endpoint
- Structured logging with `structlog`
- Token rotation automation
- Number flagging / quality rating monitoring
- Cost spike runbook (circuit breaker already handles this in code)
- Incident response template
- Frontend deployment / CDN setup

---

## Next Step

Run `gsd plan-phase 5` to create the implementation plan with task breakdown, file changes, and verification steps.
