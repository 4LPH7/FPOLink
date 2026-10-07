"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useLanguage } from "@/lib/i18n/context";
import { useDistrict } from "@/lib/district-context";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  BarChart2,
  Inbox,
  Sparkles,
  ArrowRightLeft,
  Navigation,
  ShieldCheck,
  MapPin,
  Truck,
  SlidersHorizontal,
  AlertCircle,
  CheckCircle2,
  Search,
} from "lucide-react";
import {
  getLatestPrices,
  getCrops,
  getPriceHistory,
  getForecast,
  getArbitrage,
  MarketPrice,
  Crop,
  PriceHistoryPoint,
  ForecastResponse,
  ArbitrageResponse,
} from "@/lib/api";
import dynamic from "next/dynamic";

const ForecastAreaChart = dynamic(() => import("@/components/ForecastAreaChart"), {
  ssr: false,
  loading: () => (
    <div className="h-72 w-full flex items-center justify-center text-muted-foreground animate-pulse border rounded-lg bg-card/40">
      <span className="text-xs">Loading chart visualization...</span>
    </div>
  ),
});

const PriceHistoryChart = dynamic(() => import("@/components/PriceHistoryChart"), {
  ssr: false,
  loading: () => (
    <div className="h-64 w-full flex items-center justify-center text-muted-foreground animate-pulse border rounded-lg bg-card/40">
      <span className="text-xs">Loading chart visualization...</span>
    </div>
  ),
});

function resolveCropUnit(unit?: string | null, rawUnit?: string | null, lang?: "ta" | "en") {
  const u = (unit || rawUnit || "").toLowerCase();
  if (u === "kg" || u.includes("kilo") || u.includes("கிலோ")) {
    return { label: lang === "ta" ? "/ கிலோ" : "/ kg", shortLabel: "/kg", multiplier: 1 };
  }
  if (u === "tonne" || u.includes("டன்")) {
    return { label: lang === "ta" ? "/ டன்" : "/ tonne", shortLabel: "/t", multiplier: 1000 };
  }
  return { label: lang === "ta" ? "/ குவிண்டால்" : "/ quintal", shortLabel: "/qtl", multiplier: 100 };
}

