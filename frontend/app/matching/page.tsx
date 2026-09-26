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
  GitCompare,
  Building2,
  Sprout,
  TrendingUp,
  Package,
  Calendar,
  MapPin,
  CheckCircle2,
  Clock,
  AlertCircle,
  RefreshCw,
  Loader2,
  ArrowRight,
  ArrowUpRight,
  ShieldCheck,
  Award,
  Layers,
  Sparkles,
  Search,
  Filter,
  Check,
  X,
  Phone,
} from "lucide-react";
import {
  getSupplyDemandSummary,
  getBuyerRequirements,
  getCandidatesForRequirement,
  suggestMatch,
  confirmMatch,
  rejectMatch,
  listSupplyMatches,
  getFPOs,
  getCrops,
  SupplyDemandSummary,
  BuyerRequirement,
  MatchCandidate,
  SupplyMatchItem,
  FPO,
  Crop,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

export default function MatchingPage() {
  const { lang } = useLanguage();
  const [activeTab, setActiveTab] = useState<"balance" | "matching" | "ledger">("balance");

  const [fpos, setFpos] = useState<FPO[]>([]);
  const [activeFpo, setActiveFpo] = useState<FPO | null>(null);
  const [crops, setCrops] = useState<Crop[]>([]);

  // Tab 1: Balance Summary State
  const [summary, setSummary] = useState<SupplyDemandSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  // Tab 2: Matching Engine State
  const [requirements, setRequirements] = useState<BuyerRequirement[]>([]);
  const [selectedReqId, setSelectedReqId] = useState<string>("");
  const [candidates, setCandidates] = useState<MatchCandidate[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [confirmedMatchIds, setConfirmedMatchIds] = useState<Record<string, string>>({});
  const [offeredPrices, setOfferedPrices] = useState<Record<string, string>>({});
  const [staffNotes, setStaffNotes] = useState<Record<string, string>>({});
  const [confirmingId, setConfirmingId] = useState<string | null>(null);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  // Tab 3: Confirmed Matches Ledger State
  const [ledgerMatches, setLedgerMatches] = useState<SupplyMatchItem[]>([]);
  const [loadingLedger, setLoadingLedger] = useState(false);

  const [isRefreshing, setIsRefreshing] = useState(false);

  // Check URL query for direct pre-selection (e.g., from /buyers?req_id=...)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const reqId = params.get("req_id");
      if (reqId) {
        setSelectedReqId(reqId);
        setActiveTab("matching");
      }
    }
  }, []);

  const loadInitialData = async () => {
    setIsRefreshing(true);
    try {
      const [token, fpoList, cropList] = await Promise.all([
        ensureToken(),
        getFPOs(),
        getCrops(),
      ]);
      setFpos(fpoList);
      setCrops(cropList);
      const primaryFpo = fpoList[0] || null;
      setActiveFpo(primaryFpo);

      // Load Balance Summary
      const summaryData = await getSupplyDemandSummary(
        { fpo_id: primaryFpo?.id },
        token ?? undefined
      );
      setSummary(summaryData);

      // Load Open Requirements
      const reqsData = await getBuyerRequirements(
        { fpo_id: primaryFpo?.id, status: "open" },
        token ?? undefined
      );
      setRequirements(reqsData.requirements);

      if (reqsData.requirements.length > 0 && !selectedReqId) {
        setSelectedReqId(reqsData.requirements[0].id);
      }
    } catch (err) {
      console.warn("Failed to load matching initial data:", err);
    } finally {
      setLoadingSummary(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // When selected requirement changes, fetch candidate matches
  useEffect(() => {
    if (!selectedReqId) {
      setCandidates([]);
      return;
    }

    const fetchCandidates = async () => {
      setLoadingCandidates(true);
      setActionSuccessMsg(null);
      try {
        const token = await ensureToken();
        const res = await getCandidatesForRequirement(selectedReqId, 15, token ?? undefined);
        if (res) {
          setCandidates(res.candidates);
          // Initialize offered price with req max price if present
          const req = requirements.find((r) => r.id === selectedReqId);
          const initialPrices: Record<string, string> = {};
          res.candidates.forEach((c) => {
            initialPrices[c.source_id] = req?.max_price_per_kg ? String(req.max_price_per_kg) : "";
          });
          setOfferedPrices(initialPrices);
        } else {
          setCandidates([]);
        }
      } catch (err) {
        console.warn("Error fetching matching candidates:", err);
        setCandidates([]);
      } finally {
        setLoadingCandidates(false);
      }
    };

    fetchCandidates();
  }, [selectedReqId, requirements]);

  // When ledger tab is activated, load confirmed matches
  const loadLedger = async () => {
    setLoadingLedger(true);
    try {
      const token = await ensureToken();
      const res = await listSupplyMatches(
        { fpo_id: activeFpo?.id },
        token ?? undefined
      );
      setLedgerMatches(res.matches);
    } catch (err) {
      console.warn("Failed to load match ledger:", err);
    } finally {
      setLoadingLedger(false);
    }
  };

  useEffect(() => {
    if (activeTab === "ledger") {
      loadLedger();
    }
  }, [activeTab, activeFpo]);

  // Handle 1-Click Staff Confirmation
  const handleConfirmMatch = async (candidate: MatchCandidate) => {
    if (!activeFpo || !selectedReqId) return;
    setConfirmingId(candidate.source_id);
    setActionSuccessMsg(null);

    try {
      const token = await ensureToken();
      const price = parseFloat(offeredPrices[candidate.source_id]) || undefined;
      const notes = staffNotes[candidate.source_id] || "Confirmed via Staff Matching Dashboard";

      // 1. Suggest Match
      const suggested = await suggestMatch(
        {
          buyer_requirement_id: selectedReqId,
          fpo_id: activeFpo.id,
          farm_id: candidate.candidate_type === "farm_plot" ? candidate.source_id : undefined,
          harvest_id: candidate.candidate_type === "harvest" ? candidate.source_id : undefined,
          matched_quantity_kg: candidate.available_quantity_kg,
          match_score: candidate.match_score,
          match_breakdown: candidate.match_breakdown,
          offered_price_per_kg: price,
          staff_notes: notes,
        },
        token ?? undefined
      );

      if (suggested) {
        // 2. Staff Confirm Match
        const confirmed = await confirmMatch(
          suggested.id,
          { staff_notes: notes, offered_price_per_kg: price },
          token ?? undefined
        );

        if (confirmed) {
          setConfirmedMatchIds((prev) => ({
            ...prev,
            [candidate.source_id]: confirmed.id,
          }));
          setActionSuccessMsg(
            lang === "ta"
              ? `ஒப்பந்தம் வெற்றிகரமாக உறுதிசெய்யப்பட்டது! (${candidate.farmer_name} • ${candidate.available_quantity_kg.toLocaleString()} kg)`
              : `Match confirmed successfully for ${candidate.farmer_name} (${candidate.available_quantity_kg.toLocaleString()} kg)!`
          );
        }
      }
    } catch (err: any) {
      console.error("Match confirmation error:", err);
      alert(err.message || "Failed to confirm match");
    } finally {
      setConfirmingId(null);
    }
  };

  const selectedRequirement = requirements.find((r) => r.id === selectedReqId);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight flex items-center gap-2">
            <GitCompare className="w-6 h-6 text-emerald-600" />
            <span>{lang === "ta" ? "விற்பனை & தேவை பொருத்துதல் மையம்" : "Supply & Demand Matching Console"}</span>
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "விவசாயிகளின் அறுவடை வரத்து மற்றும் நிறுவன கொள்முதல் தேவைகளை 5-காரணி அல்காரிதம் மூலம் பொருத்தி, FPO பணியாளர் ஒரு கிளிக்கில் உறுதி செய்யலாம்."
              : "Semi-automatic demand-supply matching engine: 5-factor scoring, candidate ranking, and 1-click staff confirmation."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={loadInitialData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
          <Link href="/buyers">
            <Button size="sm" variant="outline" className="h-8 text-xs gap-1.5 border-emerald-300 dark:border-emerald-800">
              <Building2 className="w-3.5 h-3.5 text-emerald-600" />
              {lang === "ta" ? "கொள்முதல் பலகை" : "Buyers & Demand"}
            </Button>
          </Link>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveTab("balance")}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center space-x-2 ${
            activeTab === "balance"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/40 dark:bg-emerald-950/20"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>{lang === "ta" ? "இருப்பு & தேவை நிலை" : "Supply & Demand Balance"}</span>
        </button>
        <button
          onClick={() => setActiveTab("matching")}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center space-x-2 ${
            activeTab === "matching"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/40 dark:bg-emerald-950/20"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>{lang === "ta" ? "பொருத்துதல் இயந்திரம்" : "Matching Engine"}</span>
          {requirements.length > 0 && (
            <Badge variant="secondary" className="ml-1 text-[11px] py-0 px-1.5">
              {requirements.length}
            </Badge>
          )}
        </button>
        <button
          onClick={() => setActiveTab("ledger")}
          className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center space-x-2 ${
            activeTab === "ledger"
              ? "border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-emerald-50/40 dark:bg-emerald-950/20"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>{lang === "ta" ? "உறுதிப்படுத்தப்பட்ட பதிவேடு" : "Execution Ledger"}</span>
        </button>
      </div>

      {/* ──────────────────────────────────────────────────────────── */}
      {/* TAB 1: SUPPLY & DEMAND BALANCE SHEET */}
      {/* ──────────────────────────────────────────────────────────── */}
      {activeTab === "balance" && (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-semibold uppercase">
                  <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                  {lang === "ta" ? "பயிரிடப்பட்ட நிலம்" : "Standing Acreage"}
                </span>
                <div className="text-2xl font-bold text-foreground">
                  {summary?.total_standing_acres?.toFixed(1) || "0.0"}{" "}
                  <span className="text-xs font-normal text-muted-foreground">{lang === "ta" ? "ஏக்கர்" : "acres"}</span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  {summary?.active_plots_total || 0} {lang === "ta" ? "தனி நிலங்கள் பதிவு" : "active farm plots"}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-semibold uppercase">
                  <Package className="w-3.5 h-3.5 text-emerald-600" />
                  {lang === "ta" ? "மொத்த இருப்பு (வரத்து)" : "Available Supply"}
                </span>
                <div className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                  {Math.round(summary?.total_supply_kg || 0).toLocaleString()}{" "}
                  <span className="text-xs font-normal text-muted-foreground">kg</span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  ~{((summary?.total_supply_kg || 0) / 100).toFixed(0)} {lang === "ta" ? "குவிண்டால்" : "quintals"}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-semibold uppercase">
                  <Building2 className="w-3.5 h-3.5 text-blue-600" />
                  {lang === "ta" ? "நிறுவன தேவை" : "Commercial Demand"}
                </span>
                <div className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                  {Math.round(summary?.total_demand_kg || 0).toLocaleString()}{" "}
                  <span className="text-xs font-normal text-muted-foreground">kg</span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  {summary?.open_requirements_total || 0} {lang === "ta" ? "திறந்த கொள்முதல் தேவைகள்" : "open requirements"}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 space-y-1">
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-semibold uppercase">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                  {lang === "ta" ? "நிகர இருப்பு நிலை" : "Net Position"}
                </span>
                {(() => {
                  const net = (summary?.total_supply_kg || 0) - (summary?.total_demand_kg || 0);
                  const isSurplus = net >= 0;
                  return (
                    <>
                      <div className={`text-2xl font-bold ${isSurplus ? "text-emerald-700 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"}`}>
                        {isSurplus ? "+" : ""}{Math.round(net).toLocaleString()}{" "}
                        <span className="text-xs font-normal text-muted-foreground">kg</span>
                      </div>
                      <Badge variant={isSurplus ? "success" : "warning"} className="text-[10px] py-0">
                        {isSurplus
                          ? lang === "ta" ? "உபரி இருப்பு (Surplus)" : "Net Surplus"
                          : lang === "ta" ? "தேவை அதிகம் (Deficit)" : "Net Deficit"}
                      </Badge>
                    </>
                  );
                })()}
              </CardContent>
            </Card>
          </div>

          {/* Commodity Breakdown Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">
                    {lang === "ta" ? "பயிர் வாரியான இருப்பு மற்றும் தேவை கணக்கீடு" : "Commodity Supply & Demand Balance Sheet"}
                  </CardTitle>
                  <CardDescription>
                    {lang === "ta"
                      ? "நிலத்தில் உள்ள பயிர்களின் கணிக்கப்பட்ட மகசூல், அறுவடை செய்யப்பட்ட சேமிப்பு மற்றும் பதிவு செய்யப்பட்ட தேவைகள்."
                      : "Standing plot yield estimates combined with verified harvest inventory vs institutional buyer orders."}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{lang === "ta" ? "பயிர்" : "Commodity"}</TableHead>
                    <TableHead>{lang === "ta" ? "பயிரிடப்பட்ட பரப்பளவு" : "Standing Acres"}</TableHead>
                    <TableHead>{lang === "ta" ? "நில மகசூல்" : "Field Yield (kg)"}</TableHead>
                    <TableHead>{lang === "ta" ? "அறுவடை சேமிப்பு" : "Harvest Stock (kg)"}</TableHead>
                    <TableHead>{lang === "ta" ? "மொத்த வரத்து" : "Total Supply (kg)"}</TableHead>
                    <TableHead>{lang === "ta" ? "வாங்குபவர் தேவை" : "Total Demand (kg)"}</TableHead>
                    <TableHead>{lang === "ta" ? "நிகர இருப்பு" : "Net Balance"}</TableHead>
                    <TableHead className="text-right">{lang === "ta" ? "நடவடிக்கை" : "Action"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loadingSummary ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                        <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                        {lang === "ta" ? "இருப்பு நிலை கணக்கிடப்படுகிறது..." : "Computing balance sheet..."}
                      </TableCell>
                    </TableRow>
                  ) : !summary || summary.commodities.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                        {lang === "ta" ? "பயிர் விவரங்கள் எதுவும் இல்லை." : "No commodity records found."}
                      </TableCell>
                    </TableRow>
                  ) : (
                    summary.commodities.map((item) => {
                      const isSurplus = item.net_balance_kg >= 0;
                      return (
                        <TableRow key={item.crop_id} className="hover:bg-muted/40 transition-colors">
                          <TableCell className="font-semibold text-foreground">
                            <div>{item.crop_name}</div>
                            {item.crop_tamil_name && (
                              <div className="text-xs text-muted-foreground font-normal">{item.crop_tamil_name}</div>
                            )}
                          </TableCell>
                          <TableCell>
                            <span className="font-medium">{item.standing_acres.toFixed(1)}</span>{" "}
                            <span className="text-xs text-muted-foreground">({item.active_plots_count} {lang === "ta" ? "நிலங்கள்" : "plots"})</span>
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {Math.round(item.standing_yield_kg).toLocaleString()} kg
                          </TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">
                            {Math.round(item.verified_harvest_kg).toLocaleString()} kg
                          </TableCell>
                          <TableCell className="font-bold text-emerald-700 dark:text-emerald-400 font-mono text-xs">
                            {Math.round(item.total_supply_kg).toLocaleString()} kg
                          </TableCell>
                          <TableCell className="font-bold text-blue-700 dark:text-blue-400 font-mono text-xs">
                            {Math.round(item.total_demand_kg).toLocaleString()} kg
                          </TableCell>
                          <TableCell>
                            <Badge variant={isSurplus ? "success" : "warning"} className="font-mono text-xs">
                              {isSurplus ? "+" : ""}{Math.round(item.net_balance_kg).toLocaleString()} kg
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs border-emerald-300 dark:border-emerald-800 hover:bg-emerald-50 text-emerald-800 dark:text-emerald-300 gap-1"
                              onClick={() => {
                                // Find requirement for this crop if any
                                const req = requirements.find((r) => r.crop_id === item.crop_id);
                                if (req) {
                                  setSelectedReqId(req.id);
                                }
                                setActiveTab("matching");
                              }}
                            >
                              <Sparkles className="w-3 h-3 text-emerald-600" />
                              <span>{lang === "ta" ? "பொருத்து" : "Match"}</span>
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
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────── */}
      {/* TAB 2: CANDIDATE RANKING & 1-CLICK CONFIRMATION */}
      {/* ──────────────────────────────────────────────────────────── */}
      {activeTab === "matching" && (
        <div className="space-y-6">
          {/* Requirement Selection Bar */}
          <Card className="border-emerald-200 dark:border-emerald-900 bg-muted/20">
            <CardContent className="p-4 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-emerald-600" />
                    <span>{lang === "ta" ? "கொள்முதல் தேவையைத் தேர்ந்தெடுக்கவும்:" : "Select Procurement Requirement:"}</span>
                  </label>
                  <select
                    className="w-full sm:w-[480px] h-10 rounded-md border border-input bg-background px-3 text-sm font-medium"
                    value={selectedReqId}
                    onChange={(e) => setSelectedReqId(e.target.value)}
                  >
                    {requirements.map((req) => (
                      <option key={req.id} value={req.id}>
                        {req.buyer_name || "Commercial Buyer"} — {req.crop_name} ({req.quantity_kg.toLocaleString()} kg by {req.required_date})
                      </option>
                    ))}
                  </select>
                </div>
                {selectedRequirement && (
                  <Badge variant="outline" className="h-7 text-xs bg-background">
                    <Clock className="w-3.5 h-3.5 mr-1 text-muted-foreground" />
                    {lang === "ta" ? "தேவை தேதி:" : "Target Date:"} {selectedRequirement.required_date}
                  </Badge>
                )}
              </div>

              {/* Requirement Details Summary Strip */}
              {selectedRequirement && (
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 border-t text-xs">
                  <div>
                    <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                      {lang === "ta" ? "நிறுவனம்" : "Buyer"}
                    </span>
                    <span className="font-bold text-foreground">{selectedRequirement.buyer_name || "Buyer"}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                      {lang === "ta" ? "தேவைப்படும் அளவு" : "Target Qty"}
                    </span>
                    <span className="font-bold text-blue-700 dark:text-blue-400">
                      {selectedRequirement.quantity_kg.toLocaleString()} kg
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                      {lang === "ta" ? "தரம் (Grade)" : "Minimum Grade"}
                    </span>
                    <Badge variant="outline" className="text-[10px] font-bold">
                      Grade {selectedRequirement.min_grade}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                      {lang === "ta" ? "அதிகபட்ச விலை" : "Target Budget"}
                    </span>
                    <span className="font-bold text-foreground">
                      {selectedRequirement.max_price_per_kg ? `₹${selectedRequirement.max_price_per_kg}/kg` : "Open Mandi Rate"}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                      {lang === "ta" ? "டெலிவரி இடம்" : "Delivery"}
                    </span>
                    <span className="text-foreground">{selectedRequirement.delivery_location || "FPO Hub"}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Action Success Alert Banner */}
          {actionSuccessMsg && (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-lg p-3 text-xs text-emerald-900 dark:text-emerald-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="font-semibold">{actionSuccessMsg}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-emerald-800 dark:text-emerald-300 hover:bg-emerald-100 p-1"
                onClick={() => setActiveTab("ledger")}
              >
                <span>{lang === "ta" ? "பதிவேட்டில் காண்க" : "View in Ledger"}</span>
                <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          )}

          {/* Ranked Candidate List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <span>{lang === "ta" ? "தரவரிசைப்படுத்தப்பட்ட வரத்து வாய்ப்புகள்" : "Ranked Supply Candidates"}</span>
              </h3>
              <Badge variant="secondary">
                {candidates.length} {lang === "ta" ? "பொருத்தங்கள் கிடைத்துள்ளன" : "candidates identified"}
              </Badge>
            </div>

            {loadingCandidates ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground text-sm space-y-2">
                <Loader2 className="w-6 h-6 animate-spin text-emerald-600" />
                <p>{lang === "ta" ? "பொருத்தங்கள் கணக்கிடப்படுகின்றன..." : "Calculating 5-factor candidate scores..."}</p>
              </div>
            ) : candidates.length === 0 ? (
              <div className="text-center py-16 px-4 border border-dashed rounded-xl bg-muted/20">
                <Layers className="w-10 h-10 text-muted-foreground mx-auto mb-2 opacity-50" />
                <p className="font-medium text-foreground text-sm">
                  {lang === "ta" ? "தற்போது பொருத்தமான வரத்து இல்லை" : "No matching supply candidates available"}
                </p>
                <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                  {lang === "ta"
                    ? "இந்த பயிர்க்கான புதிய நிலங்கள் அல்லது அறுவடை வரத்துகளை பதிவு செய்யவும்."
                    : "Add new standing plots in Farmers or verify harvest batches to match this requirement."}
                </p>
              </div>
            ) : (
              candidates.map((cand, idx) => {
                const isConfirmed = Boolean(confirmedMatchIds[cand.source_id]);
                const score = Math.round(cand.match_score);
                const scoreColor =
                  score >= 80
                    ? "bg-emerald-500"
                    : score >= 60
                    ? "bg-blue-500"
                    : "bg-amber-500";

                const scoreBadgeVariant =
                  score >= 80 ? "success" : score >= 60 ? "default" : "warning";

                return (
                  <Card
                    key={cand.source_id}
                    className={`border transition-all ${
                      isConfirmed
                        ? "border-emerald-500 bg-emerald-50/20 dark:bg-emerald-950/10"
                        : "hover:border-emerald-300 dark:hover:border-emerald-800"
                    }`}
                  >
                    <CardContent className="p-4 sm:p-5 space-y-4">
                      {/* Top Candidate Row */}
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 font-bold text-xs flex items-center justify-center">
                              #{idx + 1}
                            </span>
                            <h4 className="font-bold text-foreground text-base">
                              {cand.farmer_name}
                            </h4>
                            <Badge
                              variant={cand.candidate_type === "farm_plot" ? "outline" : "secondary"}
                              className="text-[10px] capitalize"
                            >
                              {cand.candidate_type === "farm_plot"
                                ? lang === "ta" ? "நில பயிர் வரத்து" : "Standing Plot"
                                : lang === "ta" ? "அறுவடை இருப்பு" : "Harvested Stock"}
                            </Badge>
                            {cand.farmer_alerts_opt_in && (
                              <Badge variant="success" className="text-[10px] gap-1">
                                <Phone className="w-2.5 h-2.5" />
                                <span>WhatsApp</span>
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground flex items-center space-x-3">
                            <span>
                              <MapPin className="w-3 h-3 inline mr-1 text-muted-foreground" />
                              {cand.village || "Erode"}
                            </span>
                            <span>•</span>
                            <span className="font-mono text-xs">
                              {cand.farmer_phone ? cand.farmer_phone.replace(/(\+?\d{2,5}\s?\d{3})\d{4}/, "$1••••") : "—"}
                            </span>
                          </p>
                        </div>

                        {/* Composite Match Score Gauge */}
                        <div className="flex items-center space-x-3 bg-muted/40 p-2 rounded-xl">
                          <div className="text-right">
                            <span className="text-[10px] uppercase font-bold text-muted-foreground block">
                              {lang === "ta" ? "பொருத்த மதிப்பெண்" : "Match Score"}
                            </span>
                            <span className="text-lg font-bold text-foreground">{score}%</span>
                          </div>
                          <div className="w-12 h-2.5 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                            <div className={`h-full ${scoreColor}`} style={{ width: `${score}%` }} />
                          </div>
                          <Badge variant={scoreBadgeVariant} className="text-xs font-bold">
                            {score >= 80 ? "High" : score >= 60 ? "Med" : "Fair"}
                          </Badge>
                        </div>
                      </div>

                      {/* 5-Factor Score Radar Pills */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs bg-muted/30 p-3 rounded-lg">
                        <div>
                          <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                            {lang === "ta" ? "கிடைக்கும் அளவு" : "Supply Available"}
                          </span>
                          <span className="font-bold text-foreground">
                            {Math.round(cand.available_quantity_kg).toLocaleString()} kg
                          </span>
                          <span className="text-[10px] text-muted-foreground block">
                            Fit: {Math.round(cand.match_breakdown.quantity_fit_ratio || 0)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                            {lang === "ta" ? "தொலைவு (Distance)" : "Proximity"}
                          </span>
                          <span className="font-medium text-foreground">
                            {cand.match_breakdown.distance_km != null ? `~${cand.match_breakdown.distance_km.toFixed(1)} km` : "Local"}
                          </span>
                          <span className="text-[10px] text-muted-foreground block">
                            Score: {Math.round(cand.match_breakdown.proximity_score || 0)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                            {lang === "ta" ? "கால பொருத்தம்" : "Timing Fit"}
                          </span>
                          <span className="font-medium text-foreground">
                            {cand.available_date || "Ready"}
                          </span>
                          <span className="text-[10px] text-muted-foreground block">
                            Δ {cand.match_breakdown.timing_days_delta || 0} days
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                            {lang === "ta" ? "தரம் (Grade Fit)" : "Grade Fit"}
                          </span>
                          <span className="font-medium text-foreground">
                            {cand.grade || "Grade A"}
                          </span>
                          <span className="text-[10px] text-muted-foreground block">
                            Score: {Math.round(cand.match_breakdown.grade_score || 0)}%
                          </span>
                        </div>
                      </div>

                      {/* Staff Confirmation Controls */}
                      <div className="pt-1 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-t">
                        <div className="flex items-center space-x-2 flex-1">
                          <div className="w-32">
                            <Input
                              type="number"
                              step="0.5"
                              placeholder="Price ₹/kg"
                              className="h-8 text-xs font-mono"
                              value={offeredPrices[cand.source_id] || ""}
                              onChange={(e) =>
                                setOfferedPrices((prev) => ({
                                  ...prev,
                                  [cand.source_id]: e.target.value,
                                }))
                              }
                              disabled={isConfirmed}
                            />
                          </div>
                          <div className="flex-1">
                            <Input
                              placeholder={lang === "ta" ? "பணியாளர் குறிப்புகள்..." : "Staff negotiation notes..."}
                              className="h-8 text-xs"
                              value={staffNotes[cand.source_id] || ""}
                              onChange={(e) =>
                                setStaffNotes((prev) => ({
                                  ...prev,
                                  [cand.source_id]: e.target.value,
                                }))
                              }
                              disabled={isConfirmed}
                            />
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          {isConfirmed ? (
                            <Badge variant="success" className="h-8 px-3 text-xs gap-1 font-bold">
                              <Check className="w-3.5 h-3.5" />
                              <span>{lang === "ta" ? "ஒப்பந்தம் உறுதி செய்யப்பட்டது" : "Match Confirmed"}</span>
                            </Badge>
                          ) : (
                            <Button
                              size="sm"
                              className="h-8 text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-semibold gap-1.5"
                              onClick={() => handleConfirmMatch(cand)}
                              disabled={confirmingId === cand.source_id}
                            >
                              {confirmingId === cand.source_id ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <Check className="w-3.5 h-3.5" />
                              )}
                              <span>{lang === "ta" ? "1-கிளிக் உறுதி செய்" : "Confirm Match"}</span>
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────── */}
      {/* TAB 3: CONFIRMED MATCHES EXECUTION LEDGER */}
      {/* ──────────────────────────────────────────────────────────── */}
      {activeTab === "ledger" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">
                  {lang === "ta" ? "உறுதிப்படுத்தப்பட்ட கொள்முதல் ஒப்பந்தங்கள்" : "Confirmed Match Execution Ledger"}
                </CardTitle>
                <CardDescription>
                  {lang === "ta"
                    ? "FPO ஊழியர்களால் உறுதி செய்யப்பட்ட தேவை-வரத்து ஒப்பந்தங்கள் மற்றும் விவசாயி வாட்ஸ்அப் அறிவிப்பு நிலை."
                    : "Audited ledger of staff-confirmed demand-supply commitments, agreed prices, and farmer WhatsApp alerts."}
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                onClick={loadLedger}
                disabled={loadingLedger}
              >
                <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${loadingLedger ? "animate-spin" : ""}`} />
                {lang === "ta" ? "புதுப்பி" : "Refresh"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{lang === "ta" ? "நிறுவனம் / வாங்குபவர்" : "Buyer"}</TableHead>
                  <TableHead>{lang === "ta" ? "விவசாயி / நிலம்" : "Farmer & Village"}</TableHead>
                  <TableHead>{lang === "ta" ? "பயிர்" : "Crop"}</TableHead>
                  <TableHead>{lang === "ta" ? "ஒப்பந்த அளவு" : "Matched Qty"}</TableHead>
                  <TableHead>{lang === "ta" ? "விலை (₹/kg)" : "Agreed Price"}</TableHead>
                  <TableHead>{lang === "ta" ? "மதிப்பு" : "Deal Value"}</TableHead>
                  <TableHead>{lang === "ta" ? "நிலை" : "Status"}</TableHead>
                  <TableHead>{lang === "ta" ? "உறுதிசெய்த தேதி" : "Confirmed At"}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loadingLedger ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                      <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                      {lang === "ta" ? "ஒப்பந்த பதிவேடு ஏற்றப்படுகிறது..." : "Loading ledger..."}
                    </TableCell>
                  </TableRow>
                ) : ledgerMatches.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                      {lang === "ta"
                        ? "இன்னும் ஒப்பந்தங்கள் உறுதி செய்யப்படவில்லை. 'பொருத்துதல் இயந்திரம்' மூலம் பொருத்தங்களை உறுதி செய்யலாம்."
                        : "No confirmed matches yet. Select a requirement in 'Matching Engine' and confirm candidates."}
                    </TableCell>
                  </TableRow>
                ) : (
                  ledgerMatches.map((m) => {
                    const price = m.offered_price_per_kg || 0;
                    const totalVal = Math.round(m.matched_quantity_kg * price);

                    return (
                      <TableRow key={m.id} className="hover:bg-muted/40 transition-colors">
                        <TableCell className="font-semibold text-foreground">
                          {m.buyer_name || "Buyer"}
                        </TableCell>
                        <TableCell>
                          <div className="font-medium text-foreground">{m.farmer_name || "Farmer"}</div>
                          {m.farmer_phone && (
                            <div className="text-xs text-muted-foreground font-mono">
                              {m.farmer_phone.replace(/(\+?\d{2,5}\s?\d{3})\d{4}/, "$1••••")}
                            </div>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">
                            {m.crop_name || "Crop"}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs font-bold text-foreground">
                          {Math.round(m.matched_quantity_kg).toLocaleString()} kg
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {price > 0 ? `₹${price}/kg` : "Mandi Rate"}
                        </TableCell>
                        <TableCell className="font-mono text-xs font-bold text-emerald-700 dark:text-emerald-400">
                          {totalVal > 0 ? `₹${totalVal.toLocaleString()}` : "—"}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              m.status === "confirmed_by_staff" || m.status === "fulfilled"
                                ? "success"
                                : m.status === "notified_farmer"
                                ? "default"
                                : "secondary"
                            }
                            className="text-[10px] capitalize"
                          >
                            {m.status.replace(/_/g, " ")}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {m.confirmed_at ? new Date(m.confirmed_at).toLocaleDateString() : "—"}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
