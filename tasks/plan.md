# Implementation Plan: WhatsApp Integration for FPOLink TN

## Overview

Connect the tested WhatsApp bot skeleton (webhook, Tamil/English bot engine, 17 tests against fakes)
to the real FPOLink backend, then take it from "works with fakes" to a 2-week pilot with one FPO.
The bot lets a farmer message the FPO's WhatsApp number to get mandi prices, submit a harvest,
and opt in to a daily price digest. It is inbound-first to keep messaging costs near zero.

**Starting point (already true):** FastAPI + Postgres 16 + Alembic `0001`, Argon2 auth, farmer/FPO/
price/crop APIs, worker container, CI (`test` + `docker-smoke`, green), skeleton in
`whatsapp_skeleton/`. **Not yet true:** real price data is not loaded, harvest API/service is not
built, the skeleton has never touched Meta's live API, the frontend does not exist.

## Constraints

- Free sources/tools only. Official WhatsApp Cloud API used directly (no paid provider).
- WhatsApp only (no Telegram).
- Outbound messages cost money after free allowances (Meta changes rates often; India rates in the
  July 2026 guide: utility ₹0.115, marketing ₹0.8631; service messages become chargeable after a
  monthly free allowance from Oct 1, 2026). Verify current rates on Meta's pricing page.
- DPDP Act: farmer phone numbers and locations are personal data. Consent, minimisation, purge.

## Architecture Decisions

1. **Transport-agnostic bot.** `BotEngine` depends on `MessageChannel` + `BotServices` only. Keeps
   tests fast and lets us swap the transport later.
2. **Inbound-first.** Farmers ask, the bot answers. Proactive messages are limited to one utility
   template digest per farmer per day, sent only to opted-in farmers.
3. **Identity = WhatsApp number.** FPO staff create farmer records (phone, language); farmers do
   not self-register. No OTP needed because WhatsApp already verifies the number.
4. **State in Postgres** (dedup table, conversation state with TTL, outbound log). No Redis, so no
   extra infrastructure to host or pay for.
5. **Webhook acknowledges immediately, works in the background.** Start with FastAPI
   `BackgroundTasks` plus atomic dedup. Add a "received but not finished" sweep before pilot (T5.4)
   so a crash mid-processing does not lose a message.
6. **Cost guardrails are code, not policy.** Kill switch, per-number rate limit, monthly send cap,
   and a usage report from the outbound log.
7. **Real fixtures only.** Webhook fixtures are captured from Meta's test number, redacted, and
   recorded in `docs/data-provenance.md`. Hand-written payloads stay labelled `_synthetic`.
8. **All schedules in IST**; the worker container owns scheduled jobs (never the API process).

## Agent Working Rules (paste at the top of every agent task)

- Show command output for every claim: `pytest`, `ruff check`, `ruff format --check`, `alembic check`.
- Never write API keys, tokens, app secrets or real phone numbers to any file, log or fixture.
- Never call a fixture "real" unless it came from a live call; keep the provenance ledger current.
- One task per commit; tick the box in `tasks/todo.md`; stop at each checkpoint for human review.
- New behaviour needs a test that fails without it. DB behaviour is tested against real Postgres.

## Task List

### Phase 0: De-risk the external dependencies (start immediately, in parallel)

**T0.1 Decisions (human, S).** Answer the Open Questions below (number, Meta account owner, pilot FPO).
- Acceptance: answers written into this file.

**T0.2 Meta test setup and first send (human + agent, S).** Create the Meta app, add WhatsApp, use the
test number, add your phone as a recipient, send one message with `curl`.
- Acceptance: the message arrives on your phone. Verify: `curl` response contains a message id.
- Depends: none. This is the highest-risk external step, so do it first.

**T0.3 Capture real webhook payloads (S).** Run the API locally behind a free tunnel, set the webhook,
send from your phone: text (English and Tamil), a button tap, a voice note, an image, and a message
to trigger a status callback. Save redacted JSON to `backend/tests/fixtures/whatsapp/`.
- Acceptance: `parse_webhook` handles every captured file; unsupported types map to `unsupported`;
  status callbacks parse to nothing (or to a status object after T4.4).
- Verify: new parametrised test over the fixture folder; ledger updated.
- Files: `tests/fixtures/whatsapp/*.json`, `tests/test_whatsapp_fixtures.py`, `docs/data-provenance.md`.

**T0.4 Submit message templates for approval (human, S).** Create utility templates
`daily_price_digest` (ta, en). Approval takes time, so submit before you need them. Keep the wording
factual (crop, price, market, date), no promotional language, because Meta may reclassify a
template as marketing (about 7x the price).
- Acceptance: templates show as approved in the Meta dashboard.