export default function PricesPage() {
  const { lang } = useLanguage();
  const { selectedDistrict, setSelectedDistrict, districts } = useDistrict();
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<string>("all");
  const [cropSearch, setCropSearch] = useState<string>("");
  const [activeChartCrop, setActiveChartCrop] = useState<string>("");
  const [chartHistory, setChartHistory] = useState<PriceHistoryPoint[]>([]);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [arbitrageData, setArbitrageData] = useState<ArbitrageResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"rates" | "forecast" | "arbitrage">("rates");
  const [vehicleProfile, setVehicleProfile] = useState<string>("lcv");
  const [handlingFee, setHandlingFee] = useState<number>(15);
  const [commissionPct, setCommissionPct] = useState<number>(1.5);
  const [spoilagePct, setSpoilagePct] = useState<number>(0);
  const [showCostSettings, setShowCostSettings] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastPricesCheck, setLastPricesCheck] = useState<Date | null>(null);

  const loadData = async (district = selectedDistrict) => {
    setIsRefreshing(true);
    try {
      const [pricesData, cropsData] = await Promise.all([
        getLatestPrices(district),
        getCrops(),
      ]);
      setPrices(pricesData);
      setCrops(cropsData);
      setLastPricesCheck(new Date());

      // Resolve effective chart crop dynamically
      const candidateCrop =
        activeChartCrop ||
        pricesData[0]?.crop_name ||
        cropsData[0]?.name ||
        "Paddy";

      if (!activeChartCrop) {
        setActiveChartCrop(candidateCrop);
      }

      await loadIntelligenceData(candidateCrop, cropsData, pricesData, district);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const loadIntelligenceData = async (
    targetCropName: string,
    currentCrops = crops,
    currentPrices = prices,
    district = selectedDistrict
  ) => {
    const cropObj = currentCrops.find(
      (c) => c.name.toLowerCase() === targetCropName.toLowerCase()
    );
    if (!cropObj) return;

    const priceRecord = currentPrices.find(
      (p) => p.crop_name.toLowerCase() === targetCropName.toLowerCase()
    );
    const marketId = priceRecord ? priceRecord.market_id || priceRecord.id : null;

    // 1. Fetch History
    if (marketId) {
      const history = await getPriceHistory(cropObj.id, marketId, 30);
      setChartHistory(history);
    }

    // 2. Fetch AI Forecast & Arbitrage if marketId is available
    if (marketId) {
      const [fc, arb] = await Promise.all([
        getForecast(cropObj.id, marketId, 7),
        getArbitrage(
          cropObj.id,
          marketId,
          300,
          vehicleProfile,
          handlingFee,
          commissionPct,
          spoilagePct
        ),
      ]);
      setForecastData(fc);
      setArbitrageData(arb);
    } else {
      setForecastData(null);
      setArbitrageData(null);
    }
  };

  const handleArbitrageParamChange = async (
    newProfile = vehicleProfile,
    newHandling = handlingFee,
    newCommission = commissionPct,
    newSpoilage = spoilagePct
  ) => {
    setVehicleProfile(newProfile);
    setHandlingFee(newHandling);
    setCommissionPct(newCommission);
    setSpoilagePct(newSpoilage);

    const cropObj = crops.find(
      (c) => c.name.toLowerCase() === activeChartCrop.toLowerCase()
    );
    if (!cropObj) return;

    const priceRecord = prices.find(
      (p) => p.crop_name.toLowerCase() === activeChartCrop.toLowerCase()
    );
    const marketId = priceRecord ? priceRecord.market_id || priceRecord.id : null;
    if (marketId) {
      const arb = await getArbitrage(
        cropObj.id,
        marketId,
        300,
        newProfile,
        newHandling,
        newCommission,
        newSpoilage
      );
      setArbitrageData(arb);
    }
  };

  useEffect(() => {
    loadData(selectedDistrict);
  }, [selectedDistrict]);

  useEffect(() => {
    let active = true;
    let inFlight = false;

    const refreshPrices = async () => {
      if (!active || inFlight || document.visibilityState !== "visible") return;
      inFlight = true;
      try {
        const latest = await getLatestPrices(selectedDistrict);
        if (active) {
          setPrices(latest);
          setLastPricesCheck(new Date());
        }
      } finally {
        inFlight = false;
      }
    };

    const interval = window.setInterval(() => void refreshPrices(), 60_000);
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") void refreshPrices();
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [selectedDistrict]);

  const handleChartCropChange = async (cropName: string) => {
    setActiveChartCrop(cropName);
    await loadIntelligenceData(cropName);
  };

  const filteredPrices = useMemo(() => {
    let list = prices;
    if (selectedCrop !== "all") {
      list = list.filter((p) => p.crop_name.toLowerCase() === selectedCrop.toLowerCase());
    }
    if (cropSearch.trim()) {
      const q = cropSearch.toLowerCase().trim();
      list = list.filter(
        (p) =>
          p.crop_name.toLowerCase().includes(q) ||
          (p.crop_tamil_name && p.crop_tamil_name.toLowerCase().includes(q)) ||
          p.market_name.toLowerCase().includes(q) ||
          p.district.toLowerCase().includes(q)
      );
    }
    return list;
  }, [prices, selectedCrop, cropSearch]);

  // Dynamically extract real top market cards based on active crop and distinct commodities
  const top1 =
    (activeChartCrop ? prices.find((p) => p.crop_name.toLowerCase() === activeChartCrop.toLowerCase()) : null) ||
    prices[0];
  const top2 =
    prices.find((p) => p.crop_name.toLowerCase() !== top1?.crop_name.toLowerCase()) ||
    prices[1];

  const unitInfo1 = resolveCropUnit(top1?.unit, top1?.raw_unit, lang);
  const unitInfo2 = resolveCropUnit(top2?.unit, top2?.raw_unit, lang);
  const unit1 = unitInfo1.label;
  const mult1 = unitInfo1.multiplier;
  const unit2 = unitInfo2.label;
  const mult2 = unitInfo2.multiplier;

  // Transform real history into chart points (in ₹/quintal)
  const chartData = chartHistory.map((pt) => ({
    date: pt.date ? pt.date.slice(5) : "",
    modal: Math.round(Number(pt.modal_price) * 100),
    min: Math.round(Number(pt.min_price) * 100),
    max: Math.round(Number(pt.max_price) * 100),
  }));

  // Transform forecast points for shaded envelope chart
  const forecastChartData = forecastData?.forecast.map((pt) => ({
    date: pt.target_date.slice(5),
    predicted: pt.predicted_price,
    lower: pt.lower_bound,
    upper: pt.upper_bound,
    spread: Math.round(pt.upper_bound - pt.lower_bound),
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header Info with Statewide District Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "மண்டி விலைகள் & விவசாய நுண்ணறிவு" : "Market Prices & Agricultural Intelligence"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "38 மாவட்ட மண்டி விலைகள், 7 நாள் AI முன்கணிப்பு மற்றும் மாவட்டங்களுக்கிடையேயான விலை வேறுபாடுகள்."
              : "Statewide mandi feeds across 38 districts, LightGBM 7-day AI forecasts, and transport-adjusted arbitrage."}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {/* Statewide District Dropdown */}
          <div className="flex items-center space-x-1.5 bg-card border rounded-md px-2.5 py-1">
            <MapPin className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-xs font-medium text-muted-foreground">
              {lang === "ta" ? "மாவட்டம்:" : "District:"}
            </span>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="bg-transparent text-xs font-semibold text-foreground focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-background text-foreground">
                {lang === "ta" ? "அனைத்து மாவட்டங்களும் (மாநிலம் முழுவதும்)" : "All Districts (Statewide)"}
              </option>
              {districts.map((d) => (
                <option key={d.id} value={d.name} className="bg-background text-foreground">
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          <Badge variant="outline" className="max-w-[220px] truncate text-xs">
            {prices[0]
              ? `${prices[0].source} · ${prices[0].price_date}`
              : (lang === "ta" ? "சந்தைத் தரவு இல்லை" : "No market records")}
          </Badge>
          <span className="text-[11px] text-muted-foreground" aria-live="polite">
            {lastPricesCheck
              ? `${lang === "ta" ? "சரிபார்த்த நேரம்" : "Checked"} ${lastPricesCheck.toLocaleTimeString(lang === "ta" ? "ta-IN" : "en-IN", { hour: "2-digit", minute: "2-digit" })} · 1 min`
              : (lang === "ta" ? "ஒவ்வொரு நிமிடமும் புதுப்பிக்கிறது" : "Auto-checks every minute")}
          </span>
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={() => loadData(selectedDistrict)}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isRefreshing ? "animate-spin" : ""}`} />
            <span className="text-xs">{lang === "ta" ? "புதுப்பி" : "Refresh"}</span>
          </Button>
        </div>
      </div>

      {/* Top Cards for Dynamic Anchor Commodities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Commodity Card 1 */}
        <Card className="border-l-4 border-l-amber-500 bg-card/60 shadow-sm">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-800 dark:text-amber-400">
                {top1
                  ? (lang === "ta" ? `${top1.crop_tamil_name || top1.crop_name} · மாதிரி விலை` : `${top1.crop_name} · Modal Rate`)
                  : (lang === "ta" ? "முதன்மை பயிர் · மாதிரி விலை" : "Primary Commodity · Modal Rate")}
              </span>
              {top1?.trend && (
                <Badge
                  variant={top1.trend.direction === "up" ? "success" : top1.trend.direction === "down" ? "destructive" : "outline"}
                  className="text-xs px-1.5 py-0"
                >
                  {top1.trend.direction === "up" && <TrendingUp className="w-3 h-3 mr-1" />}
                  {top1.trend.direction === "down" && <TrendingDown className="w-3 h-3 mr-1" />}
                  {top1.trend.direction === "stable" && <Minus className="w-3 h-3 mr-1" />}
                  {top1.trend.percent > 0 ? `+${top1.trend.percent.toFixed(1)}%` : `${top1.trend.percent.toFixed(1)}%`}
                </Badge>
              )}
            </div>
            <CardTitle className="text-2xl font-bold font-mono mt-1">
              {top1 ? `₹${Math.round(top1.modal_price * mult1).toLocaleString()}` : "—"}
              <span className="text-xs font-normal text-muted-foreground ml-1.5">
                {unit1}
              </span>
            </CardTitle>
            <CardDescription className="text-xs flex items-center justify-between mt-1">
              <span>{top1 ? `${top1.market_name}${top1.district ? ` (${top1.district})` : ""}` : (selectedDistrict === "all" ? "Tamil Nadu Mandi" : `${selectedDistrict} Mandi`)}</span>
              <span className="font-mono text-[11px]">{top1 ? top1.price_date : "Latest verified"}</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2 border-t text-xs text-muted-foreground flex justify-between">
            <span>
              {lang === "ta" ? "குறைந்தபட்சம்: " : "Min: "}
              <strong className="text-foreground font-mono">
                {top1 ? `₹${Math.round(top1.min_price * mult1).toLocaleString()}` : "—"}
              </strong>
            </span>
            <span>
              {lang === "ta" ? "அதிகபட்சம்: " : "Max: "}
              <strong className="text-foreground font-mono">
                {top1 ? `₹${Math.round(top1.max_price * mult1).toLocaleString()}` : "—"}
              </strong>
            </span>
          </CardContent>
        </Card>

        {/* Top Commodity Card 2 */}
        <Card className="border-l-4 border-l-emerald-500 bg-card/60 shadow-sm">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-800 dark:text-emerald-400">
                {top2
                  ? (lang === "ta" ? `${top2.crop_tamil_name || top2.crop_name} · மாதிரி விலை` : `${top2.crop_name} · Modal Rate`)
                  : (lang === "ta" ? "இரண்டாம் பயிர் · மாதிரி விலை" : "Secondary Commodity · Modal Rate")}
              </span>
              {top2?.trend && (
                <Badge
                  variant={top2.trend.direction === "up" ? "success" : top2.trend.direction === "down" ? "destructive" : "outline"}
                  className="text-xs px-1.5 py-0"
                >
                  {top2.trend.direction === "up" && <TrendingUp className="w-3 h-3 mr-1" />}
                  {top2.trend.direction === "down" && <TrendingDown className="w-3 h-3 mr-1" />}
                  {top2.trend.direction === "stable" && <Minus className="w-3 h-3 mr-1" />}
                  {top2.trend.percent > 0 ? `+${top2.trend.percent.toFixed(1)}%` : `${top2.trend.percent.toFixed(1)}%`}
                </Badge>
              )}
            </div>
            <CardTitle className="text-2xl font-bold font-mono mt-1">
              {top2 ? `₹${Math.round(top2.modal_price * mult2).toLocaleString()}` : "—"}
              <span className="text-xs font-normal text-muted-foreground ml-1.5">
                {unit2}
              </span>
            </CardTitle>
            <CardDescription className="text-xs flex items-center justify-between mt-1">
              <span>{top2 ? `${top2.market_name}${top2.district ? ` (${top2.district})` : ""}` : (selectedDistrict === "all" ? "Tamil Nadu Mandi" : `${selectedDistrict} Mandi`)}</span>
              <span className="font-mono text-[11px]">{top2 ? top2.price_date : "Latest verified"}</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2 border-t text-xs text-muted-foreground flex justify-between">
            <span>
              {lang === "ta" ? "குறைந்தபட்சம்: " : "Min: "}
              <strong className="text-foreground font-mono">
                {top2 ? `₹${Math.round(top2.min_price * mult2).toLocaleString()}` : "—"}
              </strong>
            </span>
            <span>
              {lang === "ta" ? "அதிகபட்சம்: " : "Max: "}
              <strong className="text-foreground font-mono">
                {top2 ? `₹${Math.round(top2.max_price * mult2).toLocaleString()}` : "—"}
              </strong>
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex flex-wrap gap-x-6 border-b border-border text-sm font-medium">
        <button
          onClick={() => setActiveTab("rates")}
          className={`pb-3 flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === "rates"
              ? "border-emerald-600 text-emerald-600 font-bold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>{lang === "ta" ? "சமீபத்திய மண்டி விலைகள்" : "Latest mandi records"}</span>
        </button>

        <button
          onClick={() => setActiveTab("forecast")}
          className={`pb-3 flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === "forecast"
              ? "border-emerald-600 text-emerald-600 font-bold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>{lang === "ta" ? "7 நாள் AI முன்கணிப்பு" : "7-Day AI Price Forecast"}</span>
          <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            LightGBM
          </Badge>
        </button>

        <button
          onClick={() => setActiveTab("arbitrage")}
          className={`pb-3 flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === "arbitrage"
              ? "border-emerald-600 text-emerald-600 font-bold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ArrowRightLeft className="w-4 h-4" />
          <span>{lang === "ta" ? "மாவட்டங்களுக்கிடையேயான விலை வேறுபாடு" : "Inter-District Arbitrage"}</span>
        </button>
      </div>

      {/* TAB 1: Latest rates & historical chart */}
      {activeTab === "rates" && (
        <>
          <Card>
            <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <CardTitle className="text-base">
                  {lang === "ta" ? "கடந்த 30 நாட்களின் விலை நகர்வு" : "30-Day Historical Trend"}
                </CardTitle>
                <CardDescription>
                  {lang === "ta"
                    ? "மாதிரி விலையின் தினசரி மாற்றங்கள் (₹/குவிண்டால்)"
                    : "Daily modal settlement price trends from verified government market reports"}
                </CardDescription>
              </div>
              <div className="flex flex-wrap items-center gap-1.5">
                {crops.slice(0, 5).map((c) => (
                  <Button
                    key={c.id}
                    size="sm"
                    variant={activeChartCrop.toLowerCase() === c.name.toLowerCase() ? "default" : "outline"}
                    className="h-7 text-xs"
                    onClick={() => handleChartCropChange(c.name)}
                  >
                    {lang === "ta" ? c.tamil_name || c.name : c.name}
                  </Button>
                ))}
                {crops.length > 5 && (
                  <select
                    value={activeChartCrop}
                    onChange={(e) => handleChartCropChange(e.target.value)}
                    className="h-7 px-2 text-xs rounded-md border border-input bg-card font-medium text-foreground cursor-pointer focus:outline-none"
                    aria-label={lang === "ta" ? "கூடுதல் பயிர்கள்" : "More crops"}
                  >
                    <option value="" disabled>{lang === "ta" ? "அனைத்து 20 பயிர்கள்..." : "All 20 crops..."}</option>
                    {crops.map((c) => (
                      <option key={c.id} value={c.name}>
                        {lang === "ta" && c.tamil_name ? `${c.tamil_name} (${c.name})` : c.name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {chartData.length === 0 ? (
                <div className="h-64 flex items-center justify-center text-muted-foreground text-sm">
                  {lang === "ta" ? "இந்த சந்தைக்கு வரலாற்று விலைத் தரவு இல்லை." : "No historical prices available for this crop and market."}
                </div>
              ) : (
                <PriceHistoryChart
                  data={chartData}
                  strokeColor={
                    activeChartCrop.toLowerCase().includes("turmeric") || activeChartCrop.toLowerCase().includes("chilli")
                      ? "#d97706"
                      : activeChartCrop.toLowerCase().includes("banana") || activeChartCrop.toLowerCase().includes("mango")
                      ? "#eab308"
                      : activeChartCrop.toLowerCase().includes("tomato") || activeChartCrop.toLowerCase().includes("onion")
                      ? "#ef4444"
                      : "#16a34a"
                  }
                />
              )}
            </CardContent>
          </Card>

          {/* Mandi Price Table */}
          <Card>
            <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <CardTitle className="text-lg">
                  {selectedDistrict === "all"
                    ? (lang === "ta" ? "தமிழ்நாடு மாநில மண்டி விலைகள் பட்டியல்" : "Tamil Nadu Statewide Mandi Price Feed")
                    : (lang === "ta" ? `${selectedDistrict} மாவட்ட மண்டி விலைகள் பட்டியல்` : `${selectedDistrict} District Mandi Price Feed`)}
                </CardTitle>
                <CardDescription>
                  {lang === "ta"
                    ? "சமீபத்திய விலைப் பதிவுகள் மற்றும் விலை விவரங்கள்."
                    : "Latest available market records and price details."}
                </CardDescription>
              </div>
              {/* Crop Filter Controls */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    value={cropSearch}
                    onChange={(e) => setCropSearch(e.target.value)}
                    placeholder={lang === "ta" ? "பயிர் / மண்டி தேடுக..." : "Search crop or mandi..."}
                    className="h-8 pl-8 pr-2.5 text-xs rounded-md border border-input bg-background focus:outline-none focus:ring-1 focus:ring-primary w-36 sm:w-48 font-sans"
                  />
                </div>
                <select
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  className="h-8 px-2 text-xs rounded-md border border-input bg-card font-medium text-foreground cursor-pointer focus:outline-none"
                  aria-label={lang === "ta" ? "பயிர் வடிகட்டி" : "Filter crop"}
                >
                  <option value="all">{lang === "ta" ? "அனைத்துப் பயிர்களும் (Statewide)" : "All Crops (Statewide)"}</option>
                  {crops.map((c) => (
                    <option key={c.id} value={c.name}>
                      {lang === "ta" && c.tamil_name ? `${c.tamil_name} (${c.name})` : c.name}
                    </option>
                  ))}
                </select>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-12 text-muted-foreground">
                  <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                  <span>{lang === "ta" ? "ஏற்றுகிறது..." : "Loading live prices..."}</span>
                </div>
              ) : filteredPrices.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                  <Inbox className="w-10 h-10 mb-2 opacity-40" />
                  <p className="font-medium text-sm">
                    {lang === "ta" ? "விலைத் தகவல்கள் இல்லை" : "No price observations available"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {lang === "ta" ? "தேர்ந்தெடுக்கப்பட்ட மாவட்டத்திற்கு விலை எதுவும் பதிவாகவில்லை." : "No records match the current filter selection."}
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{lang === "ta" ? "பயிர் & வகை" : "Crop & Variety"}</TableHead>
                      <TableHead>{lang === "ta" ? "சந்தை / மண்டி" : "Mandi Market"}</TableHead>
                      <TableHead>{lang === "ta" ? "குறைந்த விலை" : "Min Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "அதிக விலை" : "Max Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "மாதிரி விலை" : "Modal Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "போக்கு" : "Trend"}</TableHead>
                      <TableHead className="text-right">{lang === "ta" ? "நம்பகத்தன்மை & ஆதாரம்" : "Provenance & Trust"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredPrices.map((row) => {
                      const unitInfo = resolveCropUnit(row.unit, row.raw_unit, lang);
                      const unitLabel = unitInfo.shortLabel;
                      const multiplier = unitInfo.multiplier;

                      return (
                        <TableRow key={row.id} className="content-visibility-auto">
                          <TableCell className="font-medium">
                            <div>
                              <span className="font-semibold text-foreground">
                                {lang === "ta" ? row.crop_tamil_name || row.crop_name : row.crop_name}
                              </span>
                              <span className="block text-xs text-muted-foreground capitalize">
                                {row.crop_name}
                                {row.variety_name && (
                                  <span className="ml-1 text-[11px] font-mono text-emerald-700 dark:text-emerald-400">
                                    • {row.variety_name}
                                  </span>
                                )}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <span className="text-xs font-semibold">{row.market_name}</span>
                            <span className="block text-[11px] text-muted-foreground">{row.district}</span>
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            ₹{Math.round(row.min_price * multiplier).toLocaleString()}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            ₹{Math.round(row.max_price * multiplier).toLocaleString()}
                          </TableCell>
                          <TableCell className="font-mono text-xs font-bold text-foreground">
                            ₹{Math.round(row.modal_price * multiplier).toLocaleString()}{" "}
                            <span className="text-[10px] text-muted-foreground">{unitLabel}</span>
                          </TableCell>
                          <TableCell>
                            {row.trend ? (
                              <div className="flex items-center space-x-1">
                                {row.trend.direction === "up" && (
                                  <Badge variant="success" className="h-5 px-1 text-[10px]">
                                    <TrendingUp className="w-2.5 h-2.5 mr-0.5" />
                                    +{row.trend.percent.toFixed(1)}%
                                  </Badge>
                                )}
                                {row.trend.direction === "down" && (
                                  <Badge variant="destructive" className="h-5 px-1 text-[10px]">
                                    <TrendingDown className="w-2.5 h-2.5 mr-0.5" />
                                    -{row.trend.percent.toFixed(1)}%
                                  </Badge>
                                )}
                                {row.trend.direction === "stable" && (
                                  <Badge variant="outline" className="h-5 px-1 text-[10px]">
                                    <Minus className="w-2.5 h-2.5 mr-0.5" />
                                    0.0%
                                  </Badge>
                                )}
                              </div>
                            ) : (
                              <span className="text-xs text-muted-foreground">—</span>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex flex-col items-end gap-1">
                              <div className="flex items-center gap-1.5">
                                <span className="text-xs font-mono font-medium">{row.price_date}</span>
                                <Badge variant="outline" className="text-[9px] uppercase px-1 py-0 font-semibold tracking-wider">
                                  {row.source}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-1">
                                {row.source === "demo_seed" || row.freshness_category === "demo" ? (
                                  <Badge variant="destructive" className="text-[9px] px-1 py-0">
                                    {lang === "ta" ? "டெமோ தரவு" : "Demo Seed"}
                                  </Badge>
                                ) : row.is_stale || row.freshness_category === "stale" || row.freshness_category === "outdated" ? (
                                  <Badge variant="outline" className="text-[9px] px-1 py-0 bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300">
                                    {lang === "ta" ? `பழையது (${row.stale_days || 3} நாள்)` : `Stale (${row.stale_days || 3}d ago)`}
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="text-[9px] px-1 py-0 bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300">
                                    {lang === "ta" ? "புதியது" : "Fresh Observation"}
                                  </Badge>
                                )}
                                {typeof row.quality_score === "number" && (
                                  <span className="text-[10px] text-muted-foreground font-mono" title={row.quality_breakdown ? JSON.stringify(row.quality_breakdown) : "QA Score"}>
                                    QA {Math.round(row.quality_score)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* TAB 2: 7-Day AI Price Forecast */}
      {activeTab === "forecast" && (
        <div className="space-y-4">
          {forecastData ? (
            <>
              {/* Recommendation Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="border-l-4 border-l-emerald-600 bg-card/60">
                  <CardHeader className="pb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      {lang === "ta" ? "செயல்படுத்தக்கூடிய பரிந்துரை" : "Actionable Farmer Recommendation"}
                    </span>
                    <div className="flex items-center space-x-2 mt-1">
                      {forecastData.forecast[0]?.signal === "hold" && (
                        <Badge variant="success" className="text-sm px-2.5 py-1">
                          HOLD (விற்பனையை தள்ளிப்போடு)
                        </Badge>
                      )}
                      {forecastData.forecast[0]?.signal === "sell" && (
                        <Badge variant="destructive" className="text-sm px-2.5 py-1">
                          SELL (உடனடி விற்பனை பரிந்துரை)
                        </Badge>
                      )}
                      {forecastData.forecast[0]?.signal === "neutral" && (
                        <Badge variant="outline" className="text-sm px-2.5 py-1 text-amber-600 border-amber-400">
                          NEUTRAL (சீரான சந்தை போக்கு)
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs text-muted-foreground pt-1">
                    {forecastData.forecast[0]?.signal === "hold"
                      ? "அடுத்த 7 நாட்களில் விலை உயரும் என கணிக்கப்பட்டுள்ளது. அவசர விற்பனையை தவிர்க்கலாம்."
                      : forecastData.forecast[0]?.signal === "sell"
                      ? "விலை சரிய வாய்ப்புள்ளதால் தற்போதைய சந்தை விலையில் விற்க பரிந்துரைக்கப்படுகிறது."
                      : "சந்தை விலை வரம்பிற்குள் சீராக உள்ளது. வழமையான விற்பனை செய்யலாம்."}
                  </CardContent>
                </Card>

                <Card className="bg-card/60">
                  <CardHeader className="pb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      {lang === "ta" ? "7-நாள் கணிக்கப்பட்ட மாதிரி விலை" : "7-Day Predicted Modal Price"}
                    </span>
                    <CardTitle className="text-2xl font-bold font-mono mt-1">
                      ₹{forecastData.forecast[forecastData.forecast.length - 1]?.predicted_price.toLocaleString()}
                      <span className="text-xs font-normal text-muted-foreground ml-1">/ qtl</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-xs text-muted-foreground pt-1">
                    நம்பகத்தன்மை வரம்பு:{" "}
                    <strong className="text-foreground font-mono">
                      ₹{forecastData.forecast[forecastData.forecast.length - 1]?.lower_bound.toLocaleString()} — ₹
                      {forecastData.forecast[forecastData.forecast.length - 1]?.upper_bound.toLocaleString()}
                    </strong>
                  </CardContent>
                </Card>

                <Card className="bg-card/60">
                  <CardHeader className="pb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      {lang === "ta" ? "மாதிரி & நம்பகத்தன்மை" : "Model & Confidence Level"}
                    </span>
                    <div className="flex items-center space-x-2 mt-1">
                      <ShieldCheck className="w-5 h-5 text-emerald-600" />
                      <span className="font-bold text-sm">
                        {Math.round((forecastData.forecast[0]?.confidence || 0.85) * 100)}% Confidence
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs text-muted-foreground pt-1">
                    ஆதாரம்: <span className="font-semibold text-foreground">{forecastData.forecast[0]?.model_type}</span>
                  </CardContent>
                </Card>
              </div>

              {/* Shaded Confidence Area Chart */}
              <Card>
                <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <CardTitle className="text-base">
                      {lang === "ta" ? `${forecastData.crop_name} 7-நாள் AI விலை முன்னறிவிப்பு` : `${forecastData.crop_name} 7-Day AI Price Forecast`}
                    </CardTitle>
                    <CardDescription>
                      {lang === "ta"
                        ? "நடுநிலைக் கணிப்பு (p50) மற்றும் 80% நிச்சயமற்ற தன்மை வரம்பு (p10 — p90)"
                        : "Median forecast (p50) with 80% prediction uncertainty band (p10 to p90)"}
                    </CardDescription>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5">
                    {crops.slice(0, 5).map((c) => (
                      <Button
                        key={c.id}
                        size="sm"
                        variant={activeChartCrop.toLowerCase() === c.name.toLowerCase() ? "default" : "outline"}
                        className="h-7 text-xs"
                        onClick={() => handleChartCropChange(c.name)}
                      >
                        {lang === "ta" ? c.tamil_name || c.name : c.name}
                      </Button>
                    ))}
                    {crops.length > 5 && (
                      <select
                        value={activeChartCrop}
                        onChange={(e) => handleChartCropChange(e.target.value)}
                        className="h-7 px-2 text-xs rounded-md border border-input bg-card font-medium text-foreground cursor-pointer focus:outline-none"
                        aria-label={lang === "ta" ? "கூடுதல் பயிர்கள்" : "More crops"}
                      >
                        <option value="" disabled>{lang === "ta" ? "அனைத்து 20 பயிர்கள்..." : "All 20 crops..."}</option>
                        {crops.map((c) => (
                          <option key={c.id} value={c.name}>
                            {lang === "ta" && c.tamil_name ? `${c.tamil_name} (${c.name})` : c.name}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <ForecastAreaChart data={forecastChartData} />
                </CardContent>
              </Card>

              {/* Bilingual Disclaimer */}
              <div className="rounded-lg border border-amber-200/60 bg-amber-50/50 p-3 text-xs dark:border-amber-900/40 dark:bg-amber-950/20">
                <div className="flex items-start gap-2">
                  <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400" />
                  <div className="space-y-0.5">
                    <p className="font-medium text-amber-900 dark:text-amber-200">
                      {forecastData.disclaimer_ta || "இது மதிப்பீடு மட்டுமே, கொள்முதல் அல்லது விற்பனை ஆலோசனை அல்ல."}
                    </p>
                    <p className="text-amber-700/80 dark:text-amber-400/80 text-[11px]">
                      {forecastData.disclaimer_en || "Estimate only, not financial or trading advice."}
                    </p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <Sparkles className="w-10 h-10 mb-2 text-emerald-500 opacity-60" />
                <p className="font-semibold text-sm">
                  {lang === "ta" ? "முன்கணிப்பு உருவாக்கப்படவில்லை" : "No active forecast available for this commodity"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lang === "ta"
                    ? "தேர்ந்தெடுக்கப்பட்ட பயிருக்கு போதுமான விலை பதிவுகள் தேவை."
                    : "Please ensure active mandi price records exist for this crop-market pair."}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* TAB 3: Inter-District Arbitrage */}
      {activeTab === "arbitrage" && (
        <Card>
          <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="text-base">
                {lang === "ta"
                  ? `${selectedDistrict} இலிருந்து பிற மண்டிகளுக்கான விலை வேறுபாடு & போக்குவரத்து லாபம்`
                  : `Inter-District Arbitrage & Freight Net Realization (${selectedDistrict})`}
              </CardTitle>
              <CardDescription>
                {lang === "ta"
                  ? "ஹாவர்சைன் தொலைவு மற்றும் சரக்குக் கட்டணம் கழித்த பின்னரான உண்மையான நிகர லாபம் (₹/குவிண்டால்)."
                  : "Geodesic Haversine distance and freight cost deduction for net realized dispatch margins."}
              </CardDescription>
            </div>
            <div className="flex flex-wrap items-center gap-1.5">
              {crops.slice(0, 5).map((c) => (
                <Button
                  key={c.id}
                  size="sm"
                  variant={activeChartCrop.toLowerCase() === c.name.toLowerCase() ? "default" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => handleChartCropChange(c.name)}
                >
                  {lang === "ta" ? c.tamil_name || c.name : c.name}
                </Button>
              ))}
              {crops.length > 5 && (
                <select
                  value={activeChartCrop}
                  onChange={(e) => handleChartCropChange(e.target.value)}
                  className="h-7 px-2 text-xs rounded-md border border-input bg-card font-medium text-foreground cursor-pointer focus:outline-none"
                  aria-label={lang === "ta" ? "கூடுதல் பயிர்கள்" : "More crops"}
                >
                  <option value="" disabled>{lang === "ta" ? "அனைத்து 20 பயிர்கள்..." : "All 20 crops..."}</option>
                  {crops.map((c) => (
                    <option key={c.id} value={c.name}>
                      {lang === "ta" && c.tamil_name ? `${c.tamil_name} (${c.name})` : c.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </CardHeader>
          {/* Controls Bar: Vehicle Profile & Cost Assumptions */}
          <div className="px-6 pb-2.5 pt-1.5 border-b flex flex-wrap items-center justify-between gap-3 text-xs bg-muted/20">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-muted-foreground flex items-center gap-1">
                <Truck className="w-3.5 h-3.5 text-emerald-600" />
                {lang === "ta" ? "வாகனம்:" : "Vehicle Profile:"}
              </span>
              <div className="inline-flex rounded-md shadow-xs border bg-background p-0.5">
                <button
                  type="button"
                  onClick={() => handleArbitrageParamChange("pickup")}
                  className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                    vehicleProfile === "pickup"
                      ? "bg-emerald-600 text-white shadow-xs"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {lang === "ta" ? "பிக்கப் (1.5T)" : "Pickup (1.5T)"}
                </button>
                <button
                  type="button"
                  onClick={() => handleArbitrageParamChange("lcv")}
                  className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                    vehicleProfile === "lcv"
                      ? "bg-emerald-600 text-white shadow-xs"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {lang === "ta" ? "LCV / 407 (3.5T)" : "LCV 407 (3.5T)"}
                </button>
                <button
                  type="button"
                  onClick={() => handleArbitrageParamChange("medium_truck")}
                  className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                    vehicleProfile === "medium_truck"
                      ? "bg-emerald-600 text-white shadow-xs"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {lang === "ta" ? "லாரி (10T)" : "Medium Truck (10T)"}
                </button>
              </div>
            </div>

            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs flex items-center gap-1.5"
              onClick={() => setShowCostSettings(!showCostSettings)}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{lang === "ta" ? "செலவு வரம்புகள்" : "Cost Assumptions"}</span>
            </Button>
          </div>

          {/* Collapsible Cost Assumptions Panel */}
          {showCostSettings && (
            <div className="px-6 py-3 border-b bg-muted/40 text-xs grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">
                  {lang === "ta" ? "ஏற்று/இறக்கு கட்டணம் (₹/குவிண்டால்):" : "Handling & Bagging (₹/qtl):"}
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={handlingFee}
                  onChange={(e) =>
                    handleArbitrageParamChange(vehicleProfile, Number(e.target.value), commissionPct, spoilagePct)
                  }
                  className="w-full bg-background border rounded px-2.5 py-1 text-foreground font-mono text-xs"
                />
              </div>
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">
                  {lang === "ta" ? "மண்டி கமிஷன் கட்டணம் (%):" : "Mandi Commission Fee (%):"}
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  value={commissionPct}
                  onChange={(e) =>
                    handleArbitrageParamChange(vehicleProfile, handlingFee, Number(e.target.value), spoilagePct)
                  }
                  className="w-full bg-background border rounded px-2.5 py-1 text-foreground font-mono text-xs"
                />
              </div>
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">
                  {lang === "ta" ? "போக்குவரத்து சேதாரம் (%):" : "Transit Spoilage Buffer (%):"}
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="20"
                  value={spoilagePct}
                  onChange={(e) =>
                    handleArbitrageParamChange(vehicleProfile, handlingFee, commissionPct, Number(e.target.value))
                  }
                  className="w-full bg-background border rounded px-2.5 py-1 text-foreground font-mono text-xs"
                />
              </div>
            </div>
          )}

          <CardContent>
            {!arbitrageData || arbitrageData.opportunities.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <ArrowRightLeft className="w-10 h-10 mb-2 opacity-40" />
                <p className="font-medium text-sm">
                  {lang === "ta" ? "விலை வேறுபாட்டு வாய்ப்புகள் எதுவும் இல்லை" : "No active arbitrage opportunities detected"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lang === "ta"
                    ? "அருகிலுள்ள மண்டிகளிலிருந்து சமீபத்திய விலைகள் எதுவும் பதிவாகவில்லை."
                    : "No reporting mandis found within search radius for this commodity."}
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{lang === "ta" ? "இலக்கு மண்டி & தரம்" : "Target Mandi & Variety"}</TableHead>
                    <TableHead>{lang === "ta" ? "தொலைவு" : "Distance"}</TableHead>
                    <TableHead>{lang === "ta" ? "இலக்கு விலை" : "Target Rate"}</TableHead>
                    <TableHead>{lang === "ta" ? "மொத்த வித்தியாசம்" : "Gross Spread"}</TableHead>
                    <TableHead>{lang === "ta" ? "கட்டணங்கள் விவரம்" : "Itemized Deductions"}</TableHead>
                    <TableHead>{lang === "ta" ? "நிகர லாபம்" : "Net Advantage"}</TableHead>
                    <TableHead className="text-right">{lang === "ta" ? "நம்பகத்தன்மை & முடிவு" : "Uncertainty & Decision"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {arbitrageData.opportunities.map((opp) => (
                    <TableRow key={opp.target_market_id}>
                      <TableCell className="font-medium">
                        <div>
                          <span className="font-semibold text-foreground">{opp.target_market_name}</span>
                          <span className="block text-xs text-muted-foreground">{opp.district}</span>
                          <div className="flex items-center gap-1.5 mt-1">
                            {opp.variety_match === "exact" ? (
                              <Badge variant="outline" className="text-[9px] px-1 py-0 bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300">
                                {lang === "ta" ? "சரியான ரகம்" : "Exact Variety"}
                              </Badge>
                            ) : opp.variety_match === "cross_variety_approximate" ? (
                              <Badge variant="outline" className="text-[9px] px-1 py-0 bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300">
                                {lang === "ta" ? "சுத்தமான ரகமல்ல" : "Cross-Variety"}
                              </Badge>
                            ) : null}
                            {opp.variety_name && (
                              <span className="text-[10px] text-muted-foreground font-mono">
                                {opp.variety_name}
                              </span>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{opp.distance_km} km</TableCell>
                      <TableCell className="font-mono text-xs">
                        <div className="font-semibold">₹{opp.target_price.toLocaleString()}</div>
                        <div className="text-[10px] text-muted-foreground font-sans">
                          {opp.date_difference_days === 0
                            ? (lang === "ta" ? "இன்றைய பதிவு" : "Same day")
                            : (lang === "ta" ? `${opp.date_difference_days} நாள் தாமதம்` : `${opp.date_difference_days}d lag`)}
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {opp.gross_spread > 0 ? `+₹${opp.gross_spread.toLocaleString()}` : `₹${opp.gross_spread.toLocaleString()}`}
                      </TableCell>
                      <TableCell className="text-xs">
                        {opp.costs_breakdown ? (
                          <div className="space-y-0.5 font-mono text-[11px]">
                            <div className="text-foreground font-semibold">
                              -₹{opp.costs_breakdown.total_cost.toLocaleString()}{" "}
                              <span className="text-[9px] text-muted-foreground font-sans">/ qtl</span>
                            </div>
                            <div className="text-[10px] text-muted-foreground">
                              சரக்கு: ₹{opp.costs_breakdown.freight} | கையாளுதல்: ₹{opp.costs_breakdown.handling}
                            </div>
                            <div className="text-[10px] text-muted-foreground">
                              கமிஷன்: ₹{opp.costs_breakdown.commission} | சேதாரம்: ₹{opp.costs_breakdown.spoilage_risk}
                            </div>
                          </div>
                        ) : (
                          <span className="font-mono text-muted-foreground">-₹{opp.transport_cost.toLocaleString()}</span>
                        )}
                      </TableCell>
                      <TableCell className="font-mono text-xs font-bold">
                        {opp.net_spread > 0 ? (
                          <span className="text-emerald-600 font-bold">+₹{opp.net_spread.toLocaleString()}</span>
                        ) : (
                          <span className="text-rose-600">₹{opp.net_spread.toLocaleString()}</span>
                        )}
                        <span className="text-[10px] text-muted-foreground block">/ quintal</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex flex-col items-end gap-1">
                          {opp.recommendation === "strong_arbitrage" && (
                            <Badge variant="success" className="text-[10px]">
                              STRONG ARBITRAGE
                            </Badge>
                          )}
                          {opp.recommendation === "profitable_dispatch" && (
                            <Badge variant="outline" className="text-[10px] border-emerald-500 text-emerald-600">
                              PROFITABLE
                            </Badge>
                          )}
                          {opp.recommendation === "local_preferred" && (
                            <Badge variant="outline" className="text-[10px] text-muted-foreground">
                              LOCAL PREFERRED
                            </Badge>
                          )}
                          {/* Uncertainty Rating Badge */}
                          {opp.uncertainty_rating && (
                            <Badge
                              variant="outline"
                              className={`text-[9px] px-1 py-0 ${
                                opp.uncertainty_rating === "low"
                                  ? "border-emerald-300 text-emerald-700 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-300"
                                  : opp.uncertainty_rating === "moderate"
                                  ? "border-amber-300 text-amber-700 bg-amber-50 dark:bg-amber-950 dark:text-amber-300"
                                  : "border-rose-300 text-rose-700 bg-rose-50 dark:bg-rose-950 dark:text-rose-300"
                              }`}
                              title={opp.uncertainty_reasons?.join("; ") || ""}
                            >
                              {opp.uncertainty_rating.toUpperCase()} RISK
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>

          {/* Bilingual Defensibility Disclaimer Notice */}
          <div className="p-4 border-t bg-amber-50/50 dark:bg-amber-950/20 text-xs text-muted-foreground">
            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
              <div className="space-y-1">
                <p className="font-medium text-amber-900 dark:text-amber-200">
                  {arbitrageData?.disclaimer_ta ||
                    "இது மதிப்பிடப்பட்ட சாத்தியக்கூறு மட்டுமே; போக்குவரத்து கட்டணம், தரம் மற்றும் சந்தை கட்டணங்களின் அடிப்படையில் மாறுபடலாம்."}
                </p>
                <p className="text-[11px] text-amber-700/80 dark:text-amber-400/80">
                  {arbitrageData?.disclaimer_en ||
                    "Estimated net opportunities based on reported mandi modal prices. Does not guarantee realized trading profit; actual outcomes depend on vehicle capacity, live arrival volumes, transporter quotes, and quality grading."}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
