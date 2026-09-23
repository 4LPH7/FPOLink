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
  Filter,
} from "lucide-react";
import { getLatestPrices, getCrops, MarketPrice, Crop } from "@/lib/api";
import { TURMERIC_DATA_30D, BANANA_DATA_30D } from "@/lib/marketData";
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
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredPrices =
    selectedCrop === "all"
      ? prices
      : prices.filter((p) => p.crop_name.toLowerCase() === selectedCrop.toLowerCase());

  const chartData = activeChartCrop === "turmeric" ? TURMERIC_DATA_30D : BANANA_DATA_30D;

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
              ? "ஈரோடு மாவட்ட சந்தை விலைகள், CEDA/OGD நேரலை வரத்து, மற்றும் அடுத்த மாத முன்கணிப்பு."
              : "Erode district mandi feeds, CEDA/OGD live arrivals, and ML price predictions."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success">
            {lang === "ta" ? "OGD/CEDA நேரலை" : "OGD/CEDA Live"}
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

      {/* Featured Price Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "மஞ்சள் (விரலி)" : "Turmeric (Finger)"}
              </span>
              <Badge variant="warning">
                {lang === "ta" ? "வைத்திருத்தல் பரிந்துரை" : "HOLD SIGNAL"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              ₹12,350 <span className="text-sm font-normal text-muted-foreground">/ {lang === "ta" ? "குவிண்டால்" : "quintal"}</span>
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "பெருந்துறை ஒழுங்குமுறை விற்பனைக்கூடம் • நேற்று ₹12,200 (+1.2%)"
                : "Perundurai Regulated Mandi • Prev: ₹12,200 (+1.2%)"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {lang === "ta"
              ? "அடுத்த மாத கணிப்பு: ₹12,800/குவிண்டால் (நம்பகத்தன்மை: 85%)"
              : "Next month forecast: ₹12,800/quintal (Confidence: 85%)"}
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "வாழை (நேந்திரன்)" : "Banana (Nendran)"}
              </span>
              <Badge variant="success">
                {lang === "ta" ? "சந்தையில் விற்றல்" : "SELL SIGNAL"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              ₹38 <span className="text-sm font-normal text-muted-foreground">/ {lang === "ta" ? "கிலோ" : "kg"}</span>
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "கோபிசெட்டிபாளையம் சந்தை • நேற்று ₹37 (+2.7%)"
                : "Gobichettipalayam Mandi • Prev: ₹37 (+2.7%)"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {lang === "ta"
              ? "வரத்து உச்ச நிலை — அடுத்த 7 நாட்களில் விலை குறைய வாய்ப்பு."
              : "Peak arrivals detected — potential price softening over next 7 days."}
          </CardContent>
        </Card>
      </div>

      {/* 30-Day Trend Chart */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-lg">
              {lang === "ta" ? "30-நாள் சந்தை விலை போக்கு" : "30-Day Mandi Price Trend"}
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
              onClick={() => setActiveChartCrop("turmeric")}
            >
              {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
            </Button>
            <Button
              size="sm"
              variant={activeChartCrop === "banana" ? "default" : "outline"}
              className="h-7 text-xs"
              onClick={() => setActiveChartCrop("banana")}
            >
              {lang === "ta" ? "வாழை" : "Banana"}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis
                  domain={activeChartCrop === "turmeric" ? [10000, 14000] : [2200, 3400]}
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பயிர்" : "Crop"}</TableHead>
                <TableHead>{lang === "ta" ? "மண்டி" : "Mandi"}</TableHead>
                <TableHead>{lang === "ta" ? "மாதிரி விலை" : "Modal Price"}</TableHead>
                <TableHead>{lang === "ta" ? "வரம்பு (குறைவு - உயர்வு)" : "Range (Min - Max)"}</TableHead>
                <TableHead>{lang === "ta" ? "போக்கு" : "Trend"}</TableHead>
                <TableHead>{lang === "ta" ? "ஆதாரம்" : "Source"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta" ? "விலை தகவல்கள் ஏற்றப்படுகின்றன..." : "Loading market prices..."}
                  </TableCell>
                </TableRow>
              ) : filteredPrices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta" ? "விலை விவரங்கள் எதுவும் கிடைக்கவில்லை." : "No market price records found."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredPrices.map((p) => {
                  const dir = p.trend?.direction;
                  return (
                    <TableRow key={p.id}>
                      <TableCell className="font-semibold">
                        {lang === "ta" ? p.crop_tamil_name || p.crop_name : p.crop_name}
                      </TableCell>
                      <TableCell>{p.market_name}</TableCell>
                      <TableCell className="font-bold text-emerald-700">
                        ₹{p.modal_price.toLocaleString("en-IN")}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        ₹{p.min_price.toLocaleString("en-IN")} - ₹{p.max_price.toLocaleString("en-IN")}
                      </TableCell>
                      <TableCell>
                        {dir === "up" && (
                          <Badge variant="success" className="gap-1">
                            <TrendingUp className="w-3 h-3" /> +{p.trend?.percent.toFixed(1)}%
                          </Badge>
                        )}
                        {dir === "down" && (
                          <Badge variant="destructive" className="gap-1">
                            <TrendingDown className="w-3 h-3" /> -{p.trend?.percent.toFixed(1)}%
                          </Badge>
                        )}
                        {(!dir || dir === "stable") && (
                          <Badge variant="outline" className="gap-1">
                            <Minus className="w-3 h-3" /> 0.0%
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="uppercase text-[10px]">
                          {p.source}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
