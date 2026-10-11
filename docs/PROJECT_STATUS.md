# FPOLink Project Status

Current deployment snapshot (2026-10-11). GitHub Actions CI and the Vercel deployment check passed for the latest production Compose change; neither verifies a live backend or farmer operations. Docker VM + Cloudflare Tunnel is the selected production host, but the public domain is not set up and VM access/provisioning is unverified. The Render blueprint remains staging-only.

The UI and historical ingestion figures below are from earlier engineering verification and have not been remeasured against a current production deployment.

## Phase status

| Phase | Status | Evidence / gate |
|---|---|---|
| CI, seed data, and account safety | Latest code CI passed | GitHub Actions ran frontend build, backend migrations/tests/lint, and Docker smoke successfully for the latest production Compose change; production bootstrap uses the shared hardened admin creator with mandatory first-login password change. |
| Responsive dashboard and authentication UI | Complete & Verified on CI | Next.js 14 production build passed across all 14 routes; bilingual Tamil/English UI; mobile drawer and touch targets ($\ge 44\text{px}$); API health check context; password change flow functional; `/prices` dashboard renders 59 verified live commodity quotes. |
| Real price data ingestion and backfill | Complete & Live Ingested | 1,147 verified Agmarknet rows in database; 620 historical records (Apr–Oct 2026) + 520 live September 2026 records across 11 crops (Turmeric, Banana, Coconut, Tomato, Tapioca, Maize, Onion, Green Chilli, Ladies Finger, Brinjal, Paddy) spanning Erode, Coimbatore, Salem, Namakkal, Dharmapuri, and Thirupur mandis. CEDA API client hardened with official key, metadata caching, and 40-req/hour rate-limiting awareness. |
| Bot conversation and harvest flow | Locally exercised; live channel unverified | `verify_mvp_e2e.py` uses a mock transport with the shared BotEngine and database. It does not verify Telegram/WhatsApp provider webhooks or delivery to a physical phone. |
| Staging deployment | Configured; live state unverified | `render.yaml` defines a free-tier staging API. Its administrator is provisioned explicitly once after deployment; this is not the production hosting setup. |
| Production deployment | Not deployed/verified | Docker VM access/provisioning, a public Cloudflare DNS zone/API hostname, production secrets, encrypted offsite backup/restore, and live health/data-ingestion checks remain. |
| Farmer channel | Telegram configured in code; live account unverified | Telegram is the active default channel. Set the production bot token and public HTTPS API URL, verify the webhook, and test from a farmer account. WhatsApp remains optional pending Meta onboarding. |
| Two-week Erode pilot and feedback | Not run | Run the Telegram-focused pilot checklist in `docs/PILOT_RUNBOOK.md` after staging and channel verification. |

## Next actions

1. Provision the Docker VM and domain/Cloudflare zone; configure DNS/Tunnel routing, production secrets, and the dashboard API proxy.
2. Deploy, seed production reference data, create the administrator, and verify Telegram, HTTPS health, and fresh real market prices.
3. Set up encrypted offsite backups and retention, then complete and record a restore drill.
4. Verify consent, opt-out, Tamil interactions, and field workflows with farmers; record the 14-day Erode pilot. WhatsApp remains optional.
