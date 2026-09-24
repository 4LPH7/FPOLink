"use client";

import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import {
  TrendingUp,
  ShieldCheck,
  Calendar,
  RefreshCw,
  BarChart2,
} from "lucide-react";
import { getLatestPrices, getPriceHistory, MarketPrice, PriceHistoryPoint } from "@/lib/api";

interface PriceChartProps {
  lang: "ta" | "en";
  t: any;
}

export default function PriceChart({ lang, t }: PriceChartProps) {
  const [selectedCrop, setSelectedCrop] = useState<"turmeric" | "banana">("turmeric");
  const [timeframe, setTimeframe] = useState<"7d" | "30d" | "90d">("30d");
  const [history, setHistory] = useState<PriceHistoryPoint[]>([]);
  const [currentPrice, setCurrentPrice] = useState<MarketPrice | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchChartHistory = async (cropName: "turmeric" | "banana", days: number) => {
    setLoading(true);
    try {
      const prices = await getLatestPrices("Erode");
      const price = prices.find((p) =>
        p.crop_name.toLowerCase().includes(cropName)
      );

      // Use crop_id and market_id returned by the API (added to response)
      if (price && price.crop_id && price.market_id) {
        const hist = await getPriceHistory(price.crop_id, price.market_id, days);
        setCurrentPrice(price);
        setHistory(hist);
      } else if (price) {
        // Fallback: show current price card even if no history
        setCurrentPrice(price);
        setHistory([]);
      } else {
        setCurrentPrice(null);
        setHistory([]);
      }
    } catch (err) {
      console.warn("Failed to load price history:", err);
      setCurrentPrice(null);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const days = timeframe === "7d" ? 7 : timeframe === "90d" ? 90 : 30;
    fetchChartHistory(selectedCrop, days);
  }, [selectedCrop, timeframe]);

  // Prices in DB are ₹/kg — multiply by 100 to show ₹/quintal
  const chartData = history.map((pt) => ({
    date: pt.date ? pt.date.slice(5) : "",
    modal: Math.round(Number(pt.modal_price) * 100),
    min: Math.round(Number(pt.min_price) * 100),
    max: Math.round(Number(pt.max_price) * 100),
  }));

  const latestPoint = chartData[chartData.length - 1];
  const previousPoint = chartData[chartData.length - 2] || chartData[0];
  const priceDiff = latestPoint && previousPoint ? latestPoint.modal - previousPoint.modal : 0;
  const pctChange =
    previousPoint && previousPoint.modal > 0
      ? ((priceDiff / previousPoint.modal) * 100).toFixed(1)
      : "0.0";

  // Use currentPrice as fallback KPI when history is empty
  const displayModal = latestPoint
    ? latestPoint.modal
    : currentPrice
    ? Math.round(Number(currentPrice.modal_price) * 100)
    : null;
  const displayMin = latestPoint
    ? latestPoint.min
    : currentPrice
    ? Math.round(Number(currentPrice.min_price) * 100)
    : null;
  const displayMax = latestPoint
    ? latestPoint.max
    : currentPrice
    ? Math.round(Number(currentPrice.max_price) * 100)
    : null;

  return (
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200/90 dark:border-border p-5 sm:p-6 shadow-xs hover:shadow-md transition-all">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-gray-100 dark:border-border gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-gray-900 dark:text-foreground tracking-tight flex items-center">
              <TrendingUp className="w-5 h-5 text-emerald-600 mr-2" />
              {t.dashboard.market_prices} —{" "}
              {lang === "ta"
                ? selectedCrop === "turmeric"
                  ? "ஈரோடு மஞ்சள்"
                  : "ஈரோடு வாழை"
                : selectedCrop === "turmeric"
                ? "Erode Turmeric"
                : "Erode Banana"}
            </h2>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
              <ShieldCheck className="w-3 h-3 mr-1 text-emerald-700 dark:text-emerald-400" />
              {lang === "ta" ? "நேரலை Agmarknet" : "Live Agmarknet"}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {lang === "ta"
              ? "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடத்தின் மாதிரி விலை நிலவரம் (ரூ./குவிண்டால்)"
              : "Daily modal auction rates from official Erode regulated mandis (₹/quintal)"}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 self-start sm:self-auto">
          <div className="inline-flex p-1 bg-gray-100 dark:bg-muted rounded-xl text-xs font-medium">
            <button
              onClick={() => setSelectedCrop("turmeric")}
              className={`px-3 py-1 rounded-lg transition-all ${
                selectedCrop === "turmeric"
                  ? "bg-white dark:bg-card text-emerald-700 dark:text-emerald-400 font-bold shadow-xs"
                  : "text-gray-500 dark:text-muted-foreground hover:text-gray-700"
              }`}
            >
              {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
            </button>
            <button
              onClick={() => setSelectedCrop("banana")}
              className={`px-3 py-1 rounded-lg transition-all ${
                selectedCrop === "banana"
                  ? "bg-white dark:bg-card text-emerald-700 dark:text-emerald-400 font-bold shadow-xs"
                  : "text-gray-500 dark:text-muted-foreground hover:text-gray-700"
              }`}
            >
              {lang === "ta" ? "வாழை" : "Banana"}
            </button>
          </div>

          <div className="hidden sm:inline-flex p-1 bg-gray-100 dark:bg-muted rounded-xl text-xs font-medium">
            <button
              onClick={() => setTimeframe("7d")}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                timeframe === "7d"
                  ? "bg-white dark:bg-card text-gray-900 dark:text-foreground font-bold shadow-xs"
                  : "text-gray-500 dark:text-muted-foreground hover:text-gray-700"
              }`}
            >
              7D
            </button>
            <button
              onClick={() => setTimeframe("30d")}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                timeframe === "30d"
                  ? "bg-white dark:bg-card text-gray-900 dark:text-foreground font-bold shadow-xs"
                  : "text-gray-500 dark:text-muted-foreground hover:text-gray-700"
              }`}
            >
              30D
            </button>
          </div>
        </div>
      </div>

      {/* Metric Highlight */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 my-2 border-b border-gray-100 dark:border-border">
        <div>
          <span className="text-xs text-muted-foreground block">
            {lang === "ta" ? "தற்போதைய மாதிரி விலை" : "Current Modal Price"}
          </span>
          <span className="text-xl sm:text-2xl font-black text-gray-900 dark:text-foreground">
            {displayModal !== null ? `₹${displayModal.toLocaleString("en-IN")}` : "—"}
          </span>
          <span className="text-[10px] text-muted-foreground block">/ {lang === "ta" ? "குவிண்டால்" : "quintal"}</span>
        </div>

        <div>
          <span className="text-xs text-muted-foreground block">
            {lang === "ta" ? "விலை மாற்றம்" : "Price Movement"}
          </span>
          <div className="flex items-center space-x-1 mt-0.5">
            <span
              className={`text-sm sm:text-base font-bold ${
                Number(pctChange) >= 0 ? "text-emerald-600" : "text-destructive"
              }`}
            >
              {Number(pctChange) >= 0 ? `+${pctChange}%` : `${pctChange}%`}
            </span>
          </div>
          <span className="text-[10px] text-muted-foreground block">
            {priceDiff >= 0 ? `+₹${priceDiff}` : `-₹${Math.abs(priceDiff)}`}
          </span>
        </div>

        <div>
          <span className="text-xs text-muted-foreground block">
            {lang === "ta" ? "குறைந்தபட்ச விலை" : "Minimum Auction"}
          </span>
          <span className="text-lg font-bold text-gray-700 dark:text-muted-foreground">
            {displayMin !== null ? `₹${displayMin.toLocaleString("en-IN")}` : "—"}
          </span>
          <span className="text-[10px] text-muted-foreground block">/ {lang === "ta" ? "குவிண்டால்" : "quintal"}</span>
        </div>

        <div>
          <span className="text-xs text-muted-foreground block">
            {lang === "ta" ? "அதிகபட்ச விலை" : "Maximum Auction"}
          </span>
          <span className="text-lg font-bold text-gray-700 dark:text-muted-foreground">
            {displayMax !== null ? `₹${displayMax.toLocaleString("en-IN")}` : "—"}
          </span>
          <span className="text-[10px] text-muted-foreground block">/ {lang === "ta" ? "குவிண்டால்" : "quintal"}</span>
        </div>
      </div>

      {/* Chart Area */}
      <div className="pt-3">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <RefreshCw className="w-5 h-5 animate-spin mr-2" />
            <span>{lang === "ta" ? "ஏற்றுகிறது..." : "Loading price observations..."}</span>
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-muted-foreground p-4 text-center">
            <BarChart2 className="w-10 h-10 mb-2 opacity-40" />
            <p className="font-medium text-sm">
              {lang === "ta" ? "விலை வரலாற்றுத் தகவல்கள் இல்லை" : "No price history available"}
            </p>
            <p className="text-xs mt-1 text-muted-foreground">
              {lang === "ta" ? "தினசரி மண்டி தகவல் பெறப்பட்டதும் வரைபடம் தோன்றும்." : "Live series will render once observations are ingested."}
            </p>
          </div>
        ) : (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorModal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.2} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${v}`} />
                <Tooltip formatter={(v: number) => [`₹${v}`, lang === "ta" ? "மாதிரி விலை" : "Modal Price"]} />
                <Area
                  type="monotone"
                  dataKey="modal"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorModal)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
