# FPOLink TN — Current Workflow State

Live project state tracker for GSD workflow operations.

---

## 1. Project Overview

- **Project**: FPOLink TN
- **Active Milestone**: `M-Series MVP Sprint`
- **Active Milestone**: `M-Series MVP Sprint`
- **Active Phase**: `Phase M5 — Statewide Multi-Crop & District-Dynamic UI (Modern Web & JetBrainsMono)` (COMPLETE)
- **Current Branch**: `main`
- **Git Commit**: `HEAD`

---

## 2. Key Status Metrics

| Metric | Status | Details |
|---|---|---|
| **Render API** | 🟢 Live | `https://fpolink-api.onrender.com/api/health` → `db: ok` |
| **Render Database** | 🟢 Seeded | 43 tables migrated, 38 districts, 46 markets, 20 crops, 4 buyers, 1 FPO |
| **Admin User** | 🟢 Verified | Phone `8072845239`, Role `admin`, Language `ta`, Token verified |
| **Telegram Bot** | 🟢 Active | `@Fpo_Link_Bot` webhook verified with Render backend |
| **Test Suite** | 🟢 269 / 269 | 100% pass rate in 27.6 seconds (PostgreSQL 18) |
| **Frontend Build** | 🟢 16/16 Pages | Next.js 14 static export & route generation clean; 0 TS errors |
| **Tenant Isolation** | 🟢 11/11 Suites | Cross-FPO, District Admin, Bulk CSV, Matching, Token & Password Rotation verified |
| **Alembic Drift** | 🟢 0 Drift | Migrations 0001–0013 applied and verified |

---

## 3. Recent Session Accomplishments

1. **Phase M5 Statewide Multi-Crop, District-Dynamic UI & Typography Optimization**:
   - Switched web application typography to **JetBrainsMono** (`next/font/google` `JetBrains_Mono` + `'Noto Sans Tamil'` fallback for Tamil script preservation).
   - Applied `modern-web-guidance` best practices: `font-size-adjust: from-font;` for visually stable font fallbacks (zero-CLS), and `.content-visibility-auto` utility.
   - Decoupled locked-in crops (Turmeric, Banana, Coconut) across dashboard aggregation cards, price history charts, forecast charts, and arbitrage selector.
   - Implemented dynamic statewide district selection context (`DistrictProvider`) allowing seamless filtering across all 38 Tamil Nadu districts in Header, Prices, Farmers, and Buyers pages.
   - Expanded crop dictionaries in `i18n/en.json` and `i18n/ta.json` with bilingual support for all 20 Tier-A crops and dynamic unit pricing resolution (₹/kg, ₹/qtl, ₹/t).
   - Verified frontend static build (`npm run build`, 16/16 routes) and backend test suite (269/269 passing).
2. **Phase M4 Tenant Isolation & Security Audits**:
   - Upgraded `verify_fpo_access` with DB-backed `district_admin` scoping and district matching.
   - Enforced tenant verification on all farmer, FPO, harvest, task, buyer, and candidate matching routes.
   - Hardened `backend/scripts/create_admin.py` with $\ge 12$-character OWASP password complexity, rejection of common default passwords, and mandatory password rotation on first login.
   - Hardened CORS configuration to disallow wildcard `*` origins in production (`validate_production_secrets`).
   - Authored comprehensive test suite `backend/tests/test_tenant_isolation_security.py` (11 new tests, all passing).
   - Produced exhaustive security audit report at `docs/SECURITY_AUDIT.md`.
3. **Phase M3 Arbitrage & Transport Realization**: Upgraded engine with vehicle profiles, cost deductions, variety matching, and uncertainty scoring (`docs/ARBITRAGE_SPEC.md`).
4. **Phase M2 Honest Forecasting**: Completed walk-forward backtest framework and rolling baseline promotion rules (`docs/FORECAST_BACKTEST.md`).
5. **Phase M1 Data Provenance**: Verified OGD & CEDA pipelines with explainable data quality scoring.

---

## 4. Immediate Next Steps

1. **Phase M5 / Next Milestones**: Complete end-to-end user journeys and field pilot verification.
2. **Frontend Deployment**: Ensure production frontend deployment with restricted CORS origin configuration.
