# Phase M3: Defensible Arbitrage & Transport Realization — Implementation Plan

> **Phase:** M3  
> **Milestone:** M-Series MVP Sprint  
> **Prerequisites:** Phase M0 (Pre-flight), Phase M1 (Real Price Data), Phase M2 (Honest Forecasting) complete  
> **Context Document:** [M3-CONTEXT.md](file:///d:/PROJECTS/FPOLink/.planning/phases/M3-CONTEXT.md)

---

## 1. Phase Overview

This phase elevates inter-district price arbitrage from an ungrounded theoretical spread calculation to an operationally defensible decision workflow for Tamil Nadu FPO coordinators and dispatchers.

Every recommendation will:
1. State its input costs transparently (vehicle freight, handling, commission, spoilage).
2. Compare like-for-like varieties and account for price observation date lags.
3. Quantify uncertainty with a multi-factor risk score.
4. Carry bilingual legal/advisory disclaimers clarifying that spreads are *estimated net opportunities, not guaranteed profits*.

---

## 2. Tasks & Execution Sequence (Tracer-First)

### Task M3.1: Upgrade Arbitrage Engine & Cost Realization Math (Tracer Slice)
- **Target File:** `backend/app/services/arbitrage.py`
- **Work Items:**
  1. Define vehicle profile definitions:
     - `pickup` (1.5T payload): Base ₹35/qtl, ₹2.00/km/qtl.
     - `lcv` (3.5T payload, Default): Base ₹20/qtl, ₹1.20/km/qtl.
     - `medium_truck` (10T payload): Base ₹12/qtl, ₹0.85/km/qtl.
     - `custom`: user-specified parameters.
  2. Implement commodity-specific perishability default resolver:
     - Perishable (Banana, vegetables) -> 3.0%
     - Semi-perishable (Coconut) -> 1.0%
     - Durable (Turmeric, grains, pulses) -> 0.0%
  3. Compute itemized line-item costs:
     - Freight, Handling (default ₹15/qtl), Mandi Commission (default 1.5%), Transit Spoilage buffer.
  4. Perform variety matching:
     - Detect if origin and destination share the same variety (`exact` vs `cross_variety_approximate`).
  5. Calculate observation date disparity (`date_difference_days`) and apply recency uncertainty flags.
  6. Compute multi-factor `uncertainty_rating` (`low`, `moderate`, `high`) and reason tags.
  7. Provide bilingual disclaimers in Tamil and English.
- **Verification:** Fast sanity test on `find_market_arbitrage` with synthetic and seeded DB records.

---

### Task M3.2: Extend API Schemas & REST Endpoint
- **Target Files:**
  - `backend/app/schemas/intelligence.py`
  - `backend/app/api/v1/intelligence.py`
- **Work Items:**
  1. In `ArbitrageOpportunity` schema:
     - Add `variety_match: str` (`exact` | `cross_variety_approximate`).
     - Add `uncertainty_rating: str` (`low` | `moderate` | `high`).
     - Add `uncertainty_reasons: List[str]`.
     - Update `costs_breakdown` schema to guarantee `freight`, `handling`, `commission`, `spoilage_risk`, `total_cost`.
  2. In `ArbitrageResponse` schema:
     - Add `vehicle_profile: str`.
     - Add `disclaimer_ta: str` and `disclaimer_en: str`.
  3. In `get_arbitrage_opportunities` endpoint:
     - Support resolving `crop` and `market` / `origin_market` names automatically when UUIDs are omitted.
     - Add `vehicle_profile: str = Query("lcv")` parameter.
- **Verification:** Endpoint returns HTTP 200 with all new fields present.

---

### Task M3.3: Interactive UI Controls & Cost Visualizer
- **Target Files:**
  - `frontend/lib/api.ts`
  - `frontend/app/prices/page.tsx`
- **Work Items:**
  1. Update `ArbitrageOpportunity` and `ArbitrageResponse` TypeScript interfaces in `frontend/lib/api.ts`.
  2. In `frontend/app/prices/page.tsx` under the Arbitrage tab:
     - Add vehicle profile switcher: Pickup (1.5T), LCV (3.5T), Medium Truck (10T).
     - Add collapsible "Cost Assumptions" settings panel (Handling ₹/qtl, Mandi Commission %, Spoilage buffer %).
     - Add uncertainty badges (`Low`, `Moderate`, `High`) with contextual tooltips.
     - Show detailed cost breakdown (Freight, Handling, Mandi Fee, Spoilage) in table cells.
     - Render the prominent bilingual defensibility warning banner.
- **Verification:** `npm run build` exits 0 with zero type errors.

---

### Task M3.4: Evaluation CLI Tool & Documentation Specification
- **Target Files:**
  - `backend/scripts/evaluate_arbitrage.py` (New CLI)
  - `docs/ARBITRAGE_SPEC.md` (New Documentation)
- **Work Items:**
  1. Create `evaluate_arbitrage.py` to evaluate arbitrage for any crop/origin mandi from CLI, rendering clear terminal tables and cost breakdowns.
  2. Generate `docs/ARBITRAGE_SPEC.md` documenting the cost equations, vehicle capacities, uncertainty scoring rubrics, and defensibility rationale.
- **Verification:** CLI runs with exit code 0.

---

### Task M3.5: Automated Test Suite & Regression Verification
- **Target File:** `backend/tests/test_arbitrage_enhancements.py`
- **Work Items:**
  1. Test vehicle presets and cost math.
  2. Test commodity-specific spoilage defaults (Banana 3% vs Turmeric 0%).
  3. Test like-for-like variety matching and observation date difference penalties.
  4. Test endpoint querying by crop and market names.
  5. Test presence of bilingual disclaimers and uncertainty ratings.
  6. Run full test suite (260+ tests) to guarantee zero regressions.
- **Verification:** `pytest` exits 0.

---

### Task M3.6: Quality Checks & Git Commit
- **Work Items:**
  1. Run `ruff check .` and `ruff format --check .`.
  2. Run `graphify update .`.
  3. Commit with atomic message `feat(m3): implement defensible arbitrage engine with configurable vehicle profiles, itemized costs, and uncertainty ratings`.
