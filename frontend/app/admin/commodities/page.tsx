"use client";

import React, { useState, useEffect, useMemo } from "react";
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
import { Input } from "@/components/ui/input";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Sprout,
  Search,
  Filter,
  CheckCircle2,
  Database,
  Layers,
  Store,
  Tag,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  ChevronRight,
  Info,
} from "lucide-react";
import {
  CommoditySummary,
  CommodityDetail,
  getCommodities,
  getCommodityDetail,
} from "@/lib/api";

const CATEGORIES = [
  { id: "all", labelEn: "All Categories", labelTa: "அனைத்து வகைகள்" },
  { id: "spice", labelEn: "Spices", labelTa: "மசாலா பயிர்கள்" },
  { id: "fruit", labelEn: "Fruits", labelTa: "பழங்கள்" },
  { id: "vegetable", labelEn: "Vegetables", labelTa: "காய்கறிகள்" },
  { id: "cereal", labelEn: "Cereals", labelTa: "தானியங்கள்" },
  { id: "pulse", labelEn: "Pulses", labelTa: "பருப்பு வகைகள்" },
  { id: "plantation", labelEn: "Plantation", labelTa: "தோட்டப்பயிர்கள்" },
  { id: "cash crop", labelEn: "Cash Crops", labelTa: "பணப்பயிர்கள்" },
  { id: "oilseed", labelEn: "Oilseeds", labelTa: "எண்ணெய் வித்துக்கள்" },
  { id: "tuber", labelEn: "Tubers", labelTa: "கிழங்கு வகைகள்" },
];

