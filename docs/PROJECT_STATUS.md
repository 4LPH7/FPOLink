# FPOLink Project Status

Historical engineering snapshot dated 2026-10-04 from the `codex/mvp-readiness` branch. The 2026-10-11 deployment-hardening commit `f07524c` is on `main` and its Vercel deployment check passed; this does not verify backend deployment or live farmer operations. The Render blueprint is a staging configuration. Production hosting, live credentials, and field-pilot results remain external launch gates.

## Phase status

| Phase | Status | Evidence / gate |
|---|---|---|
| CI, seed data, and account safety | Complete & Verified on CI | GitHub Actions CI passed; 215 backend tests passed; `alembic check` 0 drift; Argon2id mandatory password rotation enforced via migration `0012`; Farmer registration hardened with atomic commit and error payload formatting (zero crash); All 13 CLI scripts fortified with UTF-8 console encoding; Ruff format and check 100% clean on all 206 backend files. |
| Responsive dashboard and authentication UI | Complete & Verified on CI | Next.js 14 production build passed across all 14 routes; bilingual Tamil/English UI; mobile drawer and touch targets ($\ge 44\text{px}$); API health check context; password change flow functional; `/prices` dashboard renders 59 verified live commodity quotes. |
| Real price data ingestion and backfill | Complete & Live Ingested | 1,147 verified Agmarknet rows in database; 620 historical records (Apr–Oct 2026) + 520 live September 2026 records across 11 crops (Turmeric, Banana, Coconut, Tomato, Tapioca, Maize, Onion, Green Chilli, Ladies Finger, Brinjal, Paddy) spanning Erode, Coimbatore, Salem, Namakkal, Dharmapuri, and Thirupur mandis. CEDA API client hardened with official key, metadata caching, and 40-req/hour rate-limiting awareness. |
| Bot conversation and harvest flow | Locally exercised; live channel unverified | `verify_mvp_e2e.py` uses a mock transport with the shared BotEngine and database. It does not verify Telegram/WhatsApp provider webhooks or delivery to a physical phone. |
| Staging deployment | Configured; live state unverified | `render.yaml` defines a free-tier staging API. Its administrator is provisioned explicitly once after deployment; this is not the production hosting setup. |
| Production deployment | Not deployed/verified | Needs a persistent backend/database host, public HTTPS domains, production secrets, backup and restore checks, and live health/data-ingestion verification. |
| Farmer channel | Telegram configured in code; live account unverified | Telegram is the active default channel. Set the production bot token and public HTTPS API URL, verify the webhook, and test from a farmer account. WhatsApp remains optional pending Meta onboarding. |
| Two-week Erode pilot and feedback | Not run | Run the Telegram-focused pilot checklist in `docs/PILOT_RUNBOOK.md` after staging and channel verification. |

## Next actions

1. Choose a persistent production host, configure backup/restore, DNS/TLS, production secrets, and the staff dashboard's HTTPS API proxy.
2. Set `TELEGRAM_BOT_TOKEN` and `PUBLIC_API_URL`, seed only production reference data, and provision the administrator once.
3. Verify health, live market-data freshness, Tamil interactions, consent and opt-out with physical farmer accounts.
4. Execute and record the 14-day Erode pilot in `docs/PILOT_RUNBOOK.md`; treat WhatsApp setup as optional unless the FPO chooses that channel.
