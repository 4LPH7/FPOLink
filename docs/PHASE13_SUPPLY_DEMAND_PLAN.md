# FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)

## Executive Summary
This document specifies the architecture, data models, matching algorithms, APIs, and zero-cost WhatsApp messaging flows for **Phase 13 (v0.8 Supply + Demand Network)** of FPOLink TN.

Building on top of the Statewide Data Network (v0.6) and Agricultural Intelligence (v0.7), v0.8 connects ground-level agricultural supply (farm plots, planting schedules, expected harvest yields) with commercial demand (staff-entered institutional buyer requirements), mediated by a semi-automatic matching engine and zero-cost WhatsApp interaction.

---

## 1. Locked Strategic Decisions

| Decision Area | Chosen Strategy | Architectural Rationale |
|---|---|---|
| **Scope & Phasing** | Wave 1 sequentially first (Data model & CRUD) | Models must stabilize before building matching algorithms or yield forecasting to avoid schema churn. |
| **Farm Entity** | Separate `Farm/Plot` entity with multiple plots per farmer | Accommodates non-contiguous plots, varied crops, soil types, and irrigation methods with per-plot yield estimation. |
| **Buyer Model** | Staff-entered for v0.8; `BUYER` RBAC role reserved | Avoids buyer onboarding/trust overhead; mirrors staff-mediated farmer bot model; seamless future transition to self-service. |
| **Matching Engine** | Semi-automatic: system scores & ranks, staff confirms | Protects farmers from false matches while capturing ground-truth labeled match data for future tuning. |
| **Yield Forecasting** | Deterministic rule-based estimates (District/Crop agro-climatic norms) | Prevents ungrounded ML on sparse outcome data; logs actual vs predicted yields to build clean training datasets for v0.9+. |
| **WhatsApp Strategy** | Inbound-first (pull-based) free window + low-cost confirmed utility alerts | Exploits free 24-hr service conversation window when farmers check in; paid utility templates used exclusively for staff-confirmed matches. |
| **Data Seeding** | Synthetic Erode pilot dataset + CSV import harness | Provides immediate operational data for testing while supporting bulk field data ingestion. |

---

## 2. Data Model Evolution (Alembic Migration 0011)

### 2.1 Farm / Plot Entity (`backend/app/models/farm.py`)
Enhances the existing `Farm` table to represent discrete agricultural plots:
- `id`: UUID (Primary Key)
- `farmer_id`: UUID (Foreign Key `farmers.id`, non-nullable)
- `crop_id`: UUID (Foreign Key `crops.id`, non-nullable)
- `plot_name`: String(100), optional (e.g. "East Canal Field", "Vadakkukadu Plot A")
- `area_acres`: Float, non-nullable ($> 0.0$)
- `village`: String(100), non-nullable
- `soil_type`: String(50), optional (e.g. "Red Loam", "Black Cotton", "Alluvial", "Clay Loam")
- `irrigation_type`: String(50), optional (e.g. "Drip", "Canal", "Borewell", "Rainfed")
- `sowing_date`: Date, optional
- `expected_harvest_date`: Date, optional
- `expected_yield_kg`: Float, optional (auto-computed by rule-based estimator)
- `actual_yield_kg`: Float, optional (recorded upon harvest completion for ML training)
- `status`: String(20), default "active" ("active", "harvested", "fallow", "abandoned")
- `state_id`, `district_id`, `taluk_id`, `village_id`: UUID Foreign Keys to Geography hierarchy

### 2.2 Buyer Entity (`backend/app/models/buyer.py`)
Decouples buyers from mandatory user logins:
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key `users.id`, **nullable** to support staff-entered buyers)
- `fpo_id`: UUID (Foreign Key `fpos.id`, nullable for statewide buyers)
- `company_name`: String(200), non-nullable
- `buyer_type`: String(50), default "wholesaler" ("wholesaler", "exporter", "processor", "retailer", "trader")
- `contact_name`: String(100), optional
- `contact_phone`: String(15), non-nullable
- `contact_email`: String, optional
- `location`: String(200), non-nullable
- `district`: String(100), optional
- `district_id`: UUID (Foreign Key `districts.id`, optional)
- `gstin`: String(20), optional
- `verified`: Boolean, default False
- `created_by_user_id`: UUID (Foreign Key `users.id`, staff member who entered the buyer)