export default function CommoditiesRegistryPage() {
  const { lang } = useLanguage();
  const [commodities, setCommodities] = useState<CommoditySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Detail Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedCropId, setSelectedCropId] = useState<string | null>(null);
  const [cropDetail, setCropDetail] = useState<CommodityDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchCommoditiesList = async () => {
    setLoading(true);
    try {
      const data = await getCommodities(selectedCategory === "all" ? undefined : selectedCategory);
      setCommodities(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommoditiesList();
  }, [selectedCategory]);

  const handleOpenDetail = async (id: string) => {
    setSelectedCropId(id);
    setDrawerOpen(true);
    setDetailLoading(true);
    try {
      const detail = await getCommodityDetail(id);
      setCropDetail(detail);
    } finally {
      setDetailLoading(false);
    }
  };

  const filteredCommodities = useMemo(() => {
    if (!searchQuery.trim()) return commodities;
    const q = searchQuery.toLowerCase().trim();
    return commodities.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.tamil_name && c.tamil_name.includes(q)) ||
        (c.scientific_name && c.scientific_name.toLowerCase().includes(q)) ||
        (c.category && c.category.toLowerCase().includes(q))
    );
  }, [commodities, searchQuery]);

  const stats = useMemo(() => {
    const totalVarieties = commodities.reduce((acc, c) => acc + c.variety_count, 0);
    const totalMappings = commodities.reduce((acc, c) => acc + c.source_mapping_count, 0);
    const totalAliases = commodities.reduce((acc, c) => acc + c.alias_count, 0);
    return {
      total: commodities.length,
      varieties: totalVarieties,
      mappings: totalMappings,
      aliases: totalAliases,
    };
  }, [commodities]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              {lang === "ta" ? "தமிழ்நாடு பயிர்கள் பதிவகம்" : "Tamil Nadu Commodity Registry"}
            </h1>
            <Badge variant="default" className="bg-emerald-600/10 text-emerald-700 dark:text-emerald-400 border-emerald-600/20">
              v0.6 Registry
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "38 மாவட்டங்களுக்கான நியமன பயிர்கள், வகைகள் மற்றும் அரசு அமைப்புகளின் நேரடி அடையாளங்கள்."
              : "Statewide canonical agricultural ontology, varietal registry, and deterministic feed mappings."}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchCommoditiesList}
          disabled={loading}
          className="self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          {lang === "ta" ? "புதுப்பி" : "Refresh"}
        </Button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="border border-border/70 shadow-xs">
          <CardContent className="p-4 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400">
              <Sprout className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "பதிவுற்ற பயிர்கள்" : "Total Commodities"}
              </p>
              <h3 className="text-xl font-bold text-foreground">{stats.total}</h3>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border/70 shadow-xs">
          <CardContent className="p-4 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "ரகங்கள்" : "Tracked Varieties"}
              </p>
              <h3 className="text-xl font-bold text-foreground">{stats.varieties}</h3>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border/70 shadow-xs">
          <CardContent className="p-4 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "வெளிப்புற இணைப்புகள்" : "Source Mappings"}
              </p>
              <h3 className="text-xl font-bold text-foreground">{stats.mappings}</h3>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border/70 shadow-xs">
          <CardContent className="p-4 flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400">
              <Tag className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "வட்டாரப் பெயர்கள்" : "Registered Aliases"}
              </p>
              <h3 className="text-xl font-bold text-foreground">{stats.aliases}</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder={
              lang === "ta"
                ? "பயிர் பெயர், தமிழ் பெயர், அறிவியல் பெயர் தேடு..."
                : "Search crop name, Tamil name, or scientific name..."
            }
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-card"
          />
        </div>
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 sm:pb-0">
          <Filter className="w-4 h-4 text-muted-foreground shrink-0 hidden sm:block" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-card border border-input rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary shrink-0"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {lang === "ta" ? cat.labelTa : cat.labelEn}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Commodity Table */}
      <Card className="border border-border/80 shadow-xs overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30">
              <TableHead className="font-semibold text-foreground">
                {lang === "ta" ? "பயிர் & தமிழ்ப்பெயர்" : "Commodity & Tamil Name"}
              </TableHead>
              <TableHead className="font-semibold text-foreground">
                {lang === "ta" ? "வகைப்பாடு" : "Category"}
              </TableHead>
              <TableHead className="font-semibold text-foreground">
                {lang === "ta" ? "அலகு" : "Unit"}
              </TableHead>
              <TableHead className="font-semibold text-foreground text-center">
                {lang === "ta" ? "ரகங்கள்" : "Varieties"}
              </TableHead>
              <TableHead className="font-semibold text-foreground text-center">
                {lang === "ta" ? "வெளிப்புற இணைப்புகள்" : "Source Mappings"}
              </TableHead>
              <TableHead className="font-semibold text-foreground text-center">
                {lang === "ta" ? "சந்தை தகவல்" : "Active Markets"}
              </TableHead>
              <TableHead className="font-semibold text-foreground text-right">
                {lang === "ta" ? "செயல்கள்" : "Actions"}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-primary" />
                  {lang === "ta" ? "ஏற்றப்படுகிறது..." : "Loading commodity ontology..."}
                </TableCell>
              </TableRow>
            ) : filteredCommodities.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                  {lang === "ta" ? "பயிர்கள் எதுவும் கண்டறியப்படவில்லை" : "No commodities matched your criteria"}
                </TableCell>
              </TableRow>
            ) : (
              filteredCommodities.map((crop) => (
                <TableRow key={crop.id} className="hover:bg-muted/20 transition-colors">
                  <TableCell>
                    <div className="font-bold text-foreground capitalize flex items-center space-x-2">
                      <span>{crop.name}</span>
                      {crop.tamil_name && (
                        <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium">
                          {crop.tamil_name}
                        </span>
                      )}
                    </div>
                    {crop.scientific_name && (
                      <div className="text-xs italic text-muted-foreground mt-0.5">
                        {crop.scientific_name}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="capitalize text-xs font-normal">
                      {crop.category || "General"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs font-mono text-muted-foreground">
                    {crop.unit}
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
                      {crop.variety_count}
                    </span>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300 border border-purple-200 dark:border-purple-900">
                      {crop.source_mapping_count} feeds
                    </span>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900">
                      {crop.reporting_market_count} mandis
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenDetail(crop.id)}
                      className="text-primary hover:text-primary hover:bg-primary/10"
                    >
                      <span className="text-xs font-semibold mr-1">
                        {lang === "ta" ? "விவரம்" : "Inspect"}
                      </span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Slide-over Detail Drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent side="right" className="w-full sm:max-w-xl overflow-y-auto p-6">
          <SheetHeader className="pb-4 border-b border-border">
            <SheetTitle className="text-xl flex items-center space-x-2">
              <span className="capitalize">{cropDetail?.name || "Commodity"}</span>
              {cropDetail?.tamil_name && (
                <span className="text-sm px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-semibold">
                  {cropDetail.tamil_name}
                </span>
              )}
            </SheetTitle>
            <SheetDescription className="text-xs italic">
              {cropDetail?.scientific_name} • {cropDetail?.category}
            </SheetDescription>
          </SheetHeader>

          {detailLoading ? (
            <div className="py-20 text-center text-muted-foreground space-y-2">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-primary" />
              <p className="text-xs">{lang === "ta" ? "விவரங்கள் ஏற்றப்படுகின்றன..." : "Loading commodity intelligence..."}</p>
            </div>
          ) : cropDetail ? (
            <div className="py-4 space-y-6">
              {/* Core Attributes */}
              <div className="grid grid-cols-2 gap-3 text-xs bg-muted/30 p-3 rounded-lg border border-border/60">
                <div>
                  <span className="text-muted-foreground block">{lang === "ta" ? "இயல்பு அலகு" : "Default Unit"}:</span>
                  <span className="font-semibold text-foreground">{cropDetail.default_unit || cropDetail.unit}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">{lang === "ta" ? "சந்தை வர்த்தக அலகு" : "Mandi Unit"}:</span>
                  <span className="font-semibold text-foreground">{cropDetail.market_unit || "quintal"}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">{lang === "ta" ? "பருவம்" : "Season"}:</span>
                  <span className="font-semibold text-foreground capitalize">{cropDetail.season_type || "Year-round"}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">{lang === "ta" ? "தோட்டக்கலை பயிர்" : "Horticulture"}:</span>
                  <span className="font-semibold text-foreground">{cropDetail.is_horticulture ? "Yes" : "No"}</span>
                </div>
              </div>

              {/* Deterministic Source Mappings */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center">
                  <Database className="w-3.5 h-3.5 mr-1.5 text-primary" />
                  {lang === "ta" ? "வெளிப்புற அரசு தரவு இணைப்புகள்" : "Deterministic Source Mappings (OGD/Agmarknet)"}
                </h4>
                {cropDetail.source_mappings.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic">
                    {lang === "ta" ? "வெளிப்புற இணைப்புகள் எதுவும் இல்லை" : "No external source mappings configured yet"}
                  </p>
                ) : (
                  <div className="space-y-1.5">
                    {cropDetail.source_mappings.map((m) => (
                      <div
                        key={m.id}
                        className="flex items-center justify-between p-2 rounded-md bg-card border border-border/70 text-xs"
                      >
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="uppercase text-[10px] font-bold">
                            {m.source_code}
                          </Badge>
                          <span className="font-mono text-foreground font-semibold">{m.external_code}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-muted-foreground">{m.external_name}</div>
                          <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                            Confidence: {Math.round(m.confidence * 100)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Varieties */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center">
                  <Layers className="w-3.5 h-3.5 mr-1.5 text-primary" />
                  {lang === "ta" ? "பதிவுற்ற ரகங்கள்" : "Registered Varieties"} ({cropDetail.varieties.length})
                </h4>
                {cropDetail.varieties.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic">
                    {lang === "ta" ? "ரகங்கள் எதுவும் பதிவு செய்யப்படவில்லை" : "No varieties registered"}
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {cropDetail.varieties.map((v) => (
                      <span
                        key={v.id}
                        className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-900"
                      >
                        {v.name}
                        {v.grade && <span className="ml-1 text-[10px] text-muted-foreground">({v.grade})</span>}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Regional Aliases */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center">
                  <Tag className="w-3.5 h-3.5 mr-1.5 text-primary" />
                  {lang === "ta" ? "அங்கீகரிக்கப்பட்ட வட்டாரப் பெயர்கள்" : "Recognized Regional Aliases"} ({cropDetail.aliases.length})
                </h4>
                {cropDetail.aliases.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic">
                    {lang === "ta" ? "வட்டாரப் பெயர்கள் இல்லை" : "No aliases registered"}
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {cropDetail.aliases.map((a) => (
                      <span
                        key={a.id}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-muted text-muted-foreground border border-border"
                      >
                        {a.alias}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Active Reporting Mandis */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center">
                  <Store className="w-3.5 h-3.5 mr-1.5 text-primary" />
                  {lang === "ta" ? "தகவல் தரும் ஒழுங்குமுறை மண்டிகள்" : "Active Reporting Mandis"} ({cropDetail.active_markets.length})
                </h4>
                {cropDetail.active_markets.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic">
                    {lang === "ta" ? "தற்போது மண்டிகள் எதுவும் பதிவு செய்யப்படவில்லை" : "No price reports recorded for this commodity yet"}
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {cropDetail.active_markets.map((m, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  );
}
