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
  Search,
  UserPlus,
  ShieldCheck,
  RefreshCw,
  Clock,
  X,
  Loader2,
  CheckCircle2,
  Sprout,
  Plus,
  MapPin,
  Calculator,
  Trash2,
  Info,
  Calendar,
  Layers,
  ChevronRight,
} from "lucide-react";
import {
  getFPOs,
  getFarmers,
  createFarmer,
  getCrops,
  getFarmPlots,
  createFarmPlot,
  deleteFarmPlot,
  getFarmYieldEstimate,
  Farmer,
  FPO,
  Crop,
  FarmPlot,
  FarmYieldEstimate,
  FarmerCreatePayload,
  FarmCreatePayload,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

const DEFAULT_DISTRICT = "Erode";

interface AddFarmerForm {
  name: string;
  phone: string;
  password: string;
  village: string;
  taluk: string;
  farm_area_acres: string;
  language_preference: string;
}

const EMPTY_FORM: AddFarmerForm = {
  name: "",
  phone: "",
  password: "farmer123",
  village: "",
  taluk: "",
  farm_area_acres: "",
  language_preference: "ta",
};

interface AddPlotForm {
  crop_id: string;
  plot_name: string;
  area_acres: string;
  village: string;
  soil_type: string;
  irrigation_type: string;
  sowing_date: string;
}

const EMPTY_PLOT_FORM: AddPlotForm = {
  crop_id: "",
  plot_name: "",
  area_acres: "",
  village: "",
  soil_type: "Red Loam",
  irrigation_type: "Drip",
  sowing_date: new Date().toISOString().split("T")[0],
};

export default function FarmersPage() {
  const { lang } = useLanguage();
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [fpos, setFpos] = useState<FPO[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [activeFpo, setActiveFpo] = useState<FPO | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [consentFilter, setConsentFilter] = useState<"all" | "granted" | "pending">("all");
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Add farmer modal state
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<AddFarmerForm>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Multi-Plot Drawer State
  const [selectedFarmer, setSelectedFarmer] = useState<Farmer | null>(null);
  const [plots, setPlots] = useState<FarmPlot[]>([]);
  const [loadingPlots, setLoadingPlots] = useState(false);
  const [showAddPlotModal, setShowAddPlotModal] = useState(false);
  const [plotForm, setPlotForm] = useState<AddPlotForm>(EMPTY_PLOT_FORM);
  const [submittingPlot, setSubmittingPlot] = useState(false);
  const [plotError, setPlotError] = useState<string | null>(null);

  // Selected plot for yield breakdown view
  const [selectedPlotEstimate, setSelectedPlotEstimate] = useState<FarmYieldEstimate | null>(null);
  const [loadingEstimate, setLoadingEstimate] = useState(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [fpoList, token, cropList] = await Promise.all([
        getFPOs(),
        ensureToken(),
        getCrops(),
      ]);
      setFpos(fpoList);
      setCrops(cropList);
      const primaryFpo = fpoList[0] || null;
      setActiveFpo(primaryFpo);

      if (primaryFpo) {
        const res = await getFarmers(primaryFpo.id, token ?? undefined, searchTerm);
        setFarmers(res.farmers);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async (term: string) => {
    setSearchTerm(term);
    if (activeFpo) {
      const token = await ensureToken();
      const res = await getFarmers(activeFpo.id, token ?? undefined, term);
      setFarmers(res.farmers);
    }
  };

  const handleAddFarmer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFpo) return;
    setSubmitting(true);
    setSubmitError(null);

    try {
      const token = await ensureToken();
      if (!token) {
        setSubmitError("Authentication failed. Please refresh the page.");
        return;
      }

      const payload: FarmerCreatePayload = {
        name: form.name.trim(),
        phone: form.phone.trim(),
        password: form.password || "farmer123",
        village: form.village.trim(),
        taluk: form.taluk.trim(),
        district: DEFAULT_DISTRICT,
        farm_area_acres: parseFloat(form.farm_area_acres) || 0,
        language_preference: form.language_preference,
        consent_given: true,
        lang: form.language_preference,
        alerts_opt_in: false,
      };

      const { farmer, error } = await createFarmer(activeFpo.id, payload, token);
      if (error) {
        setSubmitError(error);
      } else {
        setSubmitSuccess(true);
        setForm(EMPTY_FORM);
        setTimeout(async () => {
          setSubmitSuccess(false);
          setShowModal(false);
          await loadData();
        }, 1200);
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Open Multi-Plot Drawer for a Farmer
  const handleOpenPlots = async (farmer: Farmer) => {
    setSelectedFarmer(farmer);
    setLoadingPlots(true);
    setPlotError(null);
    setPlotForm({
      ...EMPTY_PLOT_FORM,
      crop_id: crops.length > 0 ? crops[0].id : "",
      village: farmer.village,
    });
    try {
      const token = await ensureToken();
      const res = await getFarmPlots({ farmer_id: farmer.id }, token ?? undefined);
      setPlots(res.plots);
    } catch (err) {
      console.warn("Failed to load plots:", err);
    } finally {
      setLoadingPlots(false);
    }
  };

  const handleAddPlot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarmer || !plotForm.crop_id) return;
    const area = parseFloat(plotForm.area_acres);
    if (!area || area <= 0) {
      setPlotError(lang === "ta" ? "சரியான நிலப்பரப்பை உள்ளிடவும்." : "Please enter a valid plot area.");
      return;
    }

    setSubmittingPlot(true);
    setPlotError(null);
    try {
      const token = await ensureToken();
      const payload: FarmCreatePayload = {
        farmer_id: selectedFarmer.id,
        crop_id: plotForm.crop_id,
        plot_name: plotForm.plot_name.trim() || `${selectedFarmer.name} Plot ${plots.length + 1}`,
        area_acres: area,
        village: plotForm.village.trim() || selectedFarmer.village,
        soil_type: plotForm.soil_type,
        irrigation_type: plotForm.irrigation_type,
        sowing_date: plotForm.sowing_date || undefined,
        status: "growing",
      };

      const newPlot = await createFarmPlot(payload, token ?? undefined);
      if (newPlot) {
        setShowAddPlotModal(false);
        // Refresh plots
        const refreshed = await getFarmPlots({ farmer_id: selectedFarmer.id }, token ?? undefined);
        setPlots(refreshed.plots);
      }
    } catch (err: any) {
      setPlotError(err.message || "Failed to create plot");
    } finally {
      setSubmittingPlot(false);
    }
  };

  const handleDeletePlot = async (plotId: string) => {
    if (!confirm(lang === "ta" ? "இந்த நிலப்பகுதியை நீக்க விரும்புகிறீர்களா?" : "Are you sure you want to delete this plot?")) {
      return;
    }
    try {
      const token = await ensureToken();
      const success = await deleteFarmPlot(plotId, token ?? undefined);
      if (success && selectedFarmer) {
        setPlots((prev) => prev.filter((p) => p.id !== plotId));
      }
    } catch (err) {
      console.warn("Failed to delete plot:", err);
    }
  };

  const handleViewEstimate = async (plot: FarmPlot) => {
    setLoadingEstimate(true);
    try {
      const token = await ensureToken();
      const est = await getFarmYieldEstimate(plot.id, token ?? undefined);
      setSelectedPlotEstimate(est);
    } catch (err) {
      console.warn("Failed to fetch estimate breakdown:", err);
    } finally {
      setLoadingEstimate(false);
    }
  };

  // Live estimated yield computation for Add Plot form
  const liveEstimatedYieldKg = useMemo(() => {
    const area = parseFloat(plotForm.area_acres);
    if (!area || area <= 0 || !plotForm.crop_id) return null;

    const crop = crops.find((c) => c.id === plotForm.crop_id);
    const cropName = (crop?.name || "").toLowerCase();

    let basePerAcreKg = 2500;
    if (cropName.includes("turmeric") || cropName.includes("மஞ்சள்")) basePerAcreKg = 10000;
    else if (cropName.includes("banana") || cropName.includes("வாழை")) basePerAcreKg = 18000;
    else if (cropName.includes("coconut") || cropName.includes("தென்னை")) basePerAcreKg = 6000;
    else if (cropName.includes("tomato") || cropName.includes("தக்காளி")) basePerAcreKg = 12000;
    else if (cropName.includes("paddy") || cropName.includes("நெல்")) basePerAcreKg = 2400;

    let irrigMult = 1.0;
    if (plotForm.irrigation_type === "Drip") irrigMult = 1.15;
    else if (plotForm.irrigation_type === "Rainfed") irrigMult = 0.70;

    let soilMult = 1.0;
    if (plotForm.soil_type === "Red Loam") soilMult = 1.10;
    else if (plotForm.soil_type === "Clay Loam") soilMult = 0.85;

    return Math.round(area * basePerAcreKg * irrigMult * soilMult);
  }, [plotForm.area_acres, plotForm.crop_id, plotForm.soil_type, plotForm.irrigation_type, crops]);

  const filteredFarmers = farmers.filter((f) => {
    if (consentFilter === "granted") return Boolean(f.notice_sent_at || f.alerts_opt_in);
    if (consentFilter === "pending") return !f.notice_sent_at && !f.alerts_opt_in;
    return true;
  });

  const totalPlotAcreage = useMemo(() => {
    return plots.reduce((acc, p) => acc + (p.area_acres || 0), 0);
  }, [plots]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "உழவர் பதிவேடு & பல நிலப்பரப்பு மேலாண்மை" : "Farmer Directory & Multi-Plot Management"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "FPO உறுப்பினர் விவசாயிகள், தனித்தனி நிலங்கள் (Multi-Plot), விதிமுறை அடிப்படையிலான மகசூல் மதிப்பீடு மற்றும் DPDP ஒப்புதல் நிலை."
              : "Registered FPO member farmers, discrete multi-plot holdings, rule-based yield estimations, and DPDP compliance."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
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
          <Button
            size="sm"
            className="h-8"
            onClick={() => { setShowModal(true); setSubmitError(null); setSubmitSuccess(false); }}
          >
            <UserPlus className="w-3.5 h-3.5 mr-1.5" />
            {lang === "ta" ? "விவசாயி சேர்" : "Add Farmer"}
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <Input
                placeholder={
                  lang === "ta"
                    ? "பெயர், கிராமம் அல்லது வட்டம் மூலம் தேடுக..."
                    : "Search by farmer name, village, or taluk..."
                }
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9 h-10"
              />
            </div>
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <Badge
                variant={consentFilter === "all" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("all")}
              >
                {lang === "ta" ? "அனைத்து விவசாயிகள்" : "All Farmers"}
              </Badge>
              <Badge
                variant={consentFilter === "granted" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("granted")}
              >
                {lang === "ta" ? "ஒப்புதல் பெற்றவை" : "Consent Active"}
              </Badge>
              <Badge
                variant={consentFilter === "pending" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("pending")}
              >
                {lang === "ta" ? "நிலுவையில்" : "Pending"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farmer Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                {lang === "ta" ? "பதிவு செய்யப்பட்ட விவசாயிகள்" : "Registered Member Farmers"}
              </CardTitle>
              <CardDescription>
                {lang === "ta"
                  ? "விவசாயிகளின் விவரங்கள், மொத்த நிலப்பரப்பு மற்றும் தனித்தனி நிலங்களை (Plots) நிர்வகிக்கலாம்."
                  : "Member farmers, total acreage, and multi-plot holdings with yield forecasts."}
              </CardDescription>
            </div>
            <Badge variant="secondary">
              {filteredFarmers.length} {lang === "ta" ? "உழவர்கள்" : "Farmers"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பெயர்" : "Name"}</TableHead>
                <TableHead>{lang === "ta" ? "கிராமம் / வட்டம்" : "Village / Taluk"}</TableHead>
                <TableHead>{lang === "ta" ? "மொத்த நிலம்" : "Holding Area"}</TableHead>
                <TableHead>{lang === "ta" ? "தொலைபேசி" : "Phone"}</TableHead>
                <TableHead>{lang === "ta" ? "DPDP ஒப்புதல்" : "DPDP Status"}</TableHead>
                <TableHead className="text-right">{lang === "ta" ? "தனி நிலங்கள்" : "Farm Plots"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                    {lang === "ta" ? "விவசாயிகள் பட்டியல் ஏற்றப்படுகிறது..." : "Loading farmer records..."}
                  </TableCell>
                </TableRow>
              ) : filteredFarmers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta"
                      ? "தேடலுக்குரிய விவசாயிகள் எவரும் இல்லை. மேலே 'விவசாயி சேர்' பொத்தானை கிளிக் செய்யுங்கள்."
                      : "No farmers found. Click 'Add Farmer' above to register the first one."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredFarmers.map((f) => {
                  const hasConsent = Boolean(f.notice_sent_at || f.alerts_opt_in);
                  const maskedPhone = f.phone
                    ? f.phone.replace(/(\+?\d{2,5}\s?\d{3})\d{4}/, "$1••••")
                    : "—";

                  return (
                    <TableRow key={f.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-semibold text-foreground">
                        {f.name}
                      </TableCell>
                      <TableCell>
                        {f.village}, {f.taluk}
                      </TableCell>
                      <TableCell>
                        <span className="font-medium text-foreground">{f.farm_area_acres}</span>{" "}
                        <span className="text-xs text-muted-foreground">{lang === "ta" ? "ஏக்கர்" : "acres"}</span>
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {maskedPhone}
                      </TableCell>
                      <TableCell>
                        {hasConsent ? (
                          <Badge variant="success" className="gap-1 text-xs">
                            <ShieldCheck className="w-3 h-3" />
                            <span>{lang === "ta" ? "ஒப்புதல் பதிவானது" : "Notice Logged"}</span>
                          </Badge>
                        ) : (
                          <Badge variant="warning" className="gap-1 text-xs">
                            <Clock className="w-3 h-3" />
                            <span>{lang === "ta" ? "நிலுவையில்" : "Pending Notice"}</span>
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleOpenPlots(f)}
                          className="h-8 text-xs gap-1.5 border-emerald-300 dark:border-emerald-800 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 font-medium"
                        >
                          <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{lang === "ta" ? "நிலங்கள்" : "Plots"}</span>
                          <ChevronRight className="w-3 h-3 ml-0.5 opacity-60" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Slide-over Multi-Plot Drawer */}
      {selectedFarmer && (
        <div
          className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-xs transition-opacity animate-in fade-in-0"
          onClick={(e) => { if (e.target === e.currentTarget) setSelectedFarmer(null); }}
        >
          <div className="w-full max-w-2xl bg-background border-l shadow-2xl h-full flex flex-col animate-in slide-in-from-right duration-300">
            {/* Drawer Header */}
            <div className="p-5 border-b bg-muted/30 flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <Sprout className="w-5 h-5 text-emerald-600" />
                  <h3 className="text-lg font-bold text-foreground">
                    {selectedFarmer.name} — {lang === "ta" ? "நில விவரங்கள்" : "Farm Plots"}
                  </h3>
                </div>
                <p className="text-xs text-muted-foreground mt-1 flex items-center space-x-3">
                  <span>
                    <MapPin className="w-3 h-3 inline mr-1 text-muted-foreground" />
                    {selectedFarmer.village}, {selectedFarmer.taluk}
                  </span>
                  <span>•</span>
                  <span>
                    {lang === "ta" ? "பதிவு செய்யப்பட்ட பரப்பளவு:" : "Registered Area:"}{" "}
                    <strong className="text-foreground">{selectedFarmer.farm_area_acres} {lang === "ta" ? "ஏக்கர்" : "acres"}</strong>
                  </span>
                </p>
              </div>
              <button
                className="text-muted-foreground hover:text-foreground p-1 rounded-md"
                onClick={() => setSelectedFarmer(null)}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Plot Stats Summary Bar */}
            <div className="px-5 py-3 border-b bg-emerald-50/50 dark:bg-emerald-950/20 flex items-center justify-between">
              <div className="flex items-center space-x-4 text-xs">
                <div>
                  <span className="text-muted-foreground">{lang === "ta" ? "மொத்த நிலங்கள்:" : "Total Plots:"} </span>
                  <span className="font-bold text-foreground">{plots.length}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">{lang === "ta" ? "பயிரிடப்பட்ட பரப்பளவு:" : "Plotted Area:"} </span>
                  <span className="font-bold text-emerald-700 dark:text-emerald-400">
                    {totalPlotAcreage.toFixed(2)} {lang === "ta" ? "ஏக்கர்" : "acres"}
                  </span>
                </div>
              </div>
              <Button
                size="sm"
                className="h-8 text-xs bg-emerald-600 hover:bg-emerald-700 text-white gap-1"
                onClick={() => {
                  setShowAddPlotModal(true);
                  setPlotError(null);
                }}
              >
                <Plus className="w-3.5 h-3.5" />
                {lang === "ta" ? "புதிய நிலம் சேர்" : "Add Plot"}
              </Button>
            </div>

            {/* Plots Content List */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {loadingPlots ? (
                <div className="flex flex-col items-center justify-center py-16 text-muted-foreground text-sm space-y-2">
                  <Loader2 className="w-6 h-6 animate-spin text-emerald-600" />
                  <p>{lang === "ta" ? "நில விவரங்கள் ஏற்றப்படுகின்றன..." : "Loading farmer's plots..."}</p>
                </div>
              ) : plots.length === 0 ? (
                <div className="text-center py-16 px-4 border border-dashed rounded-xl bg-muted/20">
                  <Layers className="w-10 h-10 text-muted-foreground mx-auto mb-2 opacity-50" />
                  <p className="font-medium text-foreground text-sm">
                    {lang === "ta" ? "இன்னும் நிலங்கள் எதுவும் சேர்க்கப்படவில்லை" : "No individual plots registered yet"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                    {lang === "ta"
                      ? "ஒரே விவசாயியின் பல தனி நிலங்களை பயிர், மண் மற்றும் பாசன முறையோடு பதிவு செய்யலாம்."
                      : "Register non-contiguous plots with specific crops, soil, and irrigation for accurate yield estimates."}
                  </p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-4 text-xs gap-1.5"
                    onClick={() => setShowAddPlotModal(true)}
                  >
                    <Plus className="w-3.5 h-3.5" />
                    {lang === "ta" ? "முதல் நிலத்தை பதிவு செய்க" : "Register First Plot"}
                  </Button>
                </div>
              ) : (
                plots.map((plot) => {
                  const estKg = plot.expected_yield_kg || 0;
                  const estQtl = (estKg / 100).toFixed(1);

                  return (
                    <Card key={plot.id} className="border hover:border-emerald-300 dark:hover:border-emerald-800 transition-all">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center space-x-2">
                              <h4 className="font-bold text-foreground text-sm">
                                {plot.plot_name || "Plot"}
                              </h4>
                              <Badge
                                variant={
                                  plot.status === "ready_for_harvest"
                                    ? "success"
                                    : plot.status === "growing"
                                    ? "default"
                                    : "secondary"
                                }
                                className="text-[11px] capitalize"
                              >
                                {plot.status}
                              </Badge>
                            </div>
                            <p className="text-xs text-emerald-800 dark:text-emerald-300 font-medium mt-0.5">
                              {plot.crop_name} {plot.crop_tamil_name ? `(${plot.crop_tamil_name})` : ""}
                            </p>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 w-7 p-0 text-muted-foreground hover:text-red-600"
                              onClick={() => handleDeletePlot(plot.id)}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </Button>
                          </div>
                        </div>

                        {/* Plot Attributes */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs bg-muted/40 p-2.5 rounded-lg">
                          <div>
                            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                              {lang === "ta" ? "பரப்பளவு" : "Area"}
                            </span>
                            <span className="font-bold text-foreground">{plot.area_acres} {lang === "ta" ? "ஏக்" : "acres"}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                              {lang === "ta" ? "மண் வகை" : "Soil"}
                            </span>
                            <span className="font-medium text-foreground">{plot.soil_type || "Standard"}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                              {lang === "ta" ? "பாசனம்" : "Irrigation"}
                            </span>
                            <span className="font-medium text-foreground">{plot.irrigation_type || "Canal"}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                              {lang === "ta" ? "விதைப்பு தேதி" : "Sown"}
                            </span>
                            <span className="font-medium text-foreground">{plot.sowing_date || "—"}</span>
                          </div>
                        </div>

                        {/* Yield Forecast Banner */}
                        <div className="flex items-center justify-between pt-1">
                          <div className="flex items-center space-x-2">
                            <Calculator className="w-4 h-4 text-emerald-600" />
                            <div>
                              <span className="text-xs text-muted-foreground mr-1.5">
                                {lang === "ta" ? "எதிர்பார்க்கப்படும் மகசூல்:" : "Expected Yield:"}
                              </span>
                              <Badge variant="outline" className="bg-emerald-50 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300 font-bold border-emerald-200">
                                {estKg.toLocaleString()} kg (~{estQtl} {lang === "ta" ? "குவிண்டால்" : "qtl"})
                              </Badge>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs text-emerald-700 hover:text-emerald-800 gap-1 p-0 px-2"
                            onClick={() => handleViewEstimate(plot)}
                          >
                            <Info className="w-3 h-3" />
                            <span>{lang === "ta" ? "விவரம்" : "Details"}</span>
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Plot Modal */}
      {showAddPlotModal && selectedFarmer && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={(e) => { if (e.target === e.currentTarget) setShowAddPlotModal(false); }}
        >
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-lg p-6 relative border">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
              onClick={() => setShowAddPlotModal(false)}
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 mb-1">
              <Sprout className="w-5 h-5 text-emerald-600" />
              <h3 className="text-lg font-bold text-foreground">
                {lang === "ta" ? "புதிய நிலப்பகுதி பதிவு" : "Register Farm Plot"}
              </h3>
            </div>
            <p className="text-xs text-muted-foreground mb-4">
              {lang === "ta"
                ? `${selectedFarmer.name} அவர்களுக்கு புதிய பயிர் நிலப்பகுதியை இணைக்கவும்.`
                : `Attach a discrete agricultural plot to ${selectedFarmer.name}.`}
            </p>

            <form onSubmit={handleAddPlot} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                {/* Crop Selection */}
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "பயிர் *" : "Crop *"}
                  </label>
                  <select
                    required
                    className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                    value={plotForm.crop_id}
                    onChange={(e) => setPlotForm((p) => ({ ...p, crop_id: e.target.value }))}
                  >
                    {crops.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} {c.tamil_name ? `(${c.tamil_name})` : ""}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Plot Name */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "நிலத்தின் பெயர்" : "Plot Name / Identifier"}
                  </label>
                  <Input
                    placeholder={lang === "ta" ? "எ.கா. கிழக்கு தோட்டம்" : "e.g. East Canal Field"}
                    value={plotForm.plot_name}
                    onChange={(e) => setPlotForm((p) => ({ ...p, plot_name: e.target.value }))}
                  />
                </div>

                {/* Area Acres */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "பரப்பளவு (ஏக்கர்) *" : "Plot Area (acres) *"}
                  </label>
                  <Input
                    required
                    type="number"
                    step="0.05"
                    min="0.05"
                    placeholder="1.5"
                    value={plotForm.area_acres}
                    onChange={(e) => setPlotForm((p) => ({ ...p, area_acres: e.target.value }))}
                  />
                </div>

                {/* Soil Type */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "மண் வகை" : "Soil Type"}
                  </label>
                  <select
                    className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                    value={plotForm.soil_type}
                    onChange={(e) => setPlotForm((p) => ({ ...p, soil_type: e.target.value }))}
                  >
                    <option value="Red Loam">Red Loam (+10% yield)</option>
                    <option value="Black Cotton">Black Cotton</option>
                    <option value="Alluvial">Alluvial</option>
                    <option value="Clay Loam">Clay Loam (-15% yield)</option>
                    <option value="Sandy Loam">Sandy Loam</option>
                  </select>
                </div>

                {/* Irrigation Type */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "பாசன முறை" : "Irrigation Method"}
                  </label>
                  <select
                    className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                    value={plotForm.irrigation_type}
                    onChange={(e) => setPlotForm((p) => ({ ...p, irrigation_type: e.target.value }))}
                  >
                    <option value="Drip">Drip Irrigation (+15% yield)</option>
                    <option value="Canal">Canal Irrigation (Baseline)</option>
                    <option value="Borewell">Borewell (Baseline)</option>
                    <option value="Rainfed">Rainfed (-30% yield)</option>
                  </select>
                </div>

                {/* Village */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "கிராமம்" : "Village"}
                  </label>
                  <Input
                    value={plotForm.village}
                    onChange={(e) => setPlotForm((p) => ({ ...p, village: e.target.value }))}
                    placeholder="Village location"
                  />
                </div>

                {/* Sowing Date */}
                <div>
                  <label className="text-xs font-semibold text-foreground block mb-1">
                    {lang === "ta" ? "விதைப்பு தேதி" : "Sowing Date"}
                  </label>
                  <Input
                    type="date"
                    value={plotForm.sowing_date}
                    onChange={(e) => setPlotForm((p) => ({ ...p, sowing_date: e.target.value }))}
                  />
                </div>
              </div>

              {/* Live Yield Calculation Preview Box */}
              {liveEstimatedYieldKg !== null && (
                <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg p-3 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-emerald-900 dark:text-emerald-200 flex items-center">
                      <Calculator className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                      {lang === "ta" ? "கணிக்கப்பட்ட விளைச்சல் (விதிமுறை மதிப்பீடு):" : "Calculated Agro-Climatic Yield:"}
                    </span>
                    <span className="font-bold text-emerald-700 dark:text-emerald-300 text-sm">
                      {liveEstimatedYieldKg.toLocaleString()} kg
                    </span>
                  </div>
                  <p className="text-[11px] text-emerald-800 dark:text-emerald-400">
                    {lang === "ta"
                      ? "தமிழ்நாடு வேளாண் பல்கலைக் கழக வழிகாட்டுதலின்படி மண் மற்றும் பாசன பெருக்கிகள் கணக்கிடப்பட்டுள்ளன."
                      : "Computed using TNAU regional benchmarks with soil & irrigation multipliers."}
                  </p>
                </div>
              )}

              {plotError && (
                <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
                  {plotError}
                </p>
              )}

              <div className="flex items-center space-x-2 pt-2">
                <Button type="submit" className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white" disabled={submittingPlot}>
                  {submittingPlot ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{lang === "ta" ? "பதிவாகிறது..." : "Registering..."}</>
                  ) : (
                    <><Plus className="w-4 h-4 mr-2" />{lang === "ta" ? "நிலம் பதிவு செய்" : "Register Plot"}</>
                  )}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowAddPlotModal(false)}>
                  {lang === "ta" ? "ரத்து" : "Cancel"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Yield Estimate Breakdown Modal */}
      {selectedPlotEstimate && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={(e) => { if (e.target === e.currentTarget) setSelectedPlotEstimate(null); }}
        >
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-md p-6 relative border">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
              onClick={() => setSelectedPlotEstimate(null)}
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 mb-1">
              <Calculator className="w-5 h-5 text-emerald-600" />
              <h3 className="text-lg font-bold text-foreground">
                {lang === "ta" ? "மகசூல் கணக்கீட்டு விவரம்" : "Agro-Climatic Yield Breakdown"}
              </h3>
            </div>
            <p className="text-xs text-muted-foreground mb-4">
              {selectedPlotEstimate.crop_name} • {selectedPlotEstimate.area_acres} {lang === "ta" ? "ஏக்கர்" : "acres"}
            </p>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-muted/40 rounded-lg space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{lang === "ta" ? "அடிப்படை மகசூல்:" : "Base Agro-Climatic Yield:"}</span>
                  <span className="font-semibold text-foreground">{selectedPlotEstimate.base_yield_kg_per_acre} kg/acre</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{lang === "ta" ? "மண் காரணி (Soil Multiplier):" : "Soil Multiplier:"}</span>
                  <span className="font-semibold text-foreground">{selectedPlotEstimate.soil_factor}x</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{lang === "ta" ? "பாசன காரணி (Irrigation Multiplier):" : "Irrigation Multiplier:"}</span>
                  <span className="font-semibold text-foreground">{selectedPlotEstimate.irrigation_factor}x</span>
                </div>
                <div className="border-t pt-2 flex justify-between text-sm">
                  <span className="font-bold text-foreground">{lang === "ta" ? "மொத்த மகசூல்:" : "Total Expected Yield:"}</span>
                  <span className="font-bold text-emerald-600">{selectedPlotEstimate.estimated_yield_kg.toLocaleString()} kg</span>
                </div>
              </div>

              {selectedPlotEstimate.estimated_harvest_window_start && (
                <div className="flex items-center space-x-2 text-muted-foreground text-xs">
                  <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>
                    {lang === "ta" ? "அறுவடை காலம்:" : "Estimated Harvest:"}{" "}
                    <strong className="text-foreground">{selectedPlotEstimate.estimated_harvest_window_start}</strong> to{" "}
                    <strong className="text-foreground">{selectedPlotEstimate.estimated_harvest_window_end}</strong>
                  </span>
                </div>
              )}

              <p className="text-[11px] text-muted-foreground bg-muted/20 p-2.5 rounded border">
                {selectedPlotEstimate.confidence_note}
              </p>

              <Button
                className="w-full mt-2"
                variant="outline"
                size="sm"
                onClick={() => setSelectedPlotEstimate(null)}
              >
                {lang === "ta" ? "மூடுக" : "Close"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Add Farmer Modal */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}
        >
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-md p-6 relative border">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
              onClick={() => setShowModal(false)}
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-foreground mb-1">
              {lang === "ta" ? "புதிய விவசாயி பதிவு" : "Register New Farmer"}
            </h3>
            <p className="text-xs text-muted-foreground mb-5">
              {lang === "ta"
                ? "FPO உறுப்பினராக விவசாயியை பதிவு செய்யவும். DPDP ஒப்புதல் தானாக பதிவாகும்."
                : "Register a farmer as an FPO member. DPDP consent will be logged automatically."}
            </p>

            {submitSuccess ? (
              <div className="flex flex-col items-center justify-center py-8 space-y-2 text-emerald-700">
                <CheckCircle2 className="w-10 h-10" />
                <p className="font-bold text-base">
                  {lang === "ta" ? "விவசாயி வெற்றிகரமாக சேர்க்கப்பட்டார்!" : "Farmer registered successfully!"}
                </p>
              </div>
            ) : (
              <form onSubmit={handleAddFarmer} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="col-span-2">
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "பெயர் *" : "Full Name *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "முழு பெயர்" : "e.g. Ramasamy K"}
                      value={form.name}
                      onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "தொலைபேசி *" : "Phone *"}
                    </label>
                    <Input
                      required
                      placeholder="9876543210"
                      value={form.phone}
                      onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "நிலப்பரப்பு (ஏக்கர்) *" : "Land Area (acres) *"}
                    </label>
                    <Input
                      required
                      type="number"
                      step="0.1"
                      min="0.1"
                      placeholder="2.5"
                      value={form.farm_area_acres}
                      onChange={(e) => setForm((f) => ({ ...f, farm_area_acres: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "கிராமம் *" : "Village *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "கிராமம்" : "e.g. Kodumudi"}
                      value={form.village}
                      onChange={(e) => setForm((f) => ({ ...f, village: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "வட்டம் *" : "Taluk *"}
                    </label>
                    <Input
                      required
                      placeholder={lang === "ta" ? "வட்டம்" : "e.g. Perundurai"}
                      value={form.taluk}
                      onChange={(e) => setForm((f) => ({ ...f, taluk: e.target.value }))}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="text-xs font-semibold text-foreground block mb-1">
                      {lang === "ta" ? "மொழி விருப்பம்" : "Language Preference"}
                    </label>
                    <select
                      className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                      value={form.language_preference}
                      onChange={(e) => setForm((f) => ({ ...f, language_preference: e.target.value }))}
                    >
                      <option value="ta">தமிழ் (Tamil)</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                </div>

                {submitError && (
                  <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
                    {submitError}
                  </p>
                )}

                <div className="flex items-center space-x-2 pt-2">
                  <Button type="submit" className="flex-1" disabled={submitting}>
                    {submitting ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{lang === "ta" ? "சேர்க்கப்படுகிறது..." : "Registering..."}</>
                    ) : (
                      <><UserPlus className="w-4 h-4 mr-2" />{lang === "ta" ? "விவசாயி சேர்" : "Register Farmer"}</>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                    {lang === "ta" ? "ரத்து" : "Cancel"}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