### 2.3 Buyer Requirement Entity (`backend/app/models/buyer.py`)
Specifies procurement demand:
- `id`: UUID (Primary Key)
- `buyer_id`: UUID (Foreign Key `buyers.id`, non-nullable)
- `fpo_id`: UUID (Foreign Key `fpos.id`, optional FPO scoping)
- `crop_id`: UUID (Foreign Key `crops.id`, non-nullable)
- `variety_id`: UUID (Foreign Key `varieties.id`, optional specific cultivar)
- `quantity_kg`: Float, non-nullable ($> 0.0$)
- `fulfilled_quantity_kg`: Float, default 0.0
- `min_grade`: Enum `HarvestGrade` (`A`, `B`, `C`)
- `required_date`: Date, non-nullable
- `delivery_window_days`: Integer, default 7
- `max_price_per_kg`: Numeric(12, 2), optional
- `delivery_location`: String(200), optional
- `status`: String(20), default "open" ("open", "matched", "partially_fulfilled", "fulfilled", "cancelled")
- `notes`: Text, optional
- `created_by_user_id`: UUID (Foreign Key `users.id`)

### 2.4 Supply Match Entity (`backend/app/models/supply_match.py` - NEW)
Audited matching records between buyer demand and farmer supply:
- `id`: UUID (Primary Key)
- `buyer_requirement_id`: UUID (Foreign Key `buyer_requirements.id`, non-nullable)
- `farm_id`: UUID (Foreign Key `farms.id`, nullable for standing crop matches)
- `harvest_id`: UUID (Foreign Key `harvests.id`, nullable for harvested batch matches)
- `fpo_id`: UUID (Foreign Key `fpos.id`, non-nullable)
- `matched_quantity_kg`: Float, non-nullable
- `offered_price_per_kg`: Numeric(12, 2), optional
- `match_score`: Float, non-nullable (0.0 to 100.0)
- `match_breakdown`: JSONB (detailed score components: `distance_km`, `quantity_fit`, `timing_days`, `grade_fit`)
- `status`: String(30), default "suggested" ("suggested", "confirmed_by_staff", "notified_farmer", "farmer_accepted", "farmer_declined", "fulfilled", "cancelled")
- `staff_notes`: Text, optional
- `confirmed_by_id`: UUID (Foreign Key `users.id`, nullable)
- `confirmed_at`: DateTime(timezone=True), nullable
- `notified_at`: DateTime(timezone=True), nullable
- `farmer_responded_at`: DateTime(timezone=True), nullable

---

## 3. Business Logic & Core Algorithms

### 3.1 Rule-Based Yield Estimator (`backend/app/services/yield_estimator.py`)
Computes expected crop yield per plot using empirical regional benchmarks:
1. **Base Agro-Climatic Yield ($Y_{\text{base}}$)**: Derived from Tamil Nadu Agricultural University (TNAU) and government district gazettes for the crop in quintals/acre (e.g., Turmeric: $25\text{ qtl/acre}$ cured or $100\text{ qtl/acre}$ fresh; Robusta Banana: $180\text{ qtl/acre}$; Coconut: $8,000\text{ nuts/acre}$; Tomato: $120\text{ qtl/acre}$).
2. **Irrigation Factor ($M_{\text{irrig}}$)**:
   - Drip Irrigation: $+15\%$ ($1.15$)
   - Canal / Borewell: Baseline ($1.00$)
   - Rainfed / Dryland: $-30\%$ ($0.70$)
3. **Soil Factor ($M_{\text{soil}}$)**:
   - Optimal soil (e.g., Red Loam for Turmeric/Banana): $+10\%$ ($1.10$)
   - Sub-optimal or Heavy Clay: $-15\%$ ($0.85$)
   - Normal / Mixed: Baseline ($1.00$)
4. **Calculated Expected Yield**:
   $$\text{Yield (kg)} = \text{Area (acres)} \times Y_{\text{base}} \times M_{\text{irrig}} \times M_{\text{soil}} \times 100$$
5. **Expected Harvest Window**: Sowing Date $+$ Crop Gestation Period (e.g., Turmeric 270 days, Banana 330 days).

### 3.2 Semi-Automatic Matching Engine (`backend/app/services/matching_service.py`)
Evaluates available supply candidates (standing plots and verified harvests) against an open `BuyerRequirement`:

$$\text{Match Score} = W_{\text{crop}} \times S_{\text{crop}} + W_{\text{prox}} \times S_{\text{prox}} + W_{\text{qty}} \times S_{\text{qty}} + W_{\text{time}} \times S_{\text{time}} + W_{\text{grade}} \times S_{\text{grade}}$$

1. **Crop Match ($S_{\text{crop}}$)**: Binary hard gate ($100\%$ or $0\%$). Must match canonical `crop_id`.
2. **Proximity Score ($S_{\text{prox}}$)**: Based on Haversine distance $D$ in km between delivery location/district and farm village:
   $$S_{\text{prox}} = \max\left(0, 100 - \frac{D}{300} \times 100\right)$$
3. **Quantity Fit ($S_{\text{qty}}$)**:
   $$S_{\text{qty}} = \frac{\min(\text{Supply Qty}, \text{Requirement Qty})}{\max(\text{Supply Qty}, \text{Requirement Qty})} \times 100$$
