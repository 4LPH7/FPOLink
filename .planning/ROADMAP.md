# FPOLink TN — Product Roadmap

Milestones, phases, delivery status, and verification evidence for FPOLink TN.

---

## Milestone History & Status Overview

```
Milestone v0.5 (Statewide Data Network)       ───► [COMPLETE & SEEDED]
Milestone v0.6 (Auth & Management Dashboard)   ───► [COMPLETE & VERIFIED]
Milestone v0.7 (Intelligence & Bot Channels)   ───► [COMPLETE & INTEGRATED]
Milestone v0.8 (Supply + Demand & FPO Tasks)   ───► [COMPLETE & SEEDED]
Milestone v0.9 (Cloud Hosting & Erode Pilot)   ───► [IN PROGRESS (90%)]
Milestone v1.0 (Statewide Expansion & Voice)   ───► [PLANNED]
```

---

## Milestone Details

### Milestone v0.5: Statewide Data Network
- **Goal**: Establish canonical data foundation across all 38 districts of Tamil Nadu.
- **Phases**:
  - [x] **Phase 1**: Statewide Geography & Market Ontology (38 revenue districts, taluks, 46 regulated markets).
  - [x] **Phase 2**: Commodity Ontology & Alias Resolution (20 commodities, Tamil phonetic aliases, varieties).
  - [x] **Phase 3**: Automated Mandi Ingestion (OGD Agmarknet API adapter, CEDA Ashoka client, MandiPrices).
- **Status**: **Completed**. Verified with 1,147+ real price rows in database.

### Milestone v0.6: Authentication & Management Dashboard
- **Goal**: Secure multi-role web dashboard for FPO administrators and staff.
- **Phases**:
  - [x] **Phase 4**: Security, RBAC & Token Auth (JWT, Argon2id/Bcrypt, role boundaries).
  - [x] **Phase 5**: FPO Operations & Farmer Management UI (Next.js 14 App Router, 16 routes, Tamil-first i18n).
  - [x] **Phase 6**: Price History & Trend Analytics Visualizations.
- **Status**: **Completed**. All routes building cleanly; 228 automated tests passing.

### Milestone v0.7: Agricultural Intelligence & Multi-Channel Messaging
- **Goal**: Machine learning price forecasting, agrometeorology, and conversational chat bots.
- **Phases**:
  - [x] **Phase 7**: ML Price Forecasting Engine (LightGBM, MAD outlier detection, feature store).
  - [x] **Phase 8**: Weather Integration (Open-Meteo 7-day agrometeorological forecasts).
  - [x] **Phase 9**: WhatsApp Cloud API Channel (Webhook, HMAC security, daily price digests, harvest submission).
  - [x] **Phase 10**: Telegram Bot Integration (`@Fpo_Link_Bot`, contact card verification, auto-registration).
- **Status**: **Completed**. Both bot channels active and tested.

### Milestone v0.8: Supply + Demand Network & Operational Tasks
- **Goal**: Land parcel yield prediction, buyer demand aggregation, and staff task board.
- **Phases**:
  - [x] **Phase 11**: Farm Plots & Yield Estimator (Multi-plot farmer parcels, agro-climatic norms).
  - [x] **Phase 12**: Buyer Registry & Demand Requirements (Staff-mediated institutional buyers).
  - [x] **Phase 13**: Semi-Automatic Matching Engine (Haversine distance ranking, suitability scoring).
  - [x] **Phase 14**: FPO Task Management Board (Task CRUD, assignment, status tracking, migration `0013_fpo_tasks`).
- **Status**: **Completed**. Seeded on Render production database.

---

## Active Milestone: v0.9 — Cloud Hosting & Field Pilot

- **Goal**: Complete live cloud staging deployment and execute 14-day field pilot in Erode district.
- **Phases**:
  - [x] **Phase 15**: Render Cloud Backend Deployment & PostgreSQL Provisioning (Live at `https://fpolink-api.onrender.com`).
  - [x] **Phase 16**: Remote Database Seeding & Production Admin Setup (Admin `8072845239` / `Admin@123` verified).
  - [x] **Phase 17**: Live Telegram Bot Webhook Integration (`@Fpo_Link_Bot` linked to Render).
  - [ ] **Phase 18**: Frontend Cloud Deployment (Link Next.js frontend to Vercel/Netlify pointing to Render API).
  - [ ] **Phase 19**: 14-Day Erode Field Pilot (Onboard 1 coordinator and 10 farmers per `docs/PILOT_RUNBOOK.md`).

---

## Future Milestone: v1.0 — Statewide Expansion & Voice Interface

- **Phase 20**: Tamil Voice-First Interface (AI speech-to-text / text-to-speech for non-literate farmers).
- **Phase 21**: Logistics & Transport Pooling (Truckload sharing for smallholder harvest transport).
- **Phase 22**: Digital Payment Escrow & Smart Contracts (Automated settlement upon buyer delivery inspection).
