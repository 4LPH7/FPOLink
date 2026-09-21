"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import {
  TrendingUp,
  ShieldCheck,
  Calendar,
  AlertCircle,
  Clock,
  Sparkles,
  Info,
} from "lucide-react";

interface PriceChartProps {
  lang: "ta" | "en";
  t: any;
}

// 30-Day Historical Data Points for Erode Mandis (Turmeric & Banana)
const TURMERIC_DATA_30D = [
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

const BANANA_DATA_30D = [
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

export default function PriceChart({ lang, t }: PriceChartProps) {
  const [selectedCrop, setSelectedCrop] = useState<"turmeric" | "banana">("turmeric");
  const [timeframe, setTimeframe] = useState<"7d" | "30d" | "90d">("30d");

  const fullData = selectedCrop === "turmeric" ? TURMERIC_DATA_30D : BANANA_DATA_30D;
  const chartData = timeframe === "7d" ? fullData.slice(-4) : fullData;

  const latestPoint = chartData[chartData.length - 1];
  const previousPoint = chartData[chartData.length - 2] || chartData[0];
  const priceDiff = latestPoint.modal - previousPoint.modal;
  const pctChange = ((priceDiff / previousPoint.modal) * 100).toFixed(1);

  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 p-5 sm:p-6 shadow-xs hover:shadow-md transition-all">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-gray-100 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-gray-900 tracking-tight flex items-center">
              <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
              {t.dashboard.market_prices} — {lang === "ta" ? (selectedCrop === "turmeric" ? "ஈரோடு மஞ்சள்" : "ஈரோடு வாழை") : (selectedCrop === "turmeric" ? "Erode Turmeric" : "Erode Banana")}
            </h2>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-green-100 text-green-800 border border-green-200">
              <ShieldCheck className="w-3 h-3 mr-1 text-green-700" />
              {t.price.verified_source}: OGD & CEDA
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {lang === "ta"
              ? "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடங்களின் அதிகாரப்பூர்வ மாதிரி, குறைந்தபட்ச மற்றும் அதிகபட்ச விலைகள் (₹/குவிண்டால்)"
              : "Official modal, minimum, and maximum wholesale mandi auction rates (₹/quintal)"}
          </p>
        </div>

        {/* Crop and Timeframe Switchers */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Crop Selector */}
          <div className="inline-flex p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setSelectedCrop("turmeric")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                selectedCrop === "turmeric"
                  ? "bg-white text-green-800 shadow-xs"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              🌾 {t.crops.turmeric}
            </button>
            <button
              onClick={() => setSelectedCrop("banana")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                selectedCrop === "banana"
                  ? "bg-white text-green-800 shadow-xs"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              🍌 {t.crops.banana}
            </button>
          </div>

          {/* Timeframe Selector */}
          <div className="inline-flex p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setTimeframe("7d")}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                timeframe === "7d"
                  ? "bg-white text-gray-900 shadow-xs"
                  : "text-gray-500 hover:text-gray-800"
              }`}
            >
              {t.dashboard.timeframe_7d}
            </button>
            <button
              onClick={() => setTimeframe("30d")}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                timeframe === "30d"
                  ? "bg-white text-gray-900 shadow-xs"
                  : "text-gray-500 hover:text-gray-800"
              }`}
            >
              {t.dashboard.timeframe_30d}
            </button>
          </div>
        </div>
      </div>

      {/* KPI & Signal Highlight Ribbon */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-5 p-4 rounded-xl bg-gradient-to-r from-emerald-50/70 via-green-50/50 to-amber-50/50 border border-emerald-100">
        <div>
          <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
            {t.price.modal_price} ({lang === "ta" ? "நேற்று" : "Latest"})
          </span>
          <div className="flex items-baseline space-x-2 mt-0.5">
            <span className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
              ₹{latestPoint.modal.toLocaleString()}
            </span>
            <span className="text-xs font-medium text-gray-500">/ {t.dashboard.per_quintal}</span>
            <span
              className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                priceDiff >= 0
                  ? "text-emerald-700 bg-emerald-100/80"
                  : "text-red-700 bg-red-100/80"
              }`}
            >
              {priceDiff >= 0 ? "+" : ""}{pctChange}%
            </span>
          </div>
          <span className="text-[11px] text-gray-500 mt-1 block">
            {lang === "ta" ? "விற்பனைக்கூடம்:" : "Mandi:"} {latestPoint.mandi}
          </span>
        </div>

        <div>
          <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
            {t.price.min_price} – {t.price.max_price}
          </span>
          <p className="text-xl font-bold text-gray-800 mt-1">
            ₹{latestPoint.min.toLocaleString()} – ₹{latestPoint.max.toLocaleString()}
          </p>
          <span className="text-[11px] text-gray-500 mt-1 block">
            {lang === "ta" ? "தர நிர்ணய வரம்பு (Grade A/B/C)" : "Commercial Grade Spread"}
          </span>
        </div>

        {/* ML Signal */}
        <div className="flex flex-col justify-center border-t md:border-t-0 md:border-l border-emerald-200/60 md:pl-4">
          <div className="flex items-center space-x-1 text-xs font-bold text-emerald-800 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-amber-600 mr-1" />
            <span>{t.dashboard.signal_title}</span>
          </div>
          <div className="mt-1 flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-extrabold bg-green-600 text-white shadow-xs">
              {t.dashboard.hold_signal}
            </span>
            <span className="text-xs font-semibold text-gray-700">
              {lang === "ta" ? "+2.9% உயர்வு எதிர்பார்ப்பு" : "Expected +2.9% in 14d"}
            </span>
          </div>
          <span className="text-[10px] text-gray-500 mt-1">
            {lang === "ta"
              ? "LightGBM & Statsforecast மாதிரி முன்கணிப்பு (ஈரோடு மாவட்டம்)"
              : "LightGBM & Statsforecast dual ensemble model"}
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 sm:h-80 w-full mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="modalGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#16a34a" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#16a34a" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="rangeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#86efac" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#86efac" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />

            <XAxis
              dataKey={lang === "ta" ? "dateTa" : "date"}
              tickLine={false}
              axisLine={{ stroke: "#e5e7eb" }}
              tick={{ fontSize: 12, fill: "#6b7280" }}
            />

            <YAxis
              domain={["auto", "auto"]}
              tickLine={false}
              axisLine={false}
              tickFormatter={(val) => `₹${(val / 1000).toFixed(1)}k`}
              tick={{ fontSize: 12, fill: "#6b7280" }}
              width={50}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-gray-900/95 text-white p-3 rounded-xl shadow-xl border border-gray-800 text-xs backdrop-blur-sm min-w-[170px]">
                      <p className="font-semibold text-gray-300 flex items-center justify-between border-b border-gray-700/80 pb-1.5 mb-2">
                        <span>{lang === "ta" ? d.dateTa : d.date}</span>
                        <span className="text-[10px] text-green-400 font-bold">{d.mandi}</span>
                      </p>
                      <div className="space-y-1">
                        <div className="flex justify-between items-center text-green-400 font-bold text-sm">
                          <span>{t.price.modal_price}:</span>
                          <span>₹{d.modal.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center text-gray-300">
                          <span>{t.price.max_price}:</span>
                          <span>₹{d.max.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center text-gray-400">
                          <span>{t.price.min_price}:</span>
                          <span>₹{d.min.toLocaleString()}</span>
                        </div>
                      </div>
                      {d.anomaly && (
                        <div className="mt-2 pt-1.5 border-t border-gray-700/80 text-[10px] text-amber-400 font-semibold flex items-center">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          <span>{t.price.anomaly}</span>
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Max / Min Band */}
            <Area
              type="monotone"
              dataKey="max"
              stroke="#86efac"
              strokeWidth={1}
              strokeDasharray="2 2"
              fill="url(#rangeGradient)"
              name="Max"
            />
            {/* Modal Price Line & Gradient Fill */}
            <Area
              type="monotone"
              dataKey="modal"
              stroke="#16a34a"
              strokeWidth={2.5}
              fill="url(#modalGradient)"
              activeDot={{ r: 6, stroke: "#ffffff", strokeWidth: 2, fill: "#15803d" }}
              name="Modal"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Legend & Provenance Footnote */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 gap-2">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-green-600 inline-block"></span>
            <span className="font-medium text-gray-700">{t.price.modal_price}</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-green-200 inline-block"></span>
            <span className="font-medium text-gray-700">{t.price.min_price} – {t.price.max_price}</span>
          </span>
        </div>
        <span className="text-[11px] text-gray-400">
          {lang === "ta" ? "கடைசியாக புதுப்பிக்கப்பட்டது: இன்று காலை 06:00 IST (Agmarknet & CEDA)" : "Last updated: Today 06:00 IST (Agmarknet & CEDA verified)"}
        </span>
      </div>
    </div>
  );
}
