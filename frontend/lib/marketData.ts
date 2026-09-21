// Shared Market Data & Pricing Source of Truth for FPOLink TN

export interface PricePoint {
  date: string;
  dateTa: string;
  modal: number;
  min: number;
  max: number;
  mandi: string;
  anomaly: boolean;
}

export interface MandiRow {
  id: string;
  cropEn: string;
  cropTa: string;
  mandiEn: string;
  mandiTa: string;
  district: string;
  modal: number;
  min: number;
  max: number;
  change: number;
  date: string;
  source: "ogd" | "ceda";
}

// 30-Day Historical Data Points for Erode Mandis (Turmeric & Banana)
export const TURMERIC_DATA_30D: PricePoint[] = [
  { date: "08/20", dateTa: "ஆக 20", modal: 11400, min: 10800, max: 11900, mandi: "பெருந்துறை", anomaly: false },
  { date: "08/23", dateTa: "ஆக 23", modal: 11550, min: 10900, max: 12050, mandi: "செம்மாம்பாளையம்", anomaly: false },
  { date: "08/26", dateTa: "ஆக 26", modal: 11600, min: 11000, max: 12100, mandi: "பெருந்துறை", anomaly: false },
  { date: "08/29", dateTa: "ஆக 29", modal: 11750, min: 11100, max: 12250, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/01", dateTa: "செப் 01", modal: 11800, min: 11150, max: 12300, mandi: "கோபிசெட்டிபாளையம்", anomaly: false },
  { date: "09/04", dateTa: "செப் 04", modal: 11920, min: 11200, max: 12400, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/07", dateTa: "செப் 07", modal: 12100, min: 11400, max: 12600, mandi: "செம்மாம்பாளையம்", anomaly: false },
  { date: "09/10", dateTa: "செப் 10", modal: 12050, min: 11300, max: 12550, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/13", dateTa: "செப் 13", modal: 12850, min: 12100, max: 13400, mandi: "பெருந்துறை", anomaly: true }, // MAD Anomaly spike
  { date: "09/16", dateTa: "செப் 16", modal: 12200, min: 11500, max: 12700, mandi: "கொடுமுடி", anomaly: false },
  { date: "09/19", dateTa: "செப் 19", modal: 12350, min: 11650, max: 12850, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/21", dateTa: "செப் 21", modal: 12480, min: 11700, max: 13000, mandi: "பெருந்துறை", anomaly: false },
];

export const BANANA_DATA_30D: PricePoint[] = [
  { date: "08/20", dateTa: "ஆக 20", modal: 2650, min: 2400, max: 2850, mandi: "கொடுமுடி", anomaly: false },
  { date: "08/23", dateTa: "ஆக 23", modal: 2700, min: 2450, max: 2900, mandi: "ஈரோடு", anomaly: false },
  { date: "08/26", dateTa: "ஆக 26", modal: 2680, min: 2400, max: 2880, mandi: "கொடுமுடி", anomaly: false },
  { date: "08/29", dateTa: "ஆக 29", modal: 2720, min: 2500, max: 2950, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/01", dateTa: "செப் 01", modal: 2750, min: 2500, max: 3000, mandi: "ஈரோடு", anomaly: false },
  { date: "09/04", dateTa: "செப் 04", modal: 2790, min: 2550, max: 3050, mandi: "கொடுமுடி", anomaly: false },
  { date: "09/07", dateTa: "செப் 07", modal: 2820, min: 2600, max: 3100, mandi: "கோபிசெட்டிபாளையம்", anomaly: false },
  { date: "09/10", dateTa: "செப் 10", modal: 2800, min: 2550, max: 3050, mandi: "ஈரோடு", anomaly: false },
  { date: "09/13", dateTa: "செப் 13", modal: 2840, min: 2600, max: 3120, mandi: "கொடுமுடி", anomaly: false },
  { date: "09/16", dateTa: "செப் 16", modal: 2860, min: 2650, max: 3150, mandi: "பெருந்துறை", anomaly: false },
  { date: "09/19", dateTa: "செப் 19", modal: 2890, min: 2680, max: 3180, mandi: "ஈரோடு", anomaly: false },
  { date: "09/21", dateTa: "செப் 21", modal: 2920, min: 2700, max: 3200, mandi: "கொடுமுடி", anomaly: false },
];

export const MANDI_DATA: MandiRow[] = [
  {
    id: "m1",
    cropEn: "Turmeric (Finger)",
    cropTa: "மஞ்சள் (விரலி)",
    mandiEn: "Perundurai Regulated Market",
    mandiTa: "பெருந்துறை ஒழுங்குமுறை விற்பனைக்கூடம்",
    district: "Erode",
    modal: 12480,
    min: 11700,
    max: 13000,
    change: 2.4,
    date: "2026-09-21",
    source: "ogd",
  },
  {
    id: "m2",
    cropEn: "Turmeric (Bulb)",
    cropTa: "மஞ்சள் (கிழங்கு)",
    mandiEn: "Erode Semmampalayam Market",
    mandiTa: "ஈரோடு செம்மாம்பாளையம் சந்தை",
    district: "Erode",
    modal: 11650,
    min: 10900,
    max: 12150,
    change: 1.2,
    date: "2026-09-21",
    source: "ogd",
  },
  {
    id: "m3",
    cropEn: "Banana (Nendran)",
    cropTa: "வாழை (நேந்திரன்)",
    mandiEn: "Kodumudi Regulated Market",
    mandiTa: "கொடுமுடி ஒழுங்குமுறை விற்பனைக்கூடம்",
    district: "Erode",
    modal: 2920,
    min: 2700,
    max: 3200,
    change: 1.8,
    date: "2026-09-21",
    source: "ogd",
  },
  {
    id: "m4",
    cropEn: "Banana (Poovan)",
    cropTa: "வாழை (பூவன்)",
    mandiEn: "Gobichettipalayam Market",
    mandiTa: "கோபிசெட்டிபாளையம் சந்தை",
    district: "Erode",
    modal: 2450,
    min: 2200,
    max: 2700,
    change: -0.8,
    date: "2026-09-20",
    source: "ceda",
  },
  {
    id: "m5",
    cropEn: "Coconut (De-husked)",
    cropTa: "தேங்காய் (மட்டை உரித்தது)",
    mandiEn: "Erode Regulated Market",
    mandiTa: "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடம்",
    district: "Erode",
    modal: 2850,
    min: 2600,
    max: 3100,
    change: 0.5,
    date: "2026-09-21",
    source: "ogd",
  },
];

export function getLatestMarketRates() {
  const latestTurmeric = TURMERIC_DATA_30D[TURMERIC_DATA_30D.length - 1];
  const prevTurmeric = TURMERIC_DATA_30D[TURMERIC_DATA_30D.length - 2] || latestTurmeric;
  const turmericDiff = latestTurmeric.modal - prevTurmeric.modal;
  const turmericPct = ((turmericDiff / prevTurmeric.modal) * 100).toFixed(1);

  const latestBanana = BANANA_DATA_30D[BANANA_DATA_30D.length - 1];
  const prevBanana = BANANA_DATA_30D[BANANA_DATA_30D.length - 2] || latestBanana;
  const bananaDiff = latestBanana.modal - prevBanana.modal;
  const bananaPct = ((bananaDiff / prevBanana.modal) * 100).toFixed(1);

  return {
    turmeric: {
      rate: `₹${latestTurmeric.modal.toLocaleString("en-IN")}`,
      rawRate: latestTurmeric.modal,
      mandiTa: `${latestTurmeric.mandi} மண்டி`,
      mandiEn: `${latestTurmeric.mandi} Mandi`,
      change: `${turmericDiff >= 0 ? "+" : ""}${turmericPct}%`,
      changeType: turmericDiff >= 0 ? ("positive" as const) : ("negative" as const),
      date: latestTurmeric.date,
      dateTa: latestTurmeric.dateTa,
    },
    banana: {
      rate: `₹${latestBanana.modal.toLocaleString("en-IN")}`,
      rawRate: latestBanana.modal,
      mandiTa: `${latestBanana.mandi} மண்டி`,
      mandiEn: `${latestBanana.mandi} Mandi`,
      change: `${bananaDiff >= 0 ? "+" : ""}${bananaPct}%`,
      changeType: bananaDiff >= 0 ? ("positive" as const) : ("negative" as const),
      date: latestBanana.date,
      dateTa: latestBanana.dateTa,
    },
    lastUpdated: "2026-09-21 06:00 IST",
  };
}
