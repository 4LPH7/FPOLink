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

export interface PriceTrend {
  amount: number;
  percent: number;
  direction: "up" | "down" | "stable";
}

export interface MarketPrice {
  id: string;
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