**T0.5 Real price data loaded (prerequisite from the data plan).** CEDA key expires Sept 27, so load
TN turmeric/banana first, then run the coverage audit. The bot is only as useful as this data.

### Phase 1: Vertical slice, "farmer texts PRICE and gets a real price"

**T1.1 Import the skeleton into the repo (S).** Copy files, register the router, match the repo's
ruff settings, keep CI green.
- Acceptance: the 17 skeleton tests run in CI. Files: `app/messaging/*`, `app/services/bot.py`,
  `app/api/whatsapp.py`, `app/main.py`, `tests/test_whatsapp_bot.py`.

**T1.2 Migration: phone, language, consent, bot tables (M).** Add to farmers: normalised
`phone` (unique, last 10 digits), `lang`, `alerts_opt_in`, `alerts_opt_in_at`, `alerts_opt_out_at`.
New tables: `whatsapp_inbound(message_id pk, received_at, status)`, `conversation_state(wa_id pk, step,
data jsonb, updated_at)`, `outbound_messages(id, wa_id, category, template, status, created_at)`.
Normalise phones on farmer create/update in the API and backfill existing rows.
- Acceptance: `alembic upgrade head` and `alembic check` clean; duplicate phone rejected with a clear error.
- Verify: migration test on empty and populated DB.

**T1.3 `DbBotServices` for farmers, prices, dedup, state (M).**
- Price rule (decide and document): newest available date per crop for the FPO's district, showing
  the market and date; if the newest data is older than N days, say so in the reply.
- Acceptance: `first_time` is atomic under concurrent calls (test with two simultaneous inserts);
  state expires after 30 minutes; stale prices are flagged.
- Verify: tests against real Postgres, not mocks.

**T1.4 Wire the engine, settings and kill switch (S).** Replace `get_bot()`, add `WHATSAPP_ENABLED`,
validate settings at startup (refuse to start in production if enabled but secrets are missing,
same pattern as the `SECRET_KEY` check).
- Acceptance: disabled means webhook returns 503 and sends nothing; missing secrets fail startup.

**T1.5 Contract tests for outgoing payloads (S).** Mock Meta's send endpoint (`respx`) and assert exact
JSON for text, buttons (max 3, titles 20 chars) and templates.

**Checkpoint A: first end-to-end.** From your own phone: `PRICE` and `விலை` return real Erode prices in
the right language; a duplicate webhook delivery is ignored; CI green; `git grep` finds no secrets.

### Phase 2: Onboarding, identity and consent

**T2.1 Invite link (S).** `GET /api/farmers/{id}/whatsapp-invite` returns a `wa.me` link with prefilled
"Hi". Farmer taps it, which opens the conversation (free service window).

**T2.2 First-contact notice (S).** First message from a registered farmer gets a short notice: what
the bot does, which data is stored, who to contact, how to stop (`STOP`). Store `notice_sent_at`.

**T2.3 Consent and STOP (S).** `ALERTS ON/OFF` and `STOP` (also Tamil `நிறுத்து`) work from any state
and take effect immediately; timestamps stored; opted-out farmers never receive templates.
- Verify: tests for each keyword, in state and out of state.

**T2.4 Scoping (S).** Bot only uses data for the farmer's FPO and district; unknown numbers get the
generic reply and no data. Test with two FPOs.

### Phase 3: Harvest submission by chat

**T3.1 Harvest service and API (M).** Depends on the harvest module from the product roadmap (Days 12-14), which is not built yet.
Validation (quantity bounds, grade A/B/C, date), status `SUBMITTED`, unique `source_message_id` so a
retry cannot double-submit.
- Verify: API tests plus a retry test.

**T3.2 Wire the harvest flow (S).** `submit_harvest` in `DbBotServices` calls the service; FPO staff
see the record via the existing API.

**T3.3 Robustness (M).** Per-number rate limit (for example 30 messages per 10 minutes), reply to voice
notes and images with "please type your message", cap retries per step, restart with `MENU`.
- Acceptance: flooding one number stops replies after the limit and logs once, not per message.

**Checkpoint B.** A farmer submits a harvest on WhatsApp; FPO staff see it; state expiry, limits and
retry-safety are tested.

### Phase 4: Proactive messages (digest and alerts) with cost control

**T4.1 Status webhooks (S).** Parse delivered/read/failed statuses, update `outbound_messages`, mark
numbers unreachable after repeated failures.

