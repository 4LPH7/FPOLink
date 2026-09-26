/**
 * FPOLink TN — Frontend API Client
 *
 * Provides typed, direct access to the FastAPI backend with 100% real database records
 * and live external telemetry (Agmarknet, OGD, Open-Meteo).
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Crop {
  id: string;
  name: string;
  tamil_name?: string;
  category?: string;
  unit: string;
}

export interface CommoditySummary {
  id: string;
  name: string;
  canonical_name?: string;
  tamil_name?: string;
  scientific_name?: string;
  category?: string;
  unit: string;
  is_active: boolean;
  variety_count: number;
  alias_count: number;
  source_mapping_count: number;
  reporting_market_count: number;
}

export interface CommodityDetail extends CommoditySummary {
  subcategory?: string;
  default_unit?: string;
  market_unit?: string;
  season_type?: string;
  is_horticulture?: boolean;
  is_commercial?: boolean;
  varieties: Array<{ id: string; name: string; canonical_name?: string; grade?: string }>;
  aliases: Array<{ id: string; alias: string; source?: string; confidence: number }>;
  source_mappings: Array<{
    id: string;
    source_code: string;
    external_code: string;
    external_name: string;
    confidence: number;
  }>;
  active_markets: string[];
}

export interface PriceTrend {
  amount: number;
  percent: number;
  direction: "up" | "down" | "stable";
}

export interface MarketPrice {
  id: string;
  crop_id?: string;
  market_id?: string;
  crop_name: string;
  crop_tamil_name?: string;
  market_name: string;
  district: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  price_date: string;
  source: string;
  arrival_quantity?: number | null;
  trend?: PriceTrend;
}

export interface PriceHistoryPoint {
  date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  arrival_quantity?: number | null;
}

export interface Farmer {
  id: string;
  user_id: string;
  fpo_id: string;
  name: string;
  phone: string;
  village: string;
  taluk: string;
  district: string;
  farm_area_acres: number;
  language_preference: string;
  lang?: string;
  alerts_opt_in?: boolean;
  notice_sent_at?: string | null;
  created_at?: string | null;
}

export interface FPO {
  id: string;
  name: string;
  registration_number: string;
  district: string;
  village: string;
  state: string;
  contact_phone: string;
  contact_email?: string | null;
  address?: string | null;
  created_at?: string | null;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  db: string;
}

export interface InboundMessageActivity {
  message_id: string;
  status: string;
  retry_count: number;
  received_at: string | null;
}

export interface WhatsAppActivitySummary {
  enabled: boolean;
  total_inbound: number;
  total_outbound: number;
  inbound_messages: InboundMessageActivity[];
}

export interface WhatsAppUsageSummary {
  month: string;
  total_messages: number;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
  delivery_rate_pct: number;
  estimated_cost_inr: number;
  unreachable_recipients: number;
  monthly_cap: number;
  monthly_budget_inr: number;
  circuit_breaker_tripped: boolean;
}

// ─── Health API ──────────────────────────────────────────────
export async function getHealth(): Promise<HealthStatus> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Health probe HTTP ${res.status}`);
    }
    return await res.json();
  } catch {
    return {
      status: "degraded",
      service: "fpolink-api",
      version: "0.1.0",
      db: "unreachable",
    };
  }
}

// ─── Crops API ───────────────────────────────────────────────
export async function getCrops(): Promise<Crop[]> {
  try {
    const res = await fetch(`${API_BASE}/api/crops/`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.crops)) {
        return data.crops;
      }
    }
  } catch (err) {
    console.warn("Failed to fetch crops from backend:", err);
  }
  return [];
}

// ─── Prices API ──────────────────────────────────────────────
export async function getLatestPrices(district = "Erode"): Promise<MarketPrice[]> {
  try {
    const res = await fetch(`${API_BASE}/api/prices/latest?district=${encodeURIComponent(district)}`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.prices)) {
        return data.prices;
      }
    }
  } catch (err) {
    console.warn("Failed to fetch latest prices from backend:", err);
  }
  return [];
}

export async function getPriceHistory(
  cropId: string,
  marketId: string,
  days = 30
): Promise<PriceHistoryPoint[]> {
  try {
    const res = await fetch(
      `${API_BASE}/api/prices/history?crop_id=${encodeURIComponent(cropId)}&market_id=${encodeURIComponent(marketId)}&days=${days}`,
      { cache: "no-store" }
    );
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.history)) {
        return data.history;
      }
    }
  } catch (err) {
    console.warn("Failed to fetch price history:", err);
  }
  return [];
}

// ─── FPOs API ────────────────────────────────────────────────
export async function getFPOs(): Promise<FPO[]> {
  try {
    const res = await fetch(`${API_BASE}/api/fpos/`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.fpos)) {
        return data.fpos;
      }
    }
  } catch (err) {
    console.warn("Failed to fetch FPOs from backend:", err);
  }
  return [];
}

// ─── Farmers API ─────────────────────────────────────────────
export async function getFarmers(
  fpoId: string,
  token?: string,
  search?: string
): Promise<{ farmers: Farmer[]; total: number }> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const query = search ? `?search=${encodeURIComponent(search)}` : "";
    const res = await fetch(`${API_BASE}/api/farmers/${fpoId}${query}`, {
      headers,
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return {
        farmers: data.farmers || [],
        total: data.total || 0,
      };
    }
  } catch (err) {
    console.warn("Failed to fetch farmers from backend:", err);
  }

  return {
    farmers: [],
    total: 0,
  };
}

export interface FarmerCreatePayload {
  name: string;
  phone: string;
  password: string;
  village: string;
  taluk: string;
  district: string;
  farm_area_acres: number;
  language_preference: string;
  consent_given: boolean;
  lang: string;
  alerts_opt_in: boolean;
}

export async function createFarmer(
  fpoId: string,
  data: FarmerCreatePayload,
  token: string
): Promise<{ farmer: Farmer | null; error: string | null }> {
  try {
    const res = await fetch(`${API_BASE}/api/farmers/${fpoId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
      cache: "no-store",
    });
    if (res.ok) {
      return { farmer: await res.json(), error: null };
    }
    const errData = await res.json().catch(() => ({ detail: "Unknown error" }));
    return { farmer: null, error: errData.detail || `HTTP ${res.status}` };
  } catch (err) {
    return { farmer: null, error: String(err) };
  }
}

export async function login(
  phone: string,
  password: string
): Promise<{ access_token: string; refresh_token: string } | null> {
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Login failed:", err);
  }
  return null;
}

// ─── WhatsApp Activity & Usage Telemetry ─────────────────────
export async function getWhatsAppActivity(limit = 20): Promise<WhatsAppActivitySummary> {
  try {
    const res = await fetch(`${API_BASE}/api/whatsapp/activity?limit=${limit}`, {
      cache: "no-store",
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Failed to fetch WhatsApp activity:", err);
  }

  return {
    enabled: true,
    total_inbound: 0,
    total_outbound: 0,
    inbound_messages: [],
  };
}

export async function getWhatsAppUsage(
  month?: string,
  token?: string
): Promise<WhatsAppUsageSummary | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const query = month ? `?month=${encodeURIComponent(month)}` : "";
    const res = await fetch(`${API_BASE}/api/admin/whatsapp/usage${query}`, {
      headers,
      cache: "no-store",
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Failed to fetch WhatsApp usage metrics:", err);
  }

  return null;
}

// ─── FPO Dashboard Stats ──────────────────────────────────────

export interface FPODashboardStats {
  member_count: number;
  total_farm_area_acres: number;
  crop_distribution: Record<string, number>;
  active_harvests_kg: number;
  revenue_total: number;
}

export async function getFPODashboard(
  fpoId: string,
  token: string
): Promise<FPODashboardStats | null> {
  try {
    const res = await fetch(`${API_BASE}/api/fpos/${fpoId}/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch FPO dashboard stats:", err);
  }
  return null;
}

// ─── Harvest Aggregation ──────────────────────────────────────

export interface HarvestGrade {
  grade: string;
  quantity_kg: number;
  percentage: number;
}

export interface HarvestBatch {
  crop_name: string;
  crop_tamil_name?: string | null;
  total_kg: number;
  farmer_count: number;
  grades: HarvestGrade[];
  warehouse?: string | null;
  status: string;
}

export interface HarvestAggregation {
  total_pooled_kg: number;
  batch_count: number;
  batches: HarvestBatch[];
}

export async function getHarvestAggregation(): Promise<HarvestAggregation> {
  try {
    const res = await fetch(`${API_BASE}/api/harvest/aggregation`, {
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch harvest aggregation:", err);
  }
  return { total_pooled_kg: 0, batch_count: 0, batches: [] };
}

// ─── Commodity Registry ──────────────────────────────────────

export async function getCommodities(category?: string): Promise<CommoditySummary[]> {
  try {
    const url = new URL(`${API_BASE}/api/v1/commodities`);
    if (category) url.searchParams.set("category", category);
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch commodities:", err);
  }
  return [];
}

export async function getCommodityDetail(id: string): Promise<CommodityDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/commodities/${id}`, { cache: "no-store" });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch commodity detail:", err);
  }
  return null;
}

// ─── Ingestion Center Telemetry ──────────────────────────────

export interface IngestionRunItem {
  id: string;
  source_code: string;
  status: string;
  district?: string | null;
  records_fetched: number;
  records_ingested: number;
  error_count: number;
  duration_seconds?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface StatewideFreshness {
  total_districts: number;
  total_canonical_markets: number;
  all_time: {
    reporting_districts: number;
    active_markets: number;
    crops_covered: number;
    latest_price_date?: string | null;
    total_observations: number;
    average_quality_score: number;
  };
  recent_7d: {
    reporting_districts: number;
    active_markets: number;
    crops_covered: number;
  };
  data_sources: Array<{
    code: string;
    name: string;
    priority: number;
    is_active: boolean;
  }>;
}

export async function getIngestionRuns(
  page: number = 1,
  pageSize: number = 10
): Promise<{ items: IngestionRunItem[]; total: number }> {
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/ingestion/runs?page=${page}&page_size=${pageSize}`,
      { cache: "no-store" }
    );
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch ingestion runs:", err);
  }
  return { items: [], total: 0 };
}

export async function getStatewideFreshness(): Promise<StatewideFreshness | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/ingestion/freshness`, {
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch statewide freshness:", err);
  }
  return null;
}

export async function triggerIngestionRun(source?: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/ingestion/trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source }),
    });
    if (res.ok) return await res.json();
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || "Failed to trigger ingestion");
  } catch (err) {
    console.warn("Failed to trigger ingestion run:", err);
    throw err;
  }
}

// ─── Agricultural Intelligence API (v0.7) ───────────────────

export interface ForecastPoint {
  crop_id: string;
  market_id: string;
  target_date: string;
  predicted_price: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
  signal: "hold" | "sell" | "neutral";
  model_type: string;
}

export interface ForecastResponse {
  crop_id: string;
  crop_name: string;
  crop_tamil_name?: string;
  market_id: string;
  market_name: string;
  district: string;
  current_modal_price?: number;
  horizon_days: number;
  forecast: ForecastPoint[];
}

export interface ArbitrageOpportunity {
  target_market_id: string;
  target_market_name: string;
  district: string;
  target_price: number;
  price_date: string;
  distance_km: number;
  gross_spread: number;
  transport_cost: number;
  net_spread: number;
  recommendation: "strong_arbitrage" | "profitable_dispatch" | "local_preferred";
}

export interface ArbitrageResponse {
  crop_id: string;
  crop_name: string;
  crop_tamil_name?: string;
  origin_market_id: string;
  origin_market_name: string;
  origin_district: string;
  origin_price?: number;
  origin_price_date?: string;
  total_destinations_analyzed: number;
  opportunities: ArbitrageOpportunity[];
}

export interface SpreadPoint {
  market_id: string;
  market_name: string;
  district: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  price_date: string;
  quality_score?: number;
}

export interface SpreadsResponse {
  crop_id: string;
  crop_name: string;
  crop_tamil_name?: string;
  district_filter?: string;
  min_price: number;
  max_price: number;
  median_price: number;
  price_spread: number;
  reporting_markets_count: number;
  markets: SpreadPoint[];
}

export interface DistrictItem {
  id: string;
  name: string;
  code: string;
}

export async function getDistricts(): Promise<DistrictItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/geography/districts`, { cache: "no-store" });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch districts:", err);
  }
  return [];
}

export async function getForecast(
  cropId: string,
  marketId: string,
  days: number = 7
): Promise<ForecastResponse | null> {
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/intelligence/forecast?crop_id=${encodeURIComponent(cropId)}&market_id=${encodeURIComponent(marketId)}&days=${days}`,
      { cache: "no-store" }
    );
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch forecast:", err);
  }
  return null;
}

export async function getArbitrage(
  cropId: string,
  originMarketId: string,
  maxDistanceKm: number = 300
): Promise<ArbitrageResponse | null> {
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/intelligence/arbitrage?crop_id=${encodeURIComponent(cropId)}&origin_market_id=${encodeURIComponent(originMarketId)}&max_distance_km=${maxDistanceKm}`,
      { cache: "no-store" }
    );
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch arbitrage:", err);
  }
  return null;
}

export async function getSpreads(
  cropId: string,
  district?: string
): Promise<SpreadsResponse | null> {
  try {
    const url = district && district !== "all"
      ? `${API_BASE}/api/v1/intelligence/spreads?crop_id=${encodeURIComponent(cropId)}&district=${encodeURIComponent(district)}`
      : `${API_BASE}/api/v1/intelligence/spreads?crop_id=${encodeURIComponent(cropId)}`;
    const res = await fetch(url, { cache: "no-store" });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch spreads:", err);
  }
  return null;
}

// ---------------------------------------------------------------------------
// Phase 13 (v0.8): Supply + Demand Network API Client
// ---------------------------------------------------------------------------

export interface FarmPlot {
  id: string;
  farmer_id: string;
  farmer_name?: string | null;
  farmer_phone?: string | null;
  crop_id: string;
  crop_name?: string | null;
  crop_tamil_name?: string | null;
  plot_name: string;
  area_acres: number;
  village: string;
  soil_type?: string | null;
  irrigation_type?: string | null;
  sowing_date?: string | null;
  expected_harvest_date?: string | null;
  expected_yield_kg?: number | null;
  actual_yield_kg?: number | null;
  status: string;
  district_id?: string | null;
  district_name?: string | null;
  taluk_id?: string | null;
  taluk_name?: string | null;
  created_at?: string | null;
}

export interface FarmPlotListResponse {
  plots: FarmPlot[];
  total: number;
  total_area_acres: number;
}

export interface FarmCreatePayload {
  farmer_id: string;
  crop_id: string;
  plot_name: string;
  area_acres: number;
  village: string;
  soil_type?: string;
  irrigation_type?: string;
  sowing_date?: string;
  status?: string;
  district_id?: string;
  taluk_id?: string;
}

export interface FarmYieldEstimate {
  crop_name: string;
  area_acres: number;
  base_yield_kg_per_acre: number;
  soil_factor: number;
  irrigation_factor: number;
  estimated_yield_kg: number;
  estimated_harvest_window_start?: string | null;
  estimated_harvest_window_end?: string | null;
  confidence_note: string;
}

export async function getFarmPlots(
  params: {
    farmer_id?: string;
    fpo_id?: string;
    crop_id?: string;
    district?: string;
    status?: string;
    page?: number;
    page_size?: number;
  },
  token?: string
): Promise<FarmPlotListResponse> {
  try {
    const q = new URLSearchParams();
    if (params.farmer_id) q.set("farmer_id", params.farmer_id);
    if (params.fpo_id) q.set("fpo_id", params.fpo_id);
    if (params.crop_id) q.set("crop_id", params.crop_id);
    if (params.district) q.set("district", params.district);
    if (params.status) q.set("status", params.status);
    if (params.page) q.set("page", params.page.toString());
    if (params.page_size) q.set("page_size", params.page_size.toString());

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/farms/?${q.toString()}`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch farm plots:", err);
  }
  return { plots: [], total: 0, total_area_acres: 0 };
}

export async function createFarmPlot(
  payload: FarmCreatePayload,
  token?: string
): Promise<FarmPlot | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/farms/`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
    const err = await res.json();
    throw new Error(err.detail || "Failed to create farm plot");
  } catch (err: any) {
    console.error("createFarmPlot error:", err);
    throw err;
  }
}

export async function getFarmYieldEstimate(
  farmId: string,
  token?: string
): Promise<FarmYieldEstimate | null> {
  try {
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/farms/${farmId}/yield-estimate`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch yield estimate:", err);
  }
  return null;
}

export async function deleteFarmPlot(farmId: string, token?: string): Promise<boolean> {
  try {
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/farms/${farmId}`, {
      method: "DELETE",
      headers,
    });
    return res.ok;
  } catch (err) {
    console.warn("Failed to delete farm plot:", err);
    return false;
  }
}

// ---------------------------------------------------------------------------
// Buyers & Requirements
// ---------------------------------------------------------------------------

export interface Buyer {
  id: string;
  company_name: string;
  buyer_type: string;
  contact_name?: string | null;
  contact_phone: string;
  contact_email?: string | null;
  location: string;
  district?: string | null;
  gstin?: string | null;
  verified: boolean;
  open_requirements_count: number;
  created_at?: string | null;
}

export interface BuyerListResponse {
  buyers: Buyer[];
  total: number;
}

export interface BuyerCreatePayload {
  company_name: string;
  buyer_type: string;
  contact_name?: string;
  contact_phone: string;
  contact_email?: string;
  location: string;
  district?: string;
  fpo_id?: string;
  gstin?: string;
  verified?: boolean;
}

export interface BuyerRequirement {
  id: string;
  buyer_id: string;
  buyer_name?: string | null;
  buyer_phone?: string | null;
  fpo_id?: string | null;
  crop_id: string;
  crop_name?: string | null;
  crop_tamil_name?: string | null;
  variety_id?: string | null;
  variety_name?: string | null;
  quantity_kg: number;
  fulfilled_quantity_kg: number;
  min_grade: string;
  required_date: string;
  delivery_window_days: number;
  max_price_per_kg?: number | null;
  delivery_location?: string | null;
  status: string;
  notes?: string | null;
  created_at?: string | null;
}

export interface BuyerRequirementListResponse {
  requirements: BuyerRequirement[];
  total: number;
  total_quantity_kg: number;
}

export interface BuyerRequirementCreatePayload {
  buyer_id: string;
  fpo_id?: string;
  crop_id: string;
  variety_id?: string;
  quantity_kg: number;
  min_grade: string;
  required_date: string;
  delivery_window_days?: number;
  max_price_per_kg?: number;
  delivery_location?: string;
  notes?: string;
}

export async function getBuyers(
  params?: {
    fpo_id?: string;
    district?: string;
    buyer_type?: string;
    page?: number;
    page_size?: number;
  },
  token?: string
): Promise<BuyerListResponse> {
  try {
    const q = new URLSearchParams();
    if (params?.fpo_id) q.set("fpo_id", params.fpo_id);
    if (params?.district) q.set("district", params.district);
    if (params?.buyer_type) q.set("buyer_type", params.buyer_type);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/buyers/?${q.toString()}`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch buyers:", err);
  }
  return { buyers: [], total: 0 };
}

export async function createBuyer(
  payload: BuyerCreatePayload,
  token?: string
): Promise<Buyer | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/buyers/`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
    const err = await res.json();
    throw new Error(err.detail || "Failed to create buyer");
  } catch (err: any) {
    console.error("createBuyer error:", err);
    throw err;
  }
}

export async function getBuyerRequirements(
  params?: {
    buyer_id?: string;
    fpo_id?: string;
    crop_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  },
  token?: string
): Promise<BuyerRequirementListResponse> {
  try {
    const q = new URLSearchParams();
    if (params?.buyer_id) q.set("buyer_id", params.buyer_id);
    if (params?.fpo_id) q.set("fpo_id", params.fpo_id);
    if (params?.crop_id) q.set("crop_id", params.crop_id);
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/buyers/requirements?${q.toString()}`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch buyer requirements:", err);
  }
  return { requirements: [], total: 0, total_quantity_kg: 0 };
}

export async function createBuyerRequirement(
  payload: BuyerRequirementCreatePayload,
  token?: string
): Promise<BuyerRequirement | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/buyers/requirements`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
    const err = await res.json();
    throw new Error(err.detail || "Failed to create buyer requirement");
  } catch (err: any) {
    console.error("createBuyerRequirement error:", err);
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Matching Engine & Balance Summary
// ---------------------------------------------------------------------------

export interface MatchBreakdown {
  crop_match: boolean;
  distance_km?: number | null;
  proximity_score: number;
  quantity_fit_ratio: number;
  timing_days_delta?: number | null;
  timing_score: number;
  grade_score: number;
  composite_score: number;
}

export interface MatchCandidate {
  candidate_type: "farm_plot" | "harvest";
  source_id: string;
  farmer_id: string;
  farmer_name: string;
  farmer_phone: string;
  farmer_alerts_opt_in: boolean;
  village?: string | null;
  district?: string | null;
  crop_id: string;
  crop_name: string;
  crop_tamil_name?: string | null;
  available_quantity_kg: number;
  grade?: string | null;
  available_date?: string | null;
  distance_km?: number | null;
  match_score: number;
  match_breakdown: MatchBreakdown;
}

export interface MatchCandidateListResponse {
  requirement_id: string;
  buyer_id: string;
  buyer_name: string;
  crop_name: string;
  required_quantity_kg: number;
  required_date: string;
  delivery_location?: string | null;
  candidates: MatchCandidate[];
  total_candidates: number;
}

export interface SupplyMatchItem {
  id: string;
  buyer_requirement_id: string;
  buyer_name?: string | null;
  farm_id?: string | null;
  harvest_id?: string | null;
  fpo_id: string;
  farmer_id?: string | null;
  farmer_name?: string | null;
  farmer_phone?: string | null;
  crop_name?: string | null;
  matched_quantity_kg: number;
  offered_price_per_kg?: number | null;
  match_score: number;
  match_breakdown?: MatchBreakdown | null;
  status: string;
  staff_notes?: string | null;
  confirmed_by_name?: string | null;
  confirmed_at?: string | null;
  notified_at?: string | null;
  farmer_responded_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SupplyDemandCropSummary {
  crop_id: string;
  crop_name: string;
  crop_tamil_name?: string | null;
  standing_acres: number;
  standing_yield_kg: number;
  verified_harvest_kg: number;
  total_supply_kg: number;
  total_demand_kg: number;
  net_balance_kg: number;
  active_plots_count: number;
  open_requirements_count: number;
}

export interface SupplyDemandSummary {
  fpo_id?: string | null;
  district?: string | null;
  commodities: SupplyDemandCropSummary[];
  total_standing_acres: number;
  total_supply_kg: number;
  total_demand_kg: number;
  active_plots_total: number;
  open_requirements_total: number;
}

export async function getCandidatesForRequirement(
  requirementId: string,
  maxCandidates: number = 15,
  token?: string
): Promise<MatchCandidateListResponse | null> {
  try {
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(
      `${API_BASE}/api/v1/matching/candidates/${requirementId}?max_candidates=${maxCandidates}`,
      { headers, cache: "no-store" }
    );
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch matching candidates:", err);
  }
  return null;
}

export async function suggestMatch(
  payload: {
    buyer_requirement_id: string;
    fpo_id: string;
    farm_id?: string;
    harvest_id?: string;
    matched_quantity_kg: number;
    match_score: number;
    match_breakdown?: any;
    offered_price_per_kg?: number;
    staff_notes?: string;
  },
  token?: string
): Promise<SupplyMatchItem | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/matching/suggest`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
    const err = await res.json();
    throw new Error(err.detail || "Failed to create match");
  } catch (err: any) {
    console.error("suggestMatch error:", err);
    throw err;
  }
}

export async function confirmMatch(
  matchId: string,
  payload: { staff_notes?: string; offered_price_per_kg?: number },
  token?: string
): Promise<SupplyMatchItem | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/matching/${matchId}/confirm`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
    const err = await res.json();
    throw new Error(err.detail || "Failed to confirm match");
  } catch (err: any) {
    console.error("confirmMatch error:", err);
    throw err;
  }
}

export async function rejectMatch(
  matchId: string,
  notes?: string,
  token?: string
): Promise<SupplyMatchItem | null> {
  try {
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const url = notes
      ? `${API_BASE}/api/v1/matching/${matchId}/reject?notes=${encodeURIComponent(notes)}`
      : `${API_BASE}/api/v1/matching/${matchId}/reject`;

    const res = await fetch(url, {
      method: "POST",
      headers,
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to reject match:", err);
  }
  return null;
}

export async function getSupplyDemandSummary(
  params?: { fpo_id?: string; district?: string },
  token?: string
): Promise<SupplyDemandSummary | null> {
  try {
    const q = new URLSearchParams();
    if (params?.fpo_id) q.set("fpo_id", params.fpo_id);
    if (params?.district) q.set("district", params.district);

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/matching/summary?${q.toString()}`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to fetch supply demand summary:", err);
  }
  return null;
}

export async function listSupplyMatches(
  params?: { fpo_id?: string; status?: string; page?: number; page_size?: number },
  token?: string
): Promise<{ matches: SupplyMatchItem[]; total: number }> {
  try {
    const q = new URLSearchParams();
    if (params?.fpo_id) q.set("fpo_id", params.fpo_id);
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/v1/matching/list?${q.toString()}`, {
      headers,
      cache: "no-store",
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Failed to list supply matches:", err);
  }
  return { matches: [], total: 0 };
}



