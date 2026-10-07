# FPOLink TN — Inter-District Arbitrage & Transport Realization Specification

> **Document Version:** 1.0  
> **Status:** Active Standard (Phase M3)  
> **Target Audience:** FPO Business Coordinators, Dispatch Managers, Agricultural Economists

---

## 1. Executive Rationale & Defensibility Philosophy

In raw agricultural trade, a nominal price differential across two mandis (e.g., Erode vs. Coimbatore) does not equal realizable profit. In traditional systems, naive recommendations mislead farmers and FPO managers by omitting:
1. Real-world vehicle freight curves (loading overheads and ton-kilometer rates).
2. Physical porterage, bagging, and mandi market committee commissions.
3. Transit spoilage and shrinkage risks, especially for high-moisture horticulture.
4. Grade/variety mismatches (comparing FAQ grade with premium bold grade).
5. Price observation time lags (e.g. comparing today's auction with a 3-day-old settlement).

Under **Phase M3**, FPOLink enforces strict **economic defensibility**: every arbitrage opportunity is modeled as an **Estimated Net Opportunity**, with explicit itemized deductions, like-for-like quality matching, and uncertainty risk ratings.

---

## 2. Mathematical Cost Model

For an origin mandi $M_{\text{origin}}$ and destination mandi $M_{\text{target}}$ separated by geodesic Haversine distance $D_{\text{km}}$:

$$\text{Gross Spread} = P_{\text{target}} - P_{\text{origin}}$$

$$\text{Total Deductions} = C_{\text{freight}} + C_{\text{handling}} + C_{\text{commission}} + C_{\text{spoilage}}$$

$$\text{Net Advantage} = \text{Gross Spread} - \text{Total Deductions}$$

### Line-Item Definitions

1. **Freight Cost ($C_{\text{freight}}$)**:
   $$C_{\text{freight}} = \text{BaseFee}_{\text{per\_qtl}} + (D_{\text{km}} \times \text{Rate}_{\text{per\_km\_qtl}})$$
   Calculated according to the active Vehicle Profile.

2. **Handling Fee ($C_{\text{handling}}$)**:
   Fixed handling, weighment, and bagging porterage per quintal (default ₹15.0/qtl).

3. **Mandi Market Fee & Commission ($C_{\text{commission}}$)**:
   $$C_{\text{commission}} = P_{\text{target}} \times \left(\frac{\text{commission\_pct}}{100}\right)$$
   Reflects regulated market committee cess and buyer agent commission (default 1.5%).

4. **Transit Spoilage Buffer ($C_{\text{spoilage}}$)**:
   $$C_{\text{spoilage}} = P_{\text{origin}} \times \left(\frac{\text{spoilage\_pct}}{100}\right)$$
   Compensates for en-route shrinkage, bruising, and grade deterioration.

---

## 3. Vehicle Profile Configurations

| Profile ID | Vehicle Description | Payload Capacity | Base Overhead (₹/qtl) | Mileage Rate (₹/km/qtl) | Economic Min (qtl) |
|---|---|---|---|---|---|
| `pickup` | Mini Truck / Tata Ace | 15 Quintals (1.5T) | ₹35.00 | ₹2.00 | 5 Quintals |
| `lcv` *(Default)* | LCV / Tata 407 | 35 Quintals (3.5T) | ₹50.00 | ₹1.20 | 10 Quintals |
| `medium_truck` | 6-Wheeler Freight Truck | 100 Quintals (10.0T) | ₹25.00 | ₹0.85 | 30 Quintals |
| `custom` | User Configured | Custom | User defined | User defined | User defined |

---

## 4. Commodity Perishability & Spoilage Matrix

Defaults applied automatically based on commodity ontology:

* **Perishable Horticulture (3.0% transit buffer)**:
  * Banana (*Musa acuminata*)
  * Tomato (*Solanum lycopersicum*)
  * Leafy vegetables and soft fruits
* **Semi-Perishable (1.0% transit buffer)**:
  * Tender & Dry Coconut (*Cocos nucifera*)
  * Sugarcane
* **Durable / Cured (0.0% transit buffer)**:
  * Turmeric (*Curcuma longa*)
  * Paddy / Rice (*Oryza sativa*)
  * Groundnut, Maize, Millets, and Pulses

---

## 5. Multi-Factor Uncertainty Rubric

Opportunities are evaluated across 4 risk vectors to compute an aggregate uncertainty rating:

| Risk Vector | Condition | Point Weight |
|---|---|---|
| **Distance** | $D_{\text{km}} > 250$ km | +30 |
| | $150 \le D_{\text{km}} \le 250$ km | +15 |
| **Observation Lag** | Destination price $\ge 5$ days older than origin | +35 |
| | Destination price $3 - 4$ days older than origin | +20 |
| **Variety Match** | `cross_variety_approximate` (differing or unrecorded varieties) | +25 |
| **Transit Spoilage** | Perishable commodity transit risk active | +10 |
| **Mandi Liquidity** | Reported arrival volume $< 5.0$ tonnes | +15 |

### Discrete Classification
* **Low Risk (< 30 pts)**: Close proximity, current observation, exact variety match.
* **Moderate Risk (30 - 59 pts)**: Standard corridor, mild date lag or approximate variety.
* **High Risk ($\ge 60$ pts)**: Long haul (> 250 km) or significant price staleness.

---

## 6. Bilingual Advisory Disclaimers

All API responses and frontend dashboards display:

* **Tamil (`ta`)**:
  > *"இது மதிப்பிடப்பட்ட சாத்தியக்கூறு மட்டுமே; போக்குவரத்து கட்டணம், தரம் மற்றும் சந்தை கட்டணங்களின் அடிப்படையில் மாறுபடலாம்."*
* **English (`en`)**:
  > *"Estimated net opportunities based on reported mandi modal prices. Does not guarantee realized trading profit; actual outcomes depend on vehicle capacity, live arrival volumes, transporter quotes, and quality grading."*
