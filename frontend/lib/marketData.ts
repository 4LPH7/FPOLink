// Shared Market Data & Pricing Interfaces for FPOLink TN
// 100% Dynamic — All data is sourced directly from PostgreSQL & Agmarknet/OGD live APIs

export interface PricePoint {
  date: string;
  dateTa?: string;
  modal: number;
  min: number;
  max: number;
  mandi?: string;
  arrival_quantity?: number | null;
  anomaly?: boolean;
}

export interface MandiRow {
  id: string;
  cropEn: string;
  cropTa?: string;
  mandiEn: string;
  mandiTa?: string;
  district: string;
  modal: number;
  min: number;
  max: number;
  change?: number;
  date: string;
  source: string;
}
