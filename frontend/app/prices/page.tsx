"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n/context";
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
} from "lucide-react";
import {
  getLatestPrices,
  getCrops,
  getPriceHistory,
  getDistricts,
  getForecast,
  getArbitrage,
  MarketPrice,
  Crop,
  PriceHistoryPoint,
  DistrictItem,
  ForecastResponse,
  ArbitrageResponse,
} from "@/lib/api";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function PricesPage() {
  const { lang } = useLanguage();
  const [districts, setDistricts] = useState<DistrictItem[]>([]);
  const [selectedDistrict, setSelectedDistrict] = useState<string>("Erode");
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<string>("all");
  const [activeChartCrop, setActiveChartCrop] = useState<string>("turmeric");
  const [chartHistory, setChartHistory] = useState<PriceHistoryPoint[]>([]);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [arbitrageData, setArbitrageData] = useState<ArbitrageResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"rates" | "forecast" | "arbitrage">("rates");
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadData = async (district = selectedDistrict) => {
    setIsRefreshing(true);
    try {
      const [districtsData, pricesData, cropsData] = await Promise.all([
        getDistricts(),
        getLatestPrices(district),
        getCrops(),
      ]);
      setDistricts(districtsData);
      setPrices(pricesData);
      setCrops(cropsData);

      // Load initial history, forecast, and arbitrage
      await loadIntelligenceData(activeChartCrop, cropsData, pricesData, district);
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
        getArbitrage(cropObj.id, marketId, 300),
      ]);
      setForecastData(fc);
      setArbitrageData(arb);
    } else {
      setForecastData(null);
      setArbitrageData(null);
    }
  };

  useEffect(() => {
    loadData(selectedDistrict);
  }, [selectedDistrict]);

  const handleChartCropChange = async (cropName: string) => {
    setActiveChartCrop(cropName);
    await loadIntelligenceData(cropName);
  };

  const filteredPrices =
    selectedCrop === "all"
      ? prices
      : prices.filter((p) => p.crop_name.toLowerCase() === selectedCrop.toLowerCase());

  // Dynamically extract real top market cards
  const turmericTop = prices.find((p) => p.crop_name.toLowerCase().includes("turmeric"));
  const bananaTop = prices.find((p) => p.crop_name.toLowerCase().includes("banana"));

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
              {districts.map((d) => (
                <option key={d.id} value={d.name} className="bg-background text-foreground">
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          <Badge variant="success" className="text-xs">
            {lang === "ta" ? "Agmarknet நேரலை" : "Agmarknet Live"}
          </Badge>
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

      {/* Top Cards for Anchor Commodities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Turmeric Top Card */}
        <Card className="border-l-4 border-l-amber-500 bg-card/60 shadow-sm">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-800 dark:text-amber-400">
                {lang === "ta" ? "மஞ்சள் (விரலி) · மாதிரி விலை" : "Turmeric (Finger) · Modal Rate"}
              </span>
              {turmericTop?.trend && (
                <Badge
                  variant={turmericTop.trend.direction === "up" ? "success" : turmericTop.trend.direction === "down" ? "destructive" : "outline"}
                  className="text-xs px-1.5 py-0"
                >
                  {turmericTop.trend.direction === "up" && <TrendingUp className="w-3 h-3 mr-1" />}
                  {turmericTop.trend.direction === "down" && <TrendingDown className="w-3 h-3 mr-1" />}
                  {turmericTop.trend.direction === "stable" && <Minus className="w-3 h-3 mr-1" />}
                  {turmericTop.trend.percent > 0 ? `+${turmericTop.trend.percent.toFixed(1)}%` : `${turmericTop.trend.percent.toFixed(1)}%`}
                </Badge>
              )}
            </div>
            <CardTitle className="text-2xl font-bold font-mono mt-1">
              {turmericTop ? `₹${Math.round(turmericTop.modal_price * 100).toLocaleString()}` : "—"}
              <span className="text-xs font-normal text-muted-foreground ml-1.5">
                {lang === "ta" ? "/ குவிண்டால்" : "/ quintal"}
              </span>
            </CardTitle>
            <CardDescription className="text-xs flex items-center justify-between mt-1">
              <span>{turmericTop ? turmericTop.market_name : `${selectedDistrict} Regulated Market`}</span>
              <span className="font-mono text-[11px]">{turmericTop ? turmericTop.price_date : "Latest verified"}</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2 border-t text-xs text-muted-foreground flex justify-between">
            <span>
              {lang === "ta" ? "குறைந்தபட்சம்: " : "Min: "}
              <strong className="text-foreground font-mono">
                {turmericTop ? `₹${Math.round(turmericTop.min_price * 100).toLocaleString()}` : "—"}
              </strong>
            </span>
            <span>
              {lang === "ta" ? "அதிகபட்சம்: " : "Max: "}
              <strong className="text-foreground font-mono">
                {turmericTop ? `₹${Math.round(turmericTop.max_price * 100).toLocaleString()}` : "—"}
              </strong>
            </span>
          </CardContent>
        </Card>

        {/* Banana Top Card */}
        <Card className="border-l-4 border-l-emerald-500 bg-card/60 shadow-sm">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-800 dark:text-emerald-400">
                {lang === "ta" ? "வாழை (நேந்திரன் / பூவன்) · மாதிரி விலை" : "Banana (Nendran/Poovan) · Modal Rate"}
              </span>
              {bananaTop?.trend && (
                <Badge
                  variant={bananaTop.trend.direction === "up" ? "success" : bananaTop.trend.direction === "down" ? "destructive" : "outline"}
                  className="text-xs px-1.5 py-0"
                >
                  {bananaTop.trend.direction === "up" && <TrendingUp className="w-3 h-3 mr-1" />}
                  {bananaTop.trend.direction === "down" && <TrendingDown className="w-3 h-3 mr-1" />}
                  {bananaTop.trend.direction === "stable" && <Minus className="w-3 h-3 mr-1" />}
                  {bananaTop.trend.percent > 0 ? `+${bananaTop.trend.percent.toFixed(1)}%` : `${bananaTop.trend.percent.toFixed(1)}%`}
                </Badge>
              )}
            </div>
            <CardTitle className="text-2xl font-bold font-mono mt-1">
              {bananaTop ? `₹${bananaTop.modal_price.toFixed(1)}` : "—"}
              <span className="text-xs font-normal text-muted-foreground ml-1.5">
                {lang === "ta" ? "/ கிலோ" : "/ kg"}
              </span>
            </CardTitle>
            <CardDescription className="text-xs flex items-center justify-between mt-1">
              <span>{bananaTop ? bananaTop.market_name : `${selectedDistrict} Mandi`}</span>
              <span className="font-mono text-[11px]">{bananaTop ? bananaTop.price_date : "Latest verified"}</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2 border-t text-xs text-muted-foreground flex justify-between">
            <span>
              {lang === "ta" ? "குறைந்தபட்சம்: " : "Min: "}
              <strong className="text-foreground font-mono">
                {bananaTop ? `₹${bananaTop.min_price.toFixed(1)}` : "—"}
              </strong>
            </span>
            <span>
              {lang === "ta" ? "அதிகபட்சம்: " : "Max: "}
              <strong className="text-foreground font-mono">
                {bananaTop ? `₹${bananaTop.max_price.toFixed(1)}` : "—"}
              </strong>
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex border-b border-border space-x-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab("rates")}
          className={`pb-3 flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === "rates"
              ? "border-emerald-600 text-emerald-600 font-bold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>{lang === "ta" ? "நேரலை மண்டி விலைகள்" : "Live Mandi Rates"}</span>
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

      {/* TAB 1: Live Rates & Historical Chart */}
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
              <div className="flex items-center space-x-1.5">
                <Button
                  size="sm"
                  variant={activeChartCrop === "turmeric" ? "default" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => handleChartCropChange("turmeric")}
                >
                  {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
                </Button>
                <Button
                  size="sm"
                  variant={activeChartCrop === "banana" ? "default" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => handleChartCropChange("banana")}
                >
                  {lang === "ta" ? "வாழை" : "Banana"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {chartData.length === 0 ? (
                <div className="h-64 flex items-center justify-center text-muted-foreground text-sm">
                  {lang === "ta" ? "வரலாற்று தரவுகள் ஏற்றப்படுகின்றன..." : "Loading historical price trend..."}
                </div>
              ) : (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
                      <Tooltip
                        formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, "Modal Rate"]}
                        labelFormatter={(lbl) => `Date: ${lbl}`}
                        contentStyle={{ backgroundColor: "#1e293b", color: "#fff", borderRadius: "8px", fontSize: "12px" }}
                      />
                      <Line
                        type="monotone"
                        dataKey="modal"
                        stroke={activeChartCrop === "turmeric" ? "#d97706" : "#16a34a"}
                        strokeWidth={2.5}
                        dot={{ r: 3 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Mandi Price Table */}
          <Card>
            <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <CardTitle className="text-lg">
                  {lang === "ta" ? `${selectedDistrict} மாவட்ட மண்டி விலைகள் பட்டியல்` : `${selectedDistrict} District Mandi Price Feed`}
                </CardTitle>
                <CardDescription>
                  {lang === "ta"
                    ? "நேரலை மண்டி விலைகள் மற்றும் மாதிரி விலை விவரங்கள்."
                    : "Live verified price records from official agricultural market committees."}
                </CardDescription>
              </div>
              {/* Crop Filter Buttons */}
              <div className="flex flex-wrap items-center gap-1.5">
                <Button
                  size="sm"
                  variant={selectedCrop === "all" ? "default" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => setSelectedCrop("all")}
                >
                  {lang === "ta" ? "அனைத்தும்" : "All"}
                </Button>
                {crops.slice(0, 8).map((crop) => (
                  <Button
                    key={crop.id}
                    size="sm"
                    variant={selectedCrop === crop.name ? "default" : "outline"}
                    className="h-7 text-xs"
                    onClick={() => setSelectedCrop(crop.name)}
                  >
                    {lang === "ta" ? crop.tamil_name || crop.name : crop.name}
                  </Button>
                ))}
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
                      <TableHead>{lang === "ta" ? "பயிர்" : "Crop"}</TableHead>
                      <TableHead>{lang === "ta" ? "சந்தை / மண்டி" : "Mandi Market"}</TableHead>
                      <TableHead>{lang === "ta" ? "குறைந்த விலை" : "Min Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "அதிக விலை" : "Max Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "மாதிரி விலை" : "Modal Price"}</TableHead>
                      <TableHead>{lang === "ta" ? "போக்கு" : "Trend"}</TableHead>
                      <TableHead className="text-right">{lang === "ta" ? "தேதி & ஆதாரம்" : "Date & Source"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredPrices.map((row) => {
                      const unitLabel = row.crop_name.toLowerCase().includes("banana") || row.crop_name.toLowerCase().includes("coconut")
                        ? "/kg"
                        : "/qtl";
                      const multiplier = unitLabel === "/qtl" ? 100 : 1;

                      return (
                        <TableRow key={row.id}>
                          <TableCell className="font-medium">
                            <div>
                              <span>{lang === "ta" ? row.crop_tamil_name || row.crop_name : row.crop_name}</span>
                              <span className="block text-xs text-muted-foreground capitalize">
                                {row.crop_name}
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
                            <div className="text-xs font-mono">{row.price_date}</div>
                            <Badge variant="outline" className="text-[10px] uppercase">
                              {row.source}
                            </Badge>
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
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant={activeChartCrop === "turmeric" ? "default" : "outline"}
                      className="h-7 text-xs"
                      onClick={() => handleChartCropChange("turmeric")}
                    >
                      {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
                    </Button>
                    <Button
                      size="sm"
                      variant={activeChartCrop === "banana" ? "default" : "outline"}
                      className="h-7 text-xs"
                      onClick={() => handleChartCropChange("banana")}
                    >
                      {lang === "ta" ? "வாழை" : "Banana"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={forecastChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
                        <Tooltip
                          formatter={(val: any, name: string) => [
                            `₹${Number(val).toLocaleString()}`,
                            name === "predicted" ? "Predicted (p50)" : name === "upper" ? "Upper Bound (p90)" : "Lower Bound (p10)",
                          ]}
                          contentStyle={{ backgroundColor: "#1e293b", color: "#fff", borderRadius: "8px", fontSize: "12px" }}
                        />
                        <Area
                          type="monotone"
                          dataKey="upper"
                          stroke="transparent"
                          fill="#10b981"
                          fillOpacity={0.15}
                        />
                        <Area
                          type="monotone"
                          dataKey="lower"
                          stroke="transparent"
                          fill="#ffffff"
                          fillOpacity={1.0}
                        />
                        <Line
                          type="monotone"
                          dataKey="predicted"
                          stroke="#10b981"
                          strokeWidth={3}
                          dot={{ r: 4, fill: "#10b981" }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
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
            <div className="flex items-center space-x-1.5">
              <Button
                size="sm"
                variant={activeChartCrop === "turmeric" ? "default" : "outline"}
                className="h-7 text-xs"
                onClick={() => handleChartCropChange("turmeric")}
              >
                {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
              </Button>
              <Button
                size="sm"
                variant={activeChartCrop === "banana" ? "default" : "outline"}
                className="h-7 text-xs"
                onClick={() => handleChartCropChange("banana")}
              >
                {lang === "ta" ? "வாழை" : "Banana"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {!arbitrageData || arbitrageData.opportunities.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <ArrowRightLeft className="w-10 h-10 mb-2 opacity-40" />
                <p className="font-medium text-sm">
                  {lang === "ta" ? "விலை வேறுபாட்டு வாய்ப்புகள் எதுவும் இல்லை" : "No active arbitrage opportunities detected"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lang === "ta" ? "அருகிலுள்ள மண்டிகளிலிருந்து சமீபத்திய விலைகள் எதுவும் பதிவாகவில்லை." : "No reporting mandis found within search radius for this commodity."}
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{lang === "ta" ? "இலக்கு மண்டி & மாவட்டம்" : "Target Mandi & District"}</TableHead>
                    <TableHead>{lang === "ta" ? "தொலைவு" : "Distance"}</TableHead>
                    <TableHead>{lang === "ta" ? "இலக்கு விலை" : "Target Rate"}</TableHead>
                    <TableHead>{lang === "ta" ? "மொத்த வித்தியாசம்" : "Gross Spread"}</TableHead>
                    <TableHead>{lang === "ta" ? "சரக்குச் செலவு" : "Transport Cost"}</TableHead>
                    <TableHead>{lang === "ta" ? "நிகர லாபம்" : "Net Advantage"}</TableHead>
                    <TableHead className="text-right">{lang === "ta" ? "முடிவு" : "Decision"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {arbitrageData.opportunities.map((opp) => (
                    <TableRow key={opp.target_market_id}>
                      <TableCell className="font-medium">
                        <span>{opp.target_market_name}</span>
                        <span className="block text-xs text-muted-foreground">{opp.district}</span>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{opp.distance_km} km</TableCell>
                      <TableCell className="font-mono text-xs font-semibold">₹{opp.target_price.toLocaleString()}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {opp.gross_spread > 0 ? `+₹${opp.gross_spread.toLocaleString()}` : `₹${opp.gross_spread.toLocaleString()}`}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        -₹{opp.transport_cost.toLocaleString()}
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
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
