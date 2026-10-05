# FPOLink Project Status

Updated 2026-10-04 from the `codex/mvp-readiness` branch. Branch pushed to GitHub with remote GitHub Actions CI passing 100%.

## Phase status

| Phase | Status | Evidence / gate |
|---|---|---|
| CI, seed data, and account safety | Complete & Verified on CI | GitHub Actions CI passed; 215 backend tests passed; `alembic check` 0 drift; Argon2id mandatory password rotation enforced via migration `0012`; Farmer registration hardened with atomic commit and error payload formatting (zero crash); All 13 CLI scripts fortified with UTF-8 console encoding; Ruff format and check 100% clean on all 206 backend files. |
| Responsive dashboard and authentication UI | Complete & Verified on CI | Next.js 14 production build passed across all 14 routes; bilingual Tamil/English UI; mobile drawer and touch targets ($\ge 44\text{px}$); API health check context; password change flow functional; `/prices` dashboard renders 59 verified live commodity quotes. |
| Real price data ingestion and backfill | Complete & Live Ingested | 1,147 verified Agmarknet rows in database; 620 historical records (Apr–Oct 2026) + 520 live September 2026 records across 11 crops (Turmeric, Banana, Coconut, Tomato, Tapioca, Maize, Onion, Green Chilli, Ladies Finger, Brinjal, Paddy) spanning Erode, Coimbatore, Salem, Namakkal, Dharmapuri, and Thirupur mandis. CEDA API client hardened with official key, metadata caching, and 40-req/hour rate-limiting awareness. |
| MVP end-to-end user journey | Verified | `verify_mvp_e2e.py` passed: system baseline $\to$ Tamil WhatsApp price query ("மஞ்சள் விலை") $\to$ 5-turn interactive harvest flow $\to$ DB persistence $\to$ staff dashboard visibility. |
| Live WhatsApp & staging HTTPS deployment | Blocked on credentials/host | Awaiting always-on host with HTTPS (Oracle Cloud / Cloudflare Tunnel / Vercel / Netlify) and Meta Cloud API credentials for physical phone testing. |
| Two-week Erode pilot and feedback | Ready for deployment | Pilot runbook prepared (`docs/PILOT_RUNBOOK.md`); cohort onboarding protocol ready for 1 coordinator and 5–10 farmers. |

## Next actions

1. **Deploy Frontend on Vercel / Netlify**: Link GitHub repository `4LPH7/FPOLink` to Vercel/Netlify for automatic frontend deployments with `NEXT_PUBLIC_DEFAULT_LANG=ta`.
2. **Deploy Always-On Backend with HTTPS**: Host `docker-compose.prod.yml` on an always-on VM (e.g. Oracle Cloud Always-Free) with Cloudflare Tunnel (`https://api.fpolink.org`) or Render.
3. **Configure Meta WhatsApp Cloud API**: Add Meta test credentials to production `.env` and execute physical smartphone verification in Tamil ("மஞ்சள் விலை").
4. **Execute 14-Day Erode FPO Pilot**: Onboard 1 coordinator and 5–10 farmers with DPDP consent per `docs/PILOT_RUNBOOK.md`.
