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
} from "lucide-react";
import {
  getLatestPrices,
  getCrops,
  getPriceHistory,
  MarketPrice,
  Crop,
  PriceHistoryPoint,
} from "@/lib/api";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function PricesPage() {
  const { lang } = useLanguage();
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<string>("all");
  const [activeChartCrop, setActiveChartCrop] = useState<"turmeric" | "banana">("turmeric");
  const [chartHistory, setChartHistory] = useState<PriceHistoryPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [pricesData, cropsData] = await Promise.all([
        getLatestPrices("Erode"),
        getCrops(),
      ]);
      setPrices(pricesData);
      setCrops(cropsData);

      // Load initial history for active crop
      await loadCropHistory(activeChartCrop, cropsData, pricesData);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const loadCropHistory = async (
    targetCropName: string,
    currentCrops = crops,
    currentPrices = prices
  ) => {
    const cropObj = currentCrops.find(
      (c) => c.name.toLowerCase() === targetCropName.toLowerCase()
    );
    if (!cropObj) return;

    // Find market for this crop from latest prices or first available
    const priceRecord = currentPrices.find(
      (p) => p.crop_name.toLowerCase() === targetCropName.toLowerCase()
    );

    // Call history endpoint
    const history = await getPriceHistory(
      cropObj.id,
      priceRecord ? priceRecord.id : "default",
      30
    );
    setChartHistory(history);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleChartCropChange = async (crop: "turmeric" | "banana") => {
    setActiveChartCrop(crop);
    await loadCropHistory(crop);
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

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "மண்டி விலைகள் & முன்கணிப்பு நுண்ணறிவு" : "Market Prices & Forecast Telemetry"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "ஈரோடு மாவட்ட சந்தை விலைகள், Agmarknet/OGD நேரலை வரத்து, மற்றும் முன்கணிப்பு."
              : "Erode district mandi feeds, verified Agmarknet/OGD live arrivals, and price forecasts."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success">
            {lang === "ta" ? "Agmarknet நேரலை" : "Agmarknet Live"}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={loadData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Featured Price Cards (100% Real Live Database Data) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
              </span>
              <Badge variant="warning">
                {lang === "ta" ? "நேரலை மண்டி விலை" : "LIVE MANDI"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              {turmericTop ? (
                <>
                  ₹{Math.round(turmericTop.modal_price * 100).toLocaleString()}{" "}
                  <span className="text-sm font-normal text-muted-foreground">
                    / {lang === "ta" ? "குவிண்டால்" : "quintal"}
                  </span>
                </>
              ) : (
                <span className="text-muted-foreground text-xl">
                  {lang === "ta" ? "விலை எதிர்பார்க்கப்படுகிறது" : "Awaiting quote"}
                </span>
              )}
            </CardTitle>
            <CardDescription>
              {turmericTop ? (
                `${turmericTop.market_name} • ₹${Math.round(turmericTop.min_price * 100)} - ₹${Math.round(turmericTop.max_price * 100)}`
              ) : (
                lang === "ta" ? "ஈரோடு மண்டி" : "Erode Mandi"
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {turmericTop?.arrival_quantity ? (
              `${lang === "ta" ? "வரத்து" : "Arrivals"}: ${turmericTop.arrival_quantity} quintals (${turmericTop.price_date})`
            ) : (
              lang === "ta" ? "அரசு அங்கீகரிக்கப்பட்ட விலை ஆதாரம்" : "Verified Agmarknet mandi quote"
            )}
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "வாழை" : "Banana"}
              </span>
              <Badge variant="success">
                {lang === "ta" ? "நேரலை மண்டி விலை" : "LIVE MANDI"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              {bananaTop ? (
                <>
                  ₹{Math.round(bananaTop.modal_price).toLocaleString()}{" "}
                  <span className="text-sm font-normal text-muted-foreground">
                    / {lang === "ta" ? "கிலோ" : "kg"}
                  </span>
                </>
              ) : (
                <span className="text-muted-foreground text-xl">
                  {lang === "ta" ? "விலை எதிர்பார்க்கப்படுகிறது" : "Awaiting quote"}
                </span>
              )}
            </CardTitle>
            <CardDescription>
              {bananaTop ? (
                `${bananaTop.market_name} • ₹${Math.round(bananaTop.min_price)} - ₹${Math.round(bananaTop.max_price)}`
              ) : (
                lang === "ta" ? "கோபிசெட்டிபாளையம் மண்டி" : "Gobichettipalayam Mandi"
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {bananaTop?.arrival_quantity ? (
              `${lang === "ta" ? "வரத்து" : "Arrivals"}: ${bananaTop.arrival_quantity} quintals (${bananaTop.price_date})`
            ) : (
              lang === "ta" ? "அரசு அங்கீகரிக்கப்பட்ட விலை ஆதாரம்" : "Verified Agmarknet mandi quote"
            )}
          </CardContent>
        </Card>
      </div>

      {/* 30-Day Trend Chart (Dynamic Live Data) */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-lg">
              {lang === "ta" ? "சந்தை விலை போக்கு வரைபடம்" : "Mandi Price Trend History"}
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "ஈரோடு சந்தைகளில் மாதிரி விலையின் மாறுபாடுகள் (ரூ/குவிண்டால்)"
                : "Daily modal price movements across Erode district mandis (₹/quintal)"}
            </CardDescription>
          </div>
          <div className="flex space-x-1.5">
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
        <CardContent className="pt-4">
          {chartData.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center text-muted-foreground p-4">
              <BarChart2 className="w-10 h-10 mb-2 opacity-40" />
              <p className="font-medium text-sm">
                {lang === "ta" ? "விலை வரலாற்றுத் தரவுகள் இல்லை" : "No price observations found for this crop"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {lang === "ta"
                  ? "தினசரி மண்டி தகவல் பதிவான பிறகு வரைபடம் தோன்றும்."
                  : "Daily mandi feeds from Agmarknet/OGD will populate historical curves automatically."}
              </p>
            </div>
          ) : (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    tickFormatter={(val) => `₹${val}`}
                  />
                  <Tooltip
                    formatter={(val: number) => [`₹${val}`, lang === "ta" ? "மாதிரி விலை" : "Modal Price"]}
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
              {lang === "ta" ? "ஈரோடு மாவட்ட மண்டி விலைகள் பட்டியல்" : "Erode District Mandi Price Feed"}
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "நேரலை மண்டி விலைகள், முரண்பாடு நிலை மற்றும் மாதிரி விலை விவரங்கள்."
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
            {crops.map((crop) => (
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
                {lang === "ta" ? "தேர்ந்தெடுக்கப்பட்ட பயிருக்கு விலை எதுவும் பதிவாகவில்லை." : "No records match the current filter selection."}
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
    </div>
  );
}
