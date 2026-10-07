# Phase M5 Context: Statewide Multi-Crop & District-Dynamic Frontend Experience with JetBrainsMono & Modern Web Optimization

## 1. Executive Intent & Goals

FPOLink TN was initially prototyped focusing on pilot crops (turmeric, banana, coconut) in Erode district. Now that backend data sources, statewide geography (38 revenue districts), and commodity ontologies (20 Tier-A crops) are fully implemented in PostgreSQL, the web application must be upgraded to:
1. **Remove hardcoded crop assumptions**: Decouple the frontend from fixed turmeric/banana/coconut defaults, supporting dynamic selection and analysis of all 20 Tier-A crops (Paddy, Groundnut, Tomato, Small Onion, Maize, Cotton, Sugarcane, Tapioca, Mango, Pulses, Spices, Vegetables).
2. **Make the entire platform district-wise choosable**: Enable selecting any of Tamil Nadu's 38 revenue districts across the Action Workspace, Price Analytics, Farmer directory, and Commercial Buyers.
3. **Typography Upgrade to JetBrainsMono**: Integrate `JetBrains_Mono` via Next.js 14 font optimization (`next/font/google`), pairing with `'Noto Sans Tamil'` for seamless Tamil script rendering, and applying `font-size-adjust: from-font;` per the `modern-web-guidance` visually stable font fallbacks standard.
4. **Performance & Modern Web Optimization**: Implement Core Web Vitals optimizations (zero Cumulative Layout Shift font metrics, CSS `content-visibility: auto` on data-dense price grids, memoized search and filtering, and lazy chart bundling).

---

## 2. Technical Decisions & Architectural Matrix

### Typography: JetBrains Mono + Noto Sans Tamil
- Use `next/font/google` for `JetBrains_Mono` (`subsets: ["latin"]`, `display: "swap"`, `variable: "--font-jetbrains-mono"`).
- Update `tailwind.config.ts` so `fontFamily.sans` and `fontFamily.mono` both prioritize `var(--font-jetbrains-mono)`.
- Fall back gracefully to `'Noto Sans Tamil'` so Tamil headers, labels, and descriptions render with full glyph integrity and balanced x-heights.
- Apply `font-size-adjust: from-font;` in `globals.css` to eliminate layout shift during font swaps.

### Multi-Crop Dynamic Engine
- Replace static crop buttons in `PriceChart.tsx` with dynamic crop selectors populated from `getCrops()` or loaded prices.
- In `frontend/app/prices/page.tsx`:
  - Dynamically default `activeChartCrop` to the first available reporting crop rather than hardcoding `"turmeric"`.
  - Render top commodity KPI cards dynamically based on reporting volume/updates rather than querying specifically for turmeric or banana.
  - Dynamically read unit from `record.unit` or `crop.unit` (₹/kg or ₹/quintal) rather than checking if `crop_name.includes("banana")`.
- In `frontend/components/AggregationSummary.tsx`:
  - Expand crop emoji mapping to cover all statewide crops (Paddy 🌾, Tomato 🍅, Onion 🧅, Maize 🌽, Cotton ☁️, Sugarcane 🎋, Mango 🥭, Chilli 🌶️, Brinjal 🍆, Groundnut 🥜, Tapioca 🥔, Coconut 🥥, Banana 🍌, Turmeric 🌾, Ginger 🫚, etc.) with generic fallback 🌱.
- In `frontend/app/farmers/page.tsx`:
  - Expand plot yield estimator (`basePerAcreKg`) with realistic agro-climatic baseline norms across all 20 Tamil Nadu commodities.

### Statewide District Selection
- Provide district-level filtering (All 38 Districts + Statewide) on:
  - Header / Navigation or Workspace.
  - `/` (FPO Action Workspace).
  - `/prices` (Market Prices & Arbitrage).
  - `/farmers` (Farmer Management).
  - `/buyers` (Buyer Requirements).
