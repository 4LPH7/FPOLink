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


## Final: Pilot
- [ ] 2-week pilot with 10–20 farmers from one FPO (runbook: `docs/PILOT_RUNBOOK.md`)
- [ ] Native-speaker review of Tamil copy and expand/adjust/stop decision (evaluation rubric: `docs/PILOT_RUNBOOK.md`)
