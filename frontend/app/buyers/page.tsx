"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
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
  Building2,
  Plus,
  Search,
  Filter,
  RefreshCw,
  FileText,
  Calendar,
  MapPin,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  Package,
  X,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  getBuyers,
  createBuyer,
  getBuyerRequirements,
  createBuyerRequirement,
  getCrops,
  getFPOs,
  Buyer,
  BuyerRequirement,
  Crop,
  FPO,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

export default function BuyersPage() {
  const { lang, t } = useLanguage();
  const [activeTab, setActiveTab] = useState<"buyers" | "requirements">("buyers");

  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [requirements, setRequirements] = useState<BuyerRequirement[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [fpos, setFpos] = useState<FPO[]>([]);
  const [activeFpo, setActiveFpo] = useState<FPO | null>(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [cropFilter, setCropFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Modals
  const [showBuyerModal, setShowBuyerModal] = useState(false);
  const [showReqModal, setShowReqModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Buyer Form
  const [buyerForm, setBuyerForm] = useState({
    company_name: "",
    buyer_type: "processor",
    contact_name: "",
    contact_phone: "",
    contact_email: "",
    location: "Erode",
    district: "Erode",
    gstin: "",
  });

  // Requirement Form
  const [reqForm, setReqForm] = useState({
    buyer_id: "",
    crop_id: "",
    quantity_kg: "",
    min_grade: "A",
    required_date: "",
    delivery_window_days: "7",
    max_price_per_kg: "",
    delivery_location: "",
    notes: "",
  });

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [token, fpoList, cropList] = await Promise.all([
        ensureToken(),
        getFPOs(),
        getCrops(),
      ]);
      setFpos(fpoList);
      const primaryFpo = fpoList[0] || null;
      setActiveFpo(primaryFpo);
      setCrops(cropList);

      const [buyersData, reqsData] = await Promise.all([
        getBuyers({ fpo_id: primaryFpo?.id }, token ?? undefined),
        getBuyerRequirements({ fpo_id: primaryFpo?.id }, token ?? undefined),
      ]);

      setBuyers(buyersData.buyers);
      setRequirements(reqsData.requirements);
      if (buyersData.buyers.length > 0 && !reqForm.buyer_id) {
        setReqForm((prev) => ({ ...prev, buyer_id: buyersData.buyers[0].id }));
      }
      if (cropList.length > 0 && !reqForm.crop_id) {
        setReqForm((prev) => ({ ...prev, crop_id: cropList[0].id }));
      }
    } catch (err) {
      console.warn("Error loading buyers data:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateBuyer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!buyerForm.company_name.trim() || !buyerForm.contact_phone.trim()) {
      setErrorMsg(lang === "ta" ? "நிறுவன பெயர் மற்றும் தொலைபேசி தேவை." : "Company name and phone are required.");
      return;
    }
    setSubmitting(true);
    setErrorMsg(null);
    try {
      const token = await ensureToken();
      await createBuyer(
        {
          ...buyerForm,
          fpo_id: activeFpo?.id,
          verified: true,
        },
        token ?? undefined
      );
      setShowBuyerModal(false);
      setBuyerForm({
        company_name: "",
        buyer_type: "processor",
        contact_name: "",
        contact_phone: "",
        contact_email: "",
        location: "Erode",
        district: "Erode",
        gstin: "",
      });
      await loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to register buyer");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateRequirement = async (e: React.FormEvent) => {
    e.preventDefault();
    const qty = parseFloat(reqForm.quantity_kg);
    if (!reqForm.buyer_id || !reqForm.crop_id || isNaN(qty) || qty <= 0 || !reqForm.required_date) {
      setErrorMsg(lang === "ta" ? "அனைத்து முக்கிய புலங்களையும் நிரப்பவும்." : "Please fill in all mandatory fields.");
      return;
    }
    setSubmitting(true);
    setErrorMsg(null);
    try {
      const token = await ensureToken();
      await createBuyerRequirement(
        {
          buyer_id: reqForm.buyer_id,
          fpo_id: activeFpo?.id,
          crop_id: reqForm.crop_id,
          quantity_kg: qty,
          min_grade: reqForm.min_grade,
          required_date: reqForm.required_date,
          delivery_window_days: parseInt(reqForm.delivery_window_days) || 7,
          max_price_per_kg: reqForm.max_price_per_kg ? parseFloat(reqForm.max_price_per_kg) : undefined,
          delivery_location: reqForm.delivery_location || undefined,
          notes: reqForm.notes || undefined,
        },
        token ?? undefined
      );
      setShowReqModal(false);
      setReqForm({
        buyer_id: buyers[0]?.id || "",
        crop_id: crops[0]?.id || "",
        quantity_kg: "",
        min_grade: "A",
        required_date: "",
        delivery_window_days: "7",
        max_price_per_kg: "",
        delivery_location: "",
        notes: "",
      });
      await loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to post requirement");
    } finally {
      setSubmitting(false);
    }
  };

  // Filtered Buyers
  const filteredBuyers = buyers.filter((b) => {
    const matchesSearch =
      b.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (b.contact_name && b.contact_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      b.contact_phone.includes(searchTerm);
    const matchesType = typeFilter === "all" || b.buyer_type === typeFilter;
    return matchesSearch && matchesType;
  });

  // Filtered Requirements
  const filteredReqs = requirements.filter((r) => {
    const matchesSearch =
      (r.buyer_name && r.buyer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (r.crop_name && r.crop_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (r.delivery_location && r.delivery_location.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCrop = cropFilter === "all" || r.crop_id === cropFilter;
    return matchesSearch && matchesCrop;
  });

  const totalDemandTonnes = requirements
    .filter((r) => r.status === "open" || r.status === "partially_fulfilled")
    .reduce((acc, curr) => acc + (curr.quantity_kg - curr.fulfilled_quantity_kg), 0) / 1000;

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              {lang === "ta" ? "வணிகக் கொள்முதலாளர்கள் & தேவைகள்" : "Commercial Buyers & Demand"}
            </h1>
            <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/20">
              v0.8 Network
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "ஈரோடு பகுதி வணிக நிறுவனங்கள், மண்டி வர்த்தகர்கள் மற்றும் கொள்முதல் தேவைகள்."
              : "Manage verified commercial buyers, institutional processors, and forward demand orders."}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadData}
            disabled={isRefreshing}
            className="h-9 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setErrorMsg(null);
              setShowBuyerModal(true);
            }}
            className="h-9 text-xs"
          >
            <Building2 className="w-3.5 h-3.5 mr-1.5 text-primary" />
            {lang === "ta" ? "+ புதிய வாங்குபவர்" : "+ Register Buyer"}
          </Button>

          <Button
            size="sm"
            onClick={() => {
              setErrorMsg(null);
              setShowReqModal(true);
            }}
            className="h-9 text-xs bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            {lang === "ta" ? "+ கொள்முதல் தேவை" : "+ Post Requirement"}
          </Button>
        </div>
      </div>

      {/* KPI Highlight Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-card border-border shadow-xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "பதிவு செய்யப்பட்ட நிறுவனங்கள்" : "Registered Buyers"}
              </p>
              <h3 className="text-2xl font-bold mt-1 text-foreground">{buyers.length}</h3>
              <p className="text-[11px] text-emerald-600 mt-0.5">
                {buyers.filter((b) => b.verified).length} {lang === "ta" ? "சரிபார்க்கப்பட்டவை" : "verified entities"}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 flex items-center justify-center">
              <Building2 className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border shadow-xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "திறந்த கொள்முதல் தேவைகள்" : "Active Requirements"}
              </p>
              <h3 className="text-2xl font-bold mt-1 text-foreground">
                {requirements.filter((r) => r.status === "open").length}
              </h3>
              <p className="text-[11px] text-primary mt-0.5">
                {requirements.filter((r) => r.status === "partially_fulfilled").length} {lang === "ta" ? "பகுதியளவு நிறைவு" : "in progress"}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border shadow-xs">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                {lang === "ta" ? "மொத்த கொள்முதல் தேவை" : "Total Open Demand"}
              </p>
              <h3 className="text-2xl font-bold mt-1 text-foreground">
                {totalDemandTonnes.toFixed(1)} <span className="text-sm font-normal text-muted-foreground">T</span>
              </h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                {lang === "ta" ? "முன்னோடி ஒப்பந்தத் திறன்" : "Forward procurement scope"}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-border space-x-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab("buyers")}
          className={`pb-3 transition-colors relative flex items-center space-x-2 ${
            activeTab === "buyers"
              ? "text-primary font-semibold"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>{lang === "ta" ? "வணிக நிறுவனங்கள்" : "Commercial Buyers"}</span>
          <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
            {buyers.length}
          </span>
          {activeTab === "buyers" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>

        <button
          onClick={() => setActiveTab("requirements")}
          className={`pb-3 transition-colors relative flex items-center space-x-2 ${
            activeTab === "requirements"
              ? "text-primary font-semibold"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Package className="w-4 h-4" />
          <span>{lang === "ta" ? "கொள்முதல் தேவைப் பலகை" : "Procurement Demand Board"}</span>
          <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
            {requirements.length}
          </span>
          {activeTab === "requirements" && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={
              activeTab === "buyers"
                ? lang === "ta"
                  ? "நிறுவனம், தொடர்பு எண் அல்லது பெயர் மூலம் தேடவும்..."
                  : "Search company, contact person or phone..."
                : lang === "ta"
                ? "பயிர், நிறுவனம் அல்லது டெலிவரி இடம் மூலம் தேடவும்..."
                : "Search crop, buyer or location..."
            }
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-9 text-xs"
          />
        </div>

        {activeTab === "buyers" ? (
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="h-9 rounded-md border border-input bg-background px-3 py-1 text-xs shadow-xs text-foreground focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="all">{lang === "ta" ? "அனைத்து வகைகள்" : "All Buyer Types"}</option>
              <option value="processor">{lang === "ta" ? "செயலாக்கம் (Processor)" : "Processor"}</option>
              <option value="retailer">{lang === "ta" ? "சில்லறை (Retailer)" : "Retailer"}</option>
              <option value="trader">{lang === "ta" ? "வர்த்தகர் (Trader)" : "Trader"}</option>
              <option value="exporter">{lang === "ta" ? "ஏற்றுமதியாளர் (Exporter)" : "Exporter"}</option>
            </select>
          </div>
        ) : (
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <select
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
              className="h-9 rounded-md border border-input bg-background px-3 py-1 text-xs shadow-xs text-foreground focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="all">{lang === "ta" ? "அனைத்துப் பயிர்கள்" : "All Crops"}</option>
              {crops.map((c) => (
                <option key={c.id} value={c.id}>
                  {lang === "ta" && c.tamil_name ? c.tamil_name : c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-12 text-muted-foreground space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-xs">{lang === "ta" ? "தரவு ஏற்றப்படுகிறது..." : "Loading commercial buyers..."}</p>
        </div>
      ) : activeTab === "buyers" ? (
        /* Buyers Table */
        <Card className="border-border shadow-xs overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="text-xs font-semibold">{lang === "ta" ? "நிறுவன பெயர்" : "Company"}</TableHead>
                <TableHead className="text-xs font-semibold">{lang === "ta" ? "வகை" : "Type"}</TableHead>
                <TableHead className="text-xs font-semibold">{lang === "ta" ? "தொடர்பு விவரம்" : "Contact"}</TableHead>
                <TableHead className="text-xs font-semibold">{lang === "ta" ? "இருப்பிடம்" : "Location"}</TableHead>
                <TableHead className="text-xs font-semibold">{lang === "ta" ? "GSTIN / சான்று" : "GSTIN / Verification"}</TableHead>
                <TableHead className="text-xs font-semibold text-right">{lang === "ta" ? "தேவைகள்" : "Active Reqs"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBuyers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-xs text-muted-foreground">
                    {lang === "ta" ? "வாங்குபவர்கள் காணப்படவில்லை." : "No commercial buyers found."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredBuyers.map((b) => (
                  <TableRow key={b.id} className="hover:bg-muted/30">
                    <TableCell className="font-medium text-xs text-foreground">
                      <div className="flex items-center space-x-2">
                        <div className="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0">
                          {b.company_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-semibold">{b.company_name}</p>
                          <p className="text-[10px] text-muted-foreground">
                            {lang === "ta" ? "சேர்க்கப்பட்டது:" : "Added:"} {b.created_at ? new Date(b.created_at).toLocaleDateString() : "—"}
                          </p>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell>
                      <Badge variant="outline" className="text-[10px] capitalize">
                        {b.buyer_type}
                      </Badge>
                    </TableCell>

                    <TableCell className="text-xs">
                      <p className="font-medium">{b.contact_name || "—"}</p>
                      <p className="text-[11px] text-muted-foreground">{b.contact_phone}</p>
                    </TableCell>

                    <TableCell className="text-xs text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-muted-foreground/70 shrink-0" />
                        <span>{b.location}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground/70">({b.district || "TN"})</span>
                    </TableCell>

                    <TableCell className="text-xs">
                      <div className="flex items-center space-x-1.5">
                        {b.verified ? (
                          <Badge className="bg-emerald-500/10 text-emerald-700 hover:bg-emerald-500/20 text-[10px] border-emerald-500/20">
                            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                            {lang === "ta" ? "சரிபார்க்கப்பட்டது" : "Verified"}
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="text-[10px]">
                            {lang === "ta" ? "நிலுவையில்" : "Unverified"}
                          </Badge>
                        )}
                        {b.gstin && <span className="font-mono text-[10px] text-muted-foreground">{b.gstin}</span>}
                      </div>
                    </TableCell>

                    <TableCell className="text-right">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">
                        {b.open_requirements_count} {lang === "ta" ? "தேவைகள்" : "reqs"}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      ) : (
        /* Requirements Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredReqs.length === 0 ? (
            <div className="col-span-full text-center py-12 text-xs text-muted-foreground">
              {lang === "ta" ? "கொள்முதல் தேவைகள் எதுவும் இல்லை." : "No procurement requirements posted."}
            </div>
          ) : (
            filteredReqs.map((r) => {
              const pendingKg = Math.max(0, r.quantity_kg - r.fulfilled_quantity_kg);
              const progressPct = Math.min(100, Math.round((r.fulfilled_quantity_kg / r.quantity_kg) * 100));

              return (
                <Card key={r.id} className="border-border shadow-xs hover:border-primary/40 transition-all flex flex-col justify-between">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <Badge variant="outline" className="text-[10px] bg-primary/5 text-primary border-primary/20 mb-1.5">
                          {lang === "ta" && r.crop_tamil_name ? r.crop_tamil_name : r.crop_name}
                        </Badge>
                        <CardTitle className="text-base font-bold text-foreground">
                          {r.buyer_name || "Commercial Buyer"}
                        </CardTitle>
                      </div>
                      <Badge
                        variant={
                          r.status === "fulfilled"
                            ? "default"
                            : r.status === "partially_fulfilled"
                            ? "secondary"
                            : "outline"
                        }
                        className="text-[10px] capitalize"
                      >
                        {r.status.replace("_", " ")}
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="p-4 pt-1 space-y-3 text-xs">
                    {/* Quantity & Progress */}
                    <div>
                      <div className="flex justify-between text-muted-foreground text-[11px] mb-1">
                        <span>{lang === "ta" ? "தேவை அளவு:" : "Required:"} <strong>{r.quantity_kg.toLocaleString()} kg</strong></span>
                        <span>{progressPct}% {lang === "ta" ? "நிறைவு" : "fulfilled"}</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-primary h-1.5 rounded-full transition-all"
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>
                    </div>

                    {/* Metadata Grid */}
                    <div className="grid grid-cols-2 gap-2 text-[11px] bg-muted/40 p-2.5 rounded-lg border border-border/50">
                      <div>
                        <span className="text-muted-foreground">{lang === "ta" ? "குறைந்த தரம்:" : "Min Grade:"}</span>
                        <p className="font-semibold text-foreground">Grade {r.min_grade}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{lang === "ta" ? "அதிகபட்ச விலை:" : "Max Price:"}</span>
                        <p className="font-semibold text-emerald-600">
                          {r.max_price_per_kg ? `₹${r.max_price_per_kg}/kg` : "Open Mandi"}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{lang === "ta" ? "தேவையான தேதி:" : "Target Date:"}</span>
                        <p className="font-semibold text-foreground">{new Date(r.required_date).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{lang === "ta" ? "டெலிவரி இடம்:" : "Delivery Hub:"}</span>
                        <p className="font-semibold truncate text-foreground">{r.delivery_location || "Buyer Depot"}</p>
                      </div>
                    </div>

                    {r.notes && (
                      <p className="text-[11px] text-muted-foreground italic line-clamp-1">
                        "{r.notes}"
                      </p>
                    )}

                    {/* Action Link to Matching Engine */}
                    <div className="pt-2 border-t border-border">
                      <Link
                        href={`/matching?req_id=${r.id}`}
                        className="inline-flex items-center justify-center w-full py-1.5 px-3 rounded-md text-xs font-semibold bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                      >
                        <span>{lang === "ta" ? "பொருத்தமான விளைச்சலைத் தேடு" : "Find Matching Supply"}</span>
                        <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Modal 1: Register Buyer */}
      {/* --------------------------------------------------------------------- */}
      {showBuyerModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-card border border-border rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-primary" />
                <h3 className="font-bold text-base text-foreground">
                  {lang === "ta" ? "புதிய வணிகக் கொள்முதலாளர் பதிவு" : "Register Commercial Buyer"}
                </h3>
              </div>
              <button
                onClick={() => setShowBuyerModal(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateBuyer} className="p-4 space-y-3 text-xs">
              {errorMsg && (
                <div className="p-2.5 rounded-lg bg-destructive/10 text-destructive text-xs flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div>
                <label className="block font-medium text-foreground mb-1">
                  {lang === "ta" ? "நிறுவன பெயர் *" : "Company Name *"}
                </label>
                <Input
                  required
                  placeholder="e.g. ITC Spices Division / Aachi Masala"
                  value={buyerForm.company_name}
                  onChange={(e) => setBuyerForm({ ...buyerForm, company_name: e.target.value })}
                  className="h-8 text-xs"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "வணிக வகை *" : "Buyer Type *"}
                  </label>
                  <select
                    value={buyerForm.buyer_type}
                    onChange={(e) => setBuyerForm({ ...buyerForm, buyer_type: e.target.value })}
                    className="w-full h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground"
                  >
                    <option value="processor">Processor</option>
                    <option value="retailer">Retailer</option>
                    <option value="trader">Trader</option>
                    <option value="exporter">Exporter</option>
                    <option value="wholesaler">Wholesaler</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "தொடர்பு எண் (10 இலக்கம்) *" : "Phone Number *"}
                  </label>
                  <Input
                    required
                    maxLength={10}
                    placeholder="9842100001"
                    value={buyerForm.contact_phone}
                    onChange={(e) => setBuyerForm({ ...buyerForm, contact_phone: e.target.value })}
                    className="h-8 text-xs font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "தொடர்பு அலுவலர் பெயர்" : "Contact Person"}
                  </label>
                  <Input
                    placeholder="e.g. Senthil Kumar"
                    value={buyerForm.contact_name}
                    onChange={(e) => setBuyerForm({ ...buyerForm, contact_name: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "மின்னஞ்சல்" : "Email"}
                  </label>
                  <Input
                    type="email"
                    placeholder="procurement@company.com"
                    value={buyerForm.contact_email}
                    onChange={(e) => setBuyerForm({ ...buyerForm, contact_email: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "இருப்பிடம் / முகவரி" : "Location / Hub"}
                  </label>
                  <Input
                    placeholder="SIPCOT Perundurai"
                    value={buyerForm.location}
                    onChange={(e) => setBuyerForm({ ...buyerForm, location: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "GSTIN எண்" : "GSTIN (Optional)"}
                  </label>
                  <Input
                    placeholder="33AAACI1234A1Z1"
                    value={buyerForm.gstin}
                    onChange={(e) => setBuyerForm({ ...buyerForm, gstin: e.target.value })}
                    className="h-8 text-xs font-mono uppercase"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-border flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowBuyerModal(false)}
                  className="h-8 text-xs"
                >
                  {lang === "ta" ? "ரத்து செய்" : "Cancel"}
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={submitting}
                  className="h-8 text-xs bg-primary text-primary-foreground"
                >
                  {submitting && <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />}
                  {lang === "ta" ? "பதிவு செய்" : "Register Buyer"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Modal 2: Post Requirement */}
      {/* --------------------------------------------------------------------- */}
      {showReqModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-card border border-border rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center space-x-2">
                <Package className="w-5 h-5 text-primary" />
                <h3 className="font-bold text-base text-foreground">
                  {lang === "ta" ? "புதிய கொள்முதல் தேவை வெளியிடுதல்" : "Post Procurement Requirement"}
                </h3>
              </div>
              <button
                onClick={() => setShowReqModal(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateRequirement} className="p-4 space-y-3 text-xs">
              {errorMsg && (
                <div className="p-2.5 rounded-lg bg-destructive/10 text-destructive text-xs flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div>
                <label className="block font-medium text-foreground mb-1">
                  {lang === "ta" ? "வாங்கும் நிறுவனம் *" : "Buyer Entity *"}
                </label>
                <select
                  required
                  value={reqForm.buyer_id}
                  onChange={(e) => setReqForm({ ...reqForm, buyer_id: e.target.value })}
                  className="w-full h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground"
                >
                  {buyers.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.company_name} ({b.buyer_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "பயிர் *" : "Crop *"}
                  </label>
                  <select
                    required
                    value={reqForm.crop_id}
                    onChange={(e) => setReqForm({ ...reqForm, crop_id: e.target.value })}
                    className="w-full h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground"
                  >
                    {crops.map((c) => (
                      <option key={c.id} value={c.id}>
                        {lang === "ta" && c.tamil_name ? c.tamil_name : c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "தேவையான அளவு (கிலோ) *" : "Quantity (kg) *"}
                  </label>
                  <Input
                    required
                    type="number"
                    min="1"
                    placeholder="e.g. 5000"
                    value={reqForm.quantity_kg}
                    onChange={(e) => setReqForm({ ...reqForm, quantity_kg: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "குறைந்த தரம் *" : "Min Grade *"}
                  </label>
                  <select
                    value={reqForm.min_grade}
                    onChange={(e) => setReqForm({ ...reqForm, min_grade: e.target.value })}
                    className="w-full h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground"
                  >
                    <option value="A">Grade A (Export / Prime)</option>
                    <option value="B">Grade B (Processing)</option>
                    <option value="C">Grade C (Standard)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "அதிகபட்ச விலை (₹/கிலோ)" : "Max Price (₹/kg)"}
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="e.g. 145.00"
                    value={reqForm.max_price_per_kg}
                    onChange={(e) => setReqForm({ ...reqForm, max_price_per_kg: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "தேவையான தேதி *" : "Required Date *"}
                  </label>
                  <Input
                    required
                    type="date"
                    value={reqForm.required_date}
                    onChange={(e) => setReqForm({ ...reqForm, required_date: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">
                    {lang === "ta" ? "டெலிவரி சாளரம் (நாட்கள்)" : "Delivery Window (Days)"}
                  </label>
                  <Input
                    type="number"
                    min="1"
                    value={reqForm.delivery_window_days}
                    onChange={(e) => setReqForm({ ...reqForm, delivery_window_days: e.target.value })}
                    className="h-8 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">
                  {lang === "ta" ? "டெலிவரி மையம் / இருப்பிடம்" : "Delivery Location / Hub"}
                </label>
                <Input
                  placeholder="e.g. SIPCOT Perundurai / Erode Yard"
                  value={reqForm.delivery_location}
                  onChange={(e) => setReqForm({ ...reqForm, delivery_location: e.target.value })}
                  className="h-8 text-xs"
                />
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">
                  {lang === "ta" ? "குறிப்புகள் / தர விவரங்கள்" : "Quality Specs / Notes"}
                </label>
                <Input
                  placeholder="e.g. Moisture < 10%, finger variety only"
                  value={reqForm.notes}
                  onChange={(e) => setReqForm({ ...reqForm, notes: e.target.value })}
                  className="h-8 text-xs"
                />
              </div>

              <div className="pt-3 border-t border-border flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowReqModal(false)}
                  className="h-8 text-xs"
                >
                  {lang === "ta" ? "ரத்து செய்" : "Cancel"}
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={submitting}
                  className="h-8 text-xs bg-primary text-primary-foreground"
                >
                  {submitting && <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />}
                  {lang === "ta" ? "தேவையை வெளியிடு" : "Post Requirement"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
