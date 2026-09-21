# WhatsApp Integration: Task List

Details, acceptance criteria and verification for each task are in `tasks/plan.md`.

## Phase 0: De-risk external dependencies (start now, in parallel)
- [ ] T0.1 Answer the open questions (number, Meta owner, pilot FPO)
- [ ] T0.2 Meta test setup and first successful send
- [ ] T0.3 Capture real webhook payloads as fixtures (+ provenance ledger)
- [ ] T0.4 Submit `daily_price_digest` templates (ta, en) for approval
- [ ] T0.5 Real price data loaded (CEDA before Sept 27) + coverage audit

## Phase 1: Vertical slice, PRICE returns a real price (Code-Complete, Pending Live Verification)
- [x] T1.1 Import skeleton into the repo, CI green
- [x] T1.2 Migration: phone/lang/consent fields + bot tables
- [x] T1.3 `DbBotServices` (farmers, prices, atomic dedup, state TTL)
- [x] T1.4 Wire engine, settings validation, kill switch
- [x] T1.5 Contract tests for outgoing payloads
### Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo
> [!NOTE]
> Checkpoint A remains open: explicitly requires real phone testing, captured real Meta webhook payload fixtures for T0.3, and verified real market price backfill for T0.5 before marking the checkpoint complete.
- [ ] Checkpoint A verified by human with real phone testing, captured real Meta webhook payload fixtures (T0.3), and verified real market price backfill (T0.5)

## Phase 2: Onboarding, identity, consent
- [x] T2.1 wa.me invite link endpoint
- [x] T2.2 First-contact notice
- [x] T2.3 ALERTS ON/OFF and STOP from any state
- [x] T2.4 FPO/district scoping

## Phase 3: Harvest by chat
- [ ] T3.1 Harvest service + API (idempotent by message id)
- [ ] T3.2 Wire harvest flow to the service
- [ ] T3.3 Rate limit, unsupported types, retry caps
### Checkpoint B: harvest submitted by chat is visible to FPO staff
- [ ] Reviewed by human

## Phase 4: Digest and alerts with cost control
- [ ] T4.1 Status webhooks and unreachable numbers
- [ ] T4.2 Daily digest worker job
- [ ] T4.3 Price-move alert (max 1 per farmer per day)
- [ ] T4.4 Usage report, monthly cap, circuit breaker
### Checkpoint C: dry run with 3 test farmers
- [ ] Reviewed by human

## Phase 5: Production readiness
- [ ] T5.1 Deploy webhook behind stable HTTPS
- [ ] T5.2 Meta production setup (number, verification, token, payment)
- [ ] T5.3 Security and privacy pass
- [ ] T5.4 At-least-once processing sweep
- [ ] T5.5 Observability and runbook
### Checkpoint D: staging E2E with a real phone
- [ ] Reviewed by human

## Phase 6: Pilot
- [ ] T6.1 Run 2-week pilot (10-20 farmers, one FPO)
- [ ] T6.2 Tamil copy review and expand/adjust/stop decision
