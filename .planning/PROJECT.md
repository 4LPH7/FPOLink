# FPOLink TN — Project Specification

An open-source, agricultural intelligence, market price tracking, and supply-demand aggregation platform for Farmer Producer Organizations (FPOs) across Tamil Nadu.

---

## 1. Executive Vision

FPOLink bridges the digital divide for smallholder farmers and agricultural cooperatives in Tamil Nadu by combining:
1. **Tamil-First Multi-Channel Messaging**: Interactive WhatsApp Cloud API and Telegram Bot (`@Fpo_Link_Bot`) allowing farmers to check wholesale mandi prices, get 7-day weather forecasts, report harvests, and view buyer demand without needing to install dedicated smartphone apps.
2. **Statewide Mandi Intelligence**: Multi-source automated price ingestion from OGD India (Agmarknet), CEDA Ashoka University, and MandiPrices covering all 38 revenue districts of Tamil Nadu, combined with LightGBM price trend forecasting and MAD anomaly detection.
3. **Supply & Demand Aggregation Network**: Land parcel yield estimation, harvest aggregation batches, verified institutional buyer requirement catalogs, and AI-assisted distance/variety matching to empower FPO collective bargaining.
4. **Cooperative Management Dashboard**: Responsive Next.js 14 executive dashboard for FPO administrators to monitor member farmers, track crops, coordinate logistics, manage operational tasks, and mediate buyer deals.

---

## 2. Core Entities & Stakeholders

| Role | Interface | Primary Activities |
|---|---|---|
| **Member Farmer** | WhatsApp (`+91...`) / Telegram (`@Fpo_Link_Bot`) | Check mandi modal prices, report harvest quantities, view weather, receive price movement alerts |
| **FPO Staff / Coordinator** | Web Dashboard (`/dashboard`, `/tasks`) | Onboard farmers, verify submitted harvest tickets, allocate tasks, manage plots |
| **FPO Admin / Director** | Web Dashboard (`/settings`, `/matching`) | System administration, statewide price exploration, buyer negotiation & match confirmation |
| **Institutional Buyer** | Staff-Mediated / Registry (`/buyers`) | Specify procurement demand (volume, grade, target price, delivery window) |

---

## 3. Technology Architecture Summary

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic (`0013_fpo_tasks`), Pydantic v2, PyJWT.
- **Frontend**: Next.js 14 App Router, React 18, TypeScript, Tailwind CSS, Lucide icons, Recharts.
- **Data & Intelligence**: PostgreSQL 16 (Render Cloud & Local), LightGBM price forecaster, Open-Meteo weather integration.
- **Bots & Gateways**: Meta WhatsApp Cloud API (v19.0+), Telegram Bot API (`@Fpo_Link_Bot`).
- **Deployment**: Live backend hosted on Render (`https://fpolink-api.onrender.com`), database on Render Managed PostgreSQL.

---

## 4. Key Constraints & Guiding Principles

- **Tamil-First**: Default language preference is Tamil (`ta`) with English fallback; native terminology prioritized.
- **Zero-Barrier for Farmers**: All farmer-facing interactions operate via lightweight chat apps with minimal data usage.
- **DPDP Act (2023) Compliance**: Explicit farmer consent required; phone numbers masked; strict log retention limits (7-day inbound purge).
- **Cost Efficiency**: Inbound-first zero-cost 24-hr messaging window; free public feeds (Agmarknet, Open-Meteo).
- **Graceful Degradation**: Offline-tolerant local cache, circuit breakers on upstream 504 errors, fallback heuristic forecasting when time-series data is sparse.
