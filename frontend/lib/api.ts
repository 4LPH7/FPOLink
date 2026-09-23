/**
 * FPOLink TN — Frontend API Client
 *
 * Provides typed, resilient access to the FastAPI backend with seamless
 * fallback to local curated datasets when backend is offline or before
 * the daily mandi ingestion sweep.
 */

import { MANDI_DATA, TURMERIC_DATA_30D, BANANA_DATA_30D, MandiRow } from "./marketData";

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
  alerts_opt_in: boolean;
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
  } catch (err) {
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
      next: { revalidate: 3600 },
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.crops) && data.crops.length > 0) {
        return data.crops;
      }
    }
  } catch {
    // Backend unreachable, fallback to defaults
  }

  return [
    { id: "1", name: "turmeric", tamil_name: "மஞ்சள்", category: "spice", unit: "kg" },
    { id: "2", name: "banana", tamil_name: "வாழைப்பழம்", category: "fruit", unit: "kg" },
    { id: "3", name: "coconut", tamil_name: "தேங்காய்", category: "plantation", unit: "unit" },
  ];
}

// ─── Prices API ──────────────────────────────────────────────
export async function getLatestPrices(district = "Erode"): Promise<MarketPrice[]> {
  try {
    const res = await fetch(`${API_BASE}/api/prices/latest?district=${encodeURIComponent(district)}`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.prices) && data.prices.length > 0) {
        return data.prices;
      }
    }
  } catch {
    // Fallback to verified local market rows
  }

  // Transform local MANDI_DATA to MarketPrice structure
  return MANDI_DATA.map((row: MandiRow) => ({
    id: row.id,
    crop_name: row.cropEn.toLowerCase(),
    crop_tamil_name: row.cropTa,
    market_name: row.mandiEn,
    district: row.district,
    min_price: row.min,
    max_price: row.max,
    modal_price: row.modal,
    price_date: row.date,
    source: row.source,
    trend: {
      amount: row.change,
      percent: Math.abs(row.change / row.modal) * 100,
      direction: row.change > 0 ? "up" : row.change < 0 ? "down" : "stable",
    },
  }));
}

// ─── FPOs API ────────────────────────────────────────────────
export async function getFPOs(): Promise<FPO[]> {
  try {
    const res = await fetch(`${API_BASE}/api/fpos/`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.fpos) && data.fpos.length > 0) {
        return data.fpos;
      }
    }
  } catch {
    // Fallback
  }

  return [
    {
      id: "fpo-erode-01",
      name: "Erode Farmers Collective",
      registration_number: "FPO-TN-ERD-001",
      district: "Erode",
      village: "Perundurai",
      state: "Tamil Nadu",
      contact_phone: "9999900001",
    },
  ];
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
  } catch {
    // Fallback
  }

  // Curated demo farmers for offline/showcase mode
  const localFarmers: Farmer[] = [
    {
      id: "farmer-01",
      user_id: "user-01",
      fpo_id: fpoId,
      name: "Ramasamy",
      phone: "+91 98765 43210",
      village: "Kodumudi",
      taluk: "Kodumudi",
      district: "Erode",
      farm_area_acres: 3.5,
      language_preference: "ta",
      lang: "ta",
      alerts_opt_in: true,
      notice_sent_at: "2026-09-20T08:00:00Z",
      created_at: "2026-09-01T00:00:00Z",
    },
    {
      id: "farmer-02",
      user_id: "user-02",
      fpo_id: fpoId,
      name: "Kuppusamy",
      phone: "+91 98765 43211",
      village: "Perundurai",
      taluk: "Perundurai",
      district: "Erode",
      farm_area_acres: 2.0,
      language_preference: "ta",
      lang: "ta",
      alerts_opt_in: false,
      notice_sent_at: "2026-09-21T09:30:00Z",
      created_at: "2026-09-05T00:00:00Z",
    },
    {
      id: "farmer-03",
      user_id: "user-03",
      fpo_id: fpoId,
      name: "Murugesan K.",
      phone: "+91 94432 10987",
      village: "Modakkurichi",
      taluk: "Modakkurichi",
      district: "Erode",
      farm_area_acres: 5.0,
      language_preference: "ta",
      lang: "ta",
      alerts_opt_in: true,
      notice_sent_at: null,
      created_at: "2026-09-10T00:00:00Z",
    },
  ];

  const filtered = search
    ? localFarmers.filter(
        (f) =>
          f.name.toLowerCase().includes(search.toLowerCase()) ||
          f.village.toLowerCase().includes(search.toLowerCase())
      )
    : localFarmers;

  return {
    farmers: filtered,
    total: filtered.length,
  };
}
