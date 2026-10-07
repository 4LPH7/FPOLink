# Phase M3: Defensible Arbitrage & Transport Realization — Context & Locked Decisions

> **Milestone:** M-Series MVP Sprint / Phase M3  
> **Topic:** Defensible Inter-District Market Arbitrage & Transport Net Realization  
> **Status:** Locked & Approved

---

## 1. Goal & Objectives

Transform the simple Haversine-and-flat-rate arbitrage engine into a defensible, real-world operational decision tool for FPO staff:
1. Replace rigid fixed formulas with configurable vehicle profiles and per-commodity transit risk defaults.
2. Provide transparent, itemized cost deductions: Freight, Handling/Bagging, Mandi Market Commission, and Spoilage buffer.
3. Compare like-for-like varieties and evaluate observation date freshness gaps.
4. Supply multi-factor uncertainty ratings (`low`, `moderate`, `high`) and explicit bilingual defensibility disclaimers.
5. Provide interactive configuration controls in the web dashboard with instant net spread recalculation.

---

## 2. Locked Architectural Decisions

### Decision 1: Vehicle & Freight Presets
- **Pickup / Tata Ace (1.5T payload)**:
  - Base fee: ₹35.0/qtl (scaled for 15 quintal load)
  - Rate: ₹2.00/km/quintal
- **LCV / 407 (3.5T payload, Default)**:
  - Base fee: ₹20.0/qtl (scaled for 35 quintal load)
  - Rate: ₹1.20/km/quintal
- **Medium Truck / 6-Wheeler (10T payload)**:
  - Base fee: ₹12.0/qtl (scaled for 100 quintal load)
  - Rate: ₹0.85/km/quintal
- **Custom Mode**: User supplies custom base loading cost and per-km rate.

### Decision 2: Per-Commodity Transit Spoilage Defaults
- **Perishable Horticulture** (Banana, Tomato, Vegetables): Default `3.0%` transit shrinkage/spoilage.
- **Semi-Perishable** (Coconut, Sugarcane): Default `1.0%` transit loss.
- **Durable / Spices / Grains** (Turmeric, Paddy, Groundnut, Pulses): Default `0.0%` transit loss.
- All defaults are user-overridable via API parameter `spoilage_risk_pct` and frontend slider.

### Decision 3: Line-Item Cost Structure
Total cost per quintal equals:
$$\text{Cost}_{\text{total}} = \text{Freight} + \text{Handling} + \text{Mandi Commission} + \text{Spoilage Risk}$$
- **Freight**: $\text{base\_cost} + (\text{distance\_km} \times \text{rate\_per\_km\_quintal})$
- **Handling**: Loading, bagging, and porterage fee (default ₹15.0/qtl)
- **Mandi Commission**: $\text{target\_modal\_price} \times (\text{commission\_pct} / 100)$ (default 1.5%)
- **Spoilage Risk**: $\text{origin\_price} \times (\text{spoilage\_risk\_pct} / 100)$

### Decision 4: Like-for-Like Quality & Date Freshness Alignment
- **Variety Matching**:
  - `exact`: Target market specifies the exact same variety as origin.
  - `cross_variety_approximate`: Target market lacks variety record or differs. Tagged with an uncertainty penalty.
- **Observation Date Gap**:
  - Track `date_difference_days = (origin_date - target_date)`.
  - If `date_difference_days > 2`, flag `observation_lag_risk` and calculate a 1.0%/day recency discount buffer.
  - If target price is $> 7$ days old, mark as stale and penalize net rating.

### Decision 5: Multi-Factor Uncertainty Rating
Composite rating:
- `low`: Distance $\le 150$ km, observation lag $\le 1$ day, exact variety match.
- `moderate`: Distance $150 - 250$ km, observation lag $2 - 3$ days, or cross-variety approximation.
- `high`: Distance $> 250$ km, observation lag $> 3$ days, or thin arrival volumes.

### Decision 6: Defensibility Disclaimers
Returned in every API response:
- `disclaimer_ta`: "இது மதிப்பிடப்பட்ட சாத்தியக்கூறு மட்டுமே; போக்குவரத்து கட்டணம், தரம் மற்றும் சந்தை கட்டணங்களின் அடிப்படையில் மாறுபடலாம்."
- `disclaimer_en`: "Estimated net opportunity based on reported mandi modal prices. Does not guarantee realized trading profit; actual outcomes depend on vehicle capacity, live arrival volumes, transporter quotes, and quality grading."

---

## 3. Scope Boundaries & Out of Scope
- **In Scope**:
  - Engine logic in `backend/app/services/arbitrage.py`
  - Extended API contracts in `backend/app/schemas/intelligence.py` and endpoint in `backend/app/api/v1/intelligence.py` (with `crop` and `market` name resolvers)
  - Interactive UI controls in `frontend/app/prices/page.tsx`
  - CLI harness in `backend/scripts/evaluate_arbitrage.py`
  - Verification test suite in `backend/tests/test_arbitrage_enhancements.py`
- **Out of Scope**:
  - Live third-party road GPS API integration (continue using Haversine geodesic distance with road tortuosity factor 1.15 where applicable).
  - Automated carrier dispatch or payments (deferred to v1.0 Logistics Pooling).
