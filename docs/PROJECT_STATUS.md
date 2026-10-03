# FPOLink Project Status

Updated 2026-10-03 from the local `codex/mvp-readiness` checkout. The commits below are local; no changes were pushed and no remote GitHub Actions run was triggered.

## Phase status

| Phase | Status | Evidence / gate |
|---|---|---|
| CI, seed data, and account safety | Complete locally | `43fb936`; migrations and `alembic check` passed; both reference seed scripts completed; 210 backend tests passed on the local Python runtime; Ruff passed. |
| Responsive dashboard and authentication UI | Complete locally | `767aac8`; Next.js production build passed; Docker API health, registration, login, and authenticated profile checks passed; Python 3.11 container tests passed 209 with one environment-file test skipped. |
| Staging ingestion and forecast validation | Blocked | CEDA returned HTTP 401 for a read-only Erode price query over 2026-04-03–2026-10-03. `OGD_API_KEY` is absent. The configured API host is localhost, so no staging instance was available. |
| Live WhatsApp, harvest review, opt-out, digest, Tamil, and HTTPS checks | Blocked | Meta credentials, a staging host, and an authorized real-phone test recipient are not configured in this environment. Mocked contract and flow tests pass, but they do not prove delivery on a real phone. |
| Two-week Erode pilot and post-pilot decisions | Not started | No farmer cohort or staff pilot feedback has been recorded. |

The seed script now tags its short illustrative price rows `demo_seed`; those seven local examples are not live market coverage. Forecast tests cover the sparse-series fallback, but no production forecast has been evaluated against verified Erode history.

## Next actions

1. Renew the CEDA credential or configure an OGD API key. Ingest turmeric and banana prices for Erode and nearby markets, then verify source lineage, latest observation date, market coverage, and six-month history.
2. Configure an HTTPS staging host and backend URL. Apply migrations and repeat ingestion, freshness, coverage, and forecast checks against staging data.
3. Configure Meta test-number credentials and an authorized test phone. Complete inbound/outbound WhatsApp, harvest submission and staff review, opt-out, digest delivery, and Tamil-language review over HTTPS.
4. Onboard 10–20 Erode farmers with consent and run the planned two-week pilot. Track engagement, message delivery, data accuracy, operating cost, and farmer feedback.
5. Update the roadmap and README using measured pilot outcomes, then choose the next product phase with FPO staff and farmers.
