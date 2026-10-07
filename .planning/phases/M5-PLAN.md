# Phase M5 Execution Plan: Statewide Multi-Crop & District-Dynamic Experience with JetBrainsMono & Performance Optimization

## Overview
Phase M5 transforms FPOLink from a pilot-restricted view (turmeric/banana/coconut in Erode) into an extensible statewide platform covering all 38 revenue districts and 20 Tier-A crops, with JetBrains Mono typography and modern web performance optimizations.

---

## Tasks

### Task M5.1: Typography Foundation with JetBrains Mono
- [ ] Import `JetBrains_Mono` in `frontend/app/layout.tsx` using `next/font/google`.
- [ ] Update `frontend/tailwind.config.ts` font families:
  - `sans`: `["var(--font-jetbrains-mono)", "'Noto Sans Tamil'", "monospace", "sans-serif"]`
  - `mono`: `["var(--font-jetbrains-mono)", "monospace"]`
  - `tamil`: `["'Noto Sans Tamil'", "sans-serif"]`
- [ ] Update `frontend/app/globals.css`:
  - Add `font-size-adjust: from-font;` to `body` per `modern-web-guidance` visually stable font fallbacks.
  - Set default font to `var(--font-jetbrains-mono)`.

### Task M5.2: Statewide Dynamic District Filtering
- [ ] Provide unified district state management or selectors across key pages.
- [ ] Enhance Header (`frontend/components/shell/Header.tsx`) or page headers with accessible, fast district selector.
- [ ] Ensure `/` (FPO Action Workspace), `/prices`, `/farmers`, and `/buyers` respect district selection.

### Task M5.3: Remove Locked-In Crops & Implement Statewide Multi-Crop Architecture
- [ ] Upgrade `frontend/components/PriceChart.tsx` to accept dynamic crop list or load from API, with a clean selector covering all available crops.
- [ ] Upgrade `frontend/components/AggregationSummary.tsx` with statewide crop emoji mapping covering all 20 Tier-A crops.
- [ ] Upgrade `frontend/app/prices/page.tsx`:
  - Remove hardcoded `"turmeric"` initial active crop; dynamically initialize to first available crop.
  - Remove hardcoded `"turmeric"` / `"banana"` lookups for top KPI cards; dynamically derive top reporting commodities.
  - Dynamically format units based on actual price record units.
- [ ] Upgrade `frontend/app/farmers/page.tsx`:
  - Expand yield calculations across all 20 crops (paddy, maize, cotton, sugarcane, tomato, onion, tapioca, groundnut, chillies, etc.).
  - Populate farmer registration district dropdown dynamically from `getDistricts()`.
- [ ] Upgrade `frontend/app/page.tsx`:
  - Allow district-level filtering of available produce and price telemetry.
  - Clean dynamic matching explanations for all commodities.

### Task M5.4: Modern Web Performance Optimizations
- [ ] Implement `content-visibility: auto; contain-intrinsic-size: 0 48px;` for price tables and card lists.
- [ ] Memoize expensive filters and list transforms in `PricesPage` and `FPOActionWorkspace`.
- [ ] Verify zero layout shift and clean fast rendering.

### Task M5.5: Full Verification & Graph Sync
- [ ] Verify `npm run build` passes with zero errors.
- [ ] Verify `pytest backend/tests` passes all 269 tests.
- [ ] Run `graphify update .`.
- [ ] Update documentation and commit.