**T4.2 Daily digest job in the worker (M).** After ingestion and anomaly checks, at about 07:30 IST,
send the approved template to opted-in farmers, only for crops they grow (from farms), only if fresh
data exists. Unique `(farmer, date, type)` so a rerun cannot double-send.
- Acceptance: rerunning the job sends nothing new; no fresh data means no send.

**T4.3 Price-move alert (S).** At most one alert per farmer per day when the change passes a threshold.

**T4.4 Usage report, caps and circuit breaker (M).** `GET /api/admin/whatsapp/usage?month=` counts
messages by category and estimates cost from rates in config (never hard-coded). Monthly send cap
stops sending and alerts an admin.

**Checkpoint C.** A dry run with three test farmers: digest arrives once, STOP is honoured, the usage
report matches Meta's dashboard within a small margin.

### Phase 5: Production readiness

**T5.1 Deploy the webhook (M).** Stable HTTPS URL (free VM with Caddy, or Cloudflare Tunnel), env-based
secrets, health check, Meta webhook pointed at it.

**T5.2 Meta production setup (human, wait time unknown).** Own number on the Cloud API, business
verification with FPO documents, System User token, payment method, display name. Start this early:
verification can take days.

**T5.3 Security and privacy pass (M).** Signature and empty-secret tests, PII masking in logs, secret
scanning and push protection on, token rotation notes, retention purge (inbound log 7 days,
conversation state, outbound log 12 months), dependency audit.

**T5.4 At-least-once processing (S).** Sweep `whatsapp_inbound` rows stuck in `received` and reprocess
them; test by killing processing mid-message.

**T5.5 Observability and runbook (S).** Counters for inbound, outbound, failures; alert when webhook
errors or send failures spike; runbook for token expiry, Meta outage, kill switch.

**Checkpoint D.** Staging E2E script passes with a real phone; runbook reviewed.

### Phase 6: Pilot (10-20 farmers, one FPO, 2 weeks)

**T6.1 Run the pilot (human).** Track weekly active farmers, median reply time, harvest submissions by
chat versus manual, digest delivery rate, opt-outs, and cost per farmer.

**T6.2 Native-speaker review of Tamil copy and gate decision (human).** Expand, adjust, or stop.

### Later backlog (only if the pilot justifies it)

Voice-note input (Tamil speech recognition), list messages for more than 3 options, WhatsApp Flows for
forms, multi-FPO, buyer requirements by chat.

## Testing Strategy

| Layer | How |
|---|---|
| Unit | Existing skeleton tests, intents, parsing, formatting |
| Service | `DbBotServices` against real Postgres in CI (atomic dedup, TTL, price rule) |
| Contract | Real captured webhook payloads in; exact JSON out (mocked Meta API) |
| End-to-end | Manual script with a real phone at each checkpoint; no live secrets in CI |
| Cost/abuse | Rate limit, kill switch, cap and duplicate-send tests |

CI never receives WhatsApp secrets. Anything needing live Meta access is manual and recorded in the plan.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Meta verification or template approval is slow or rejected | High | Start T0.2, T0.4, T5.2 first; keep the bot useful inbound-only meanwhile |
| Template reclassified as marketing (price about 7x) | Med | Factual wording; monitor category in dashboard; usage report |
| Message cost exceeds expectation after Oct 1 pricing change | Med | Combined replies, one digest per day, caps and circuit breaker |
| Number flagged or banned (spam reports) | High | Opt-in only, STOP works instantly, no promotion, quality rating watched |
| Wrong or stale price shown to a farmer | High | Always show date and market; flag stale data; forecasts only with ranges and after the accuracy scorecard |
| Farmers prefer voice or low text literacy | Med | Buttons first; voice-note support after pilot feedback |
| Token expiry or API version retirement | Med | System User token, version in config, runbook and calendar reminder |
| Personal data exposure | High | Masked logs, retention purge, scoped queries, secret scanning |
| Agent claims unverified work | Med | Working rules above; evidence required at checkpoints |

## Open Questions (need your answers)

1. Which number will the bot use? It must not be active on a normal WhatsApp app (ideally a dedicated SIM).
2. Who owns the Meta business account: you or the FPO? Business verification needs the owner's documents.
3. Which FPO and which 10-20 farmers will run the pilot?
4. Do harvest submissions need FPO staff approval before they count?
5. Default language for new farmers: Tamil or English?
6. Who reviews the Tamil text?

## Dates that matter

- **Sept 27, 2026:** CEDA API key expires. Load real data before this.
- **Sept 30 / Oct 1, 2026:** reported payment-method deadline and start of chargeable service messages. Verify on Meta's site.