4. **Timing Fit ($S_{\text{time}}$)**: Delta $\Delta t = |\text{Harvest Date} - \text{Required Date}|$ in days:
   $$S_{\text{time}} = \max\left(0, 100 - \Delta t \times 5\right) \quad (\text{0 if } \Delta t > 20 \text{ days})$$
5. **Grade Fit ($S_{\text{grade}}$)**: $100\%$ if Grade matches or exceeds minimum required; penalized if lower.

Staff reviews ranked candidates on the dashboard and triggers a one-click confirmation (`confirmed_by_staff`).

---

## 4. WhatsApp Zero-Cost Interaction Architecture

### 4.1 Free Service Conversation Window (Inbound-First)
- When a farmer messages the WhatsApp bot (e.g., typing "HI", "UPDATE", "BUYERS", "கொள்முதல்", or selecting the interactive menu):
  1. A **24-hour free service conversation window** opens with Meta.
  2. The bot fetches active, staff-confirmed buyer matches for the farmer's registered crops.
  3. The bot replies with an interactive message listing buyer opportunities (crop, quantity, indicative price, delivery window).
  4. **Cost**: ₹0.00 (within Meta's 1,000 monthly free service conversations).

### 4.2 Gated Low-Cost Outbound Nudge (Only When Staff Confirms)
- When FPO staff confirms a high-value match on the web dashboard:
  - If the farmer has `alerts_opt_in = True` and is within monthly rate limits:
  - System sends a single, low-cost **Utility Template** message (₹0.115):
    > *"வணக்கம் {farmer_name}, உங்கள் {crop_name} அறுவடைக்கு புதிய கொள்முதல் வாய்ப்பு உள்ளது. விவரங்களை அறிய '1' அல்லது 'BUY' என பதிலளிக்கவும்."*
  - When the farmer replies, it opens the free 24-hr service window for negotiation and harvest scheduling.

---

## 5. REST API v1 Specification

### 5.1 Farm Plot Endpoints (`/api/v1/farms`)
- `POST /api/v1/farms/`: Register a new farm plot under a farmer.
- `GET /api/v1/farms/`: List farm plots with filters (`farmer_id`, `fpo_id`, `crop_id`, `district`).
- `GET /api/v1/farms/{farm_id}`: Retrieve plot details and calculated yield breakdown.
- `PUT /api/v1/farms/{farm_id}`: Update plot status, actual yield, or cultivation details.
- `POST /api/v1/farms/import-csv`: Bulk import plots from CSV template with validation.

### 5.2 Buyer & Requirement Endpoints (`/api/v1/buyers`)
- `POST /api/v1/buyers/`: Register a commercial buyer (staff-mediated).
- `GET /api/v1/buyers/`: List registered buyers with FPO/district scoping.
- `POST /api/v1/buyers/requirements`: Post a new buyer procurement requirement.
- `GET /api/v1/buyers/requirements`: List open requirements with crop and status filters.
- `GET /api/v1/buyers/requirements/{id}`: Detailed requirement view with active matches.

### 5.3 Semi-Automatic Matching Endpoints (`/api/v1/matching`)
- `GET /api/v1/matching/candidates/{requirement_id}`: Generate ranked candidate supply plots and harvests.
- `POST /api/v1/matching/confirm/{match_id}`: Staff confirmation of a candidate match.
- `POST /api/v1/matching/reject/{match_id}`: Staff rejection/dismissal of a match.
- `POST /api/v1/matching/notify/{match_id}`: Trigger WhatsApp utility notification to confirmed farmer.
- `GET /api/v1/matching/summary`: Aggregate supply and demand balance across commodities and districts.

---

## 6. Implementation Waves

```text
                               PHASE 13 ROADMAP
                                      │
  ┌───────────────────────────────────┴───────────────────────────────────┐
  │                                                                       │
  ▼                                                                       ▼
Wave 1: Data Model & Schema                                 Wave 2: Engines & Services
├── Farm/Plot Model (app/models/farm.py)                    ├── Rule-Based Yield Estimator
├── Buyer & Requirement (app/models/buyer.py)               ├── Farm & Buyer CRUD Services
├── SupplyMatch (app/models/supply_match.py)                ├── CSV Import Pipeline
└── Migration 0011_supply_demand_network                    └── Multi-Factor Matching Engine
  │                                                                       │
  └───────────────────────────────────┬───────────────────────────────────┘
                                      │
  ┌───────────────────────────────────┴───────────────────────────────────┐
  │                                                                       │
  ▼                                                                       ▼
Wave 3: API & WhatsApp Integration                          Wave 4: Frontend UI & Sign-Off
├── REST API v1 Routing                                     ├── Buyer Registry & Requirements
├── Inbound-First WhatsApp Match Query                      ├── Plot Management Modal
├── Confirmed Match Utility Nudge                           ├── Semi-Automatic Match Console
└── Synthetic Erode Pilot Seed Data                         └── Checkpoint H (100% Green Tests)
```
