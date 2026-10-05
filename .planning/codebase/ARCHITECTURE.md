# FPOLink System Architecture

High-level architecture, module decomposition, data pipelines, and design patterns.

---

## 1. Architectural Style & Design Patterns

FPOLink follows a **Clean Layered Architecture** with **Hexagonal / Ports-and-Adapters** design for multi-channel messaging and external data providers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                            │
│  Next.js Web App (16 Routes)  │  Telegram Webhook  │  WhatsApp Webhook │
└───────────────────────┬───────────────────┬───────────────────┬────────┘
                        │                   │                   │
                        ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        API & TRANSPORT ADAPTERS                        │
│  FastAPI Routers (/api/*)     │ TelegramChatChannel│ WhatsAppChannel   │
│  - JWT Bearer & RBAC Guards   │ - Contact Linking  │ - HMAC Verification│
└───────────────────────┬───────────────────┬───────────────────┬────────┘
                        │                   │                   │
                        ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          DOMAIN & SERVICE LAYER                        │
│  BotEngine (Transport Agnostic State Machine)                         │
│  IngestionService & Data Quality Engine (MAD Outliers, Replay)         │
│  AgriculturalIntelligenceService (LightGBM Forecaster, Haversine)     │
│  MatchingEngine (Buyer-Farm Ranking & Staff Mediation)                 │
│  YieldEstimator (Crop Benchmarks & Soil Multipliers)                   │
│  FPOService, FarmerService, TaskService                                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS & STORAGE LAYER                      │
│  SQLAlchemy 2.0 Models  │  SessionLocal (Unit of Work)                 │
│  PostgreSQL 16 (Render Cloud / Local Dev)                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystems & Data Pipelines

### A. Price Ingestion & Normalization Pipeline
1. **Trigger**: Scheduled daily worker (`worker.py`) or manual admin trigger (`POST /api/admin/ingest`).
2. **Fetch**: Adapters query upstream sources (`OGD Agmarknet`, `CEDA Ashoka`, `MandiPrices`).
3. **Audit**: Raw payload is archived in `raw_ingest` with SHA-256 checksum for replay and lineage auditing.
4. **Cleanse**: Normalization engine parses date formats, canonicalizes crop/market aliases (`CropAlias`, `MarketAlias`), and converts quantities into ₹/quintal and ₹/kg.
5. **Quality Gate**: MAD (Median Absolute Deviation) outlier detector flags suspicious price spikes or drops.
6. **Persist**: Valid prices inserted into `market_prices`; lineage recorded in `data_lineage`.

### B. Transport-Agnostic Bot Engine
1. **Inbound Handshake**: Webhook arrives at `/api/whatsapp/webhook` or `/api/telegram/webhook`.
2. **Channel Normalization**:
   - `WhatsApp`: Unpacks Cloud API JSON, checks HMAC-SHA256 signature.
   - `Telegram`: `TelegramBotService` extracts chat ID, resolves phone number from `User.telegram_chat_id` or prompts for contact card.
3. **State Machine Execution (`BotEngine`)**:
   - Manages state in `conversation_state` with 15-minute TTL.
   - Interprets natural language or button taps (supporting Tamil keywords e.g. `விலை`, `அறுவடை`, `நிறுத்து` alongside English).
   - Resolves intent: Price check, 7-day forecast, harvest logging, weather check, or buyer search.
4. **Outbound Dispatch**: Generic response payload is formatted by the respective channel adapter (e.g. Telegram Inline Keyboards or WhatsApp Interactive Buttons).

### C. Supply & Demand Matching Engine
1. **Farmer Plot Registration**: Farmer or FPO registers plot (`farms`), specifying crop, variety, acreage, and sowing date.
2. **Yield Estimation**: `YieldEstimator` computes predicted harvest volume based on TN regional benchmarks, irrigation types, and soil profiles.
3. **Demand Aggregation**: FPO staff records verified buyer procurement requirements (`requirements`).
4. **Matching Algorithm**:
   - Filters candidate farm plots by crop type, variety, and harvest window.
   - Computes Haversine distance between farm coordinates and buyer delivery point.
   - Computes weighted suitability score (Quality/Variety match + Distance proximity + Volume coverage).
   - Generates suggested `supply_matches` for FPO staff mediation.

---

## 3. Security & Multitenancy Architecture

- **Role-Based Access Control (RBAC)**: Defined via `UserRole` enum (`admin`, `fpo_staff`, `farmer`, `buyer`).
- **Dependency-Injected Guards**: `require_role(["admin", "fpo_staff"])` enforces endpoint authorization in FastAPI.
- **Tenant Scoping**: FPO staff actions are scoped to their respective `fpo_id`. Admins hold statewide visibility.
- **Password Policies**:
  - Minimum 8-12 character rules enforced on creation.
  - New staff/farmer seed accounts flag `password_change_required=true`, blocking privileged actions until updated.
- **Secrets Management**: Dynamic settings loaded through Pydantic `Settings` class with production validation rejecting default secrets when `ENVIRONMENT=production`.
