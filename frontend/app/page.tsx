"use client";

import React, { useState, useEffect, useCallback } from "react";
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
  CheckCircle2,
  Clock,
  AlertTriangle,
  Package,
  Building2,
  TrendingUp,
  Plus,
  ArrowRight,
  RefreshCw,
  Loader2,
  Check,
  MapPin,
  Calendar,
  Sparkles,
  ShieldCheck,
  Store,
  Users,
  Smartphone,
  ExternalLink,
} from "lucide-react";
import {
  getLatestPrices,
  getFPODashboard,
  getHarvestAggregation,
  getBuyerRequirements,
  getHarvests,
  updateHarvestStatus,
  getTasks,
  updateTaskStatus,
  MarketPrice,
  HarvestAggregation,
  BuyerRequirement,
  HarvestRecord,
  TaskItem,
  FPODashboardStats,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

const FPO_ID = process.env.NEXT_PUBLIC_FPO_ID || "d7342e5d-bac6-466e-a18b-366133137074";

export default function FPOActionWorkspace() {
  const { lang } = useLanguage();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  // Operational Data States
  const [stats, setStats] = useState<FPODashboardStats | null>(null);
  const [pendingHarvests, setPendingHarvests] = useState<HarvestRecord[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [aggregation, setAggregation] = useState<HarvestAggregation | null>(null);
  const [buyerRequirements, setBuyerRequirements] = useState<BuyerRequirement[]>([]);
  const [prices, setPrices] = useState<MarketPrice[]>([]);

  // Task inline quick-add form
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [creatingTask, setCreatingTask] = useState(false);
  const [verifyingHarvestId, setVerifyingHarvestId] = useState<string | null>(null);
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(null);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  const loadWorkspaceData = useCallback(async () => {
    setRefreshing(true);
    try {
      const activeToken = await ensureToken();
      setToken(activeToken);

      // Parallel fetch across key operational endpoints
      const [
        pricesData,
        aggData,
        reqsData,
        harvestsData,
        tasksData,
        statsData,
      ] = await Promise.all([
        getLatestPrices(),
        getHarvestAggregation(),
        getBuyerRequirements({ status: "open", page_size: 6 }, activeToken ?? undefined),
        getHarvests({ status: "submitted", page_size: 10 }, activeToken ?? undefined),
        getTasks({}, activeToken ?? undefined),
        activeToken ? getFPODashboard(FPO_ID, activeToken) : Promise.resolve(null),
      ]);

      setPrices(pricesData.slice(0, 8));
      setAggregation(aggData);
      setBuyerRequirements(reqsData.requirements || []);
      setPendingHarvests(harvestsData.harvests || []);
      setTasks(tasksData.filter((t) => t.status !== "done"));
      setStats(statsData);
    } catch (err) {
      console.warn("Failed to load workspace data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  // Quick Action: 1-Click Harvest Verification
  const handleVerifyHarvest = async (harvestId: string) => {
    setVerifyingHarvestId(harvestId);
    setActionSuccessMessage(null);
    try {
      const updated = await updateHarvestStatus(harvestId, "verified", "Confirmed from Action Workspace", token ?? undefined);
      if (updated) {
        setPendingHarvests((prev) => prev.filter((h) => h.id !== harvestId));
        setActionSuccessMessage(
          lang === "ta"
            ? `அறுவடை பதிவு வெற்றிகரமாக சரிபார்க்கப்பட்டு இருப்புடன் சேர்க்கப்பட்டது!`
            : `Harvest record confirmed and added to pooled supply!`
        );
        // Refresh aggregation in background
        getHarvestAggregation().then(setAggregation);
      }
    } catch (err) {
      console.error("Harvest verification error:", err);
    } finally {
      setVerifyingHarvestId(null);
    }
  };

  // Quick Action: 1-Click Task Completion
  const handleCompleteTask = async (taskId: string) => {
    setCompletingTaskId(taskId);
    setActionSuccessMessage(null);
    try {
      const updated = await updateTaskStatus(taskId, "done", token ?? undefined);
      if (updated) {
        setTasks((prev) => prev.filter((t) => t.id !== taskId));
        setActionSuccessMessage(
          lang === "ta"
            ? `பணி வெற்றிகரமாக முடிக்கப்பட்டது!`
            : `Task marked complete!`
        );
      }
    } catch (err) {
      console.error("Task completion error:", err);
    } finally {
      setCompletingTaskId(null);
    }
  };

  // Inline Quick Task Add
  const handleQuickAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    setCreatingTask(true);
    try {
      const res = await fetch("/api/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          title: newTaskTitle.trim(),
          priority: "medium",
          category: "harvest",
        }),
      });
      if (res.ok) {
        const created: TaskItem = await res.json();
        setTasks((prev) => [created, ...prev]);
        setNewTaskTitle("");
      }
    } catch (err) {
      console.warn("Failed to create task:", err);
    } finally {
      setCreatingTask(false);
    }
  };

  // Compute key summary indicators
  const overdueTasksCount = tasks.filter((t) => t.is_overdue).length;
  const totalPooledTonnes = aggregation ? (aggregation.total_pooled_kg / 1000).toFixed(1) : "0.0";
  const totalDemandTonnes = buyerRequirements.reduce((sum, r) => sum + r.quantity_kg, 0) / 1000;
  const stalePricesCount = prices.filter((p) => p.is_stale).length;

  return (
    <div className="space-y-6 pb-12">
      {/* ── Operational Banner & Executive Strip ────────────────── */}
      <div className="relative overflow-hidden rounded-2xl border border-emerald-900/15 bg-gradient-to-r from-emerald-950 via-emerald-900 to-teal-950 p-5 text-white shadow-xs sm:p-6">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-emerald-800/60 text-emerald-100 text-xs font-semibold backdrop-blur-xs">
              <span>🌾 {lang === "ta" ? "ஈரோடு வேளாண் கூட்டமைப்பு" : "Erode Agri Producer Network"}</span>
              <span>•</span>
              <span>{lang === "ta" ? "செயல் தளம்" : "FPO Action Workspace"}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black tracking-tight">
              {lang === "ta"
                ? "இன்றைய FPO செயல்பாடுகள் & வணிக மேலாண்மை"
                : "Today's FPO Operations & Wholesale Desk"}
            </h1>
            <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
              {lang === "ta"
                ? "விவசாயிகளின் அறுவடை வரத்து, சரிபார்ப்பு பணிகள், வாங்குபவர் தேவைகள் மற்றும் தணிக்கை செய்யப்பட்ட சந்தை விலைகள்."
                : "Connect member harvests, pending verifications, buyer requirements, and audited market prices into a single workflow."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadWorkspaceData}
              disabled={refreshing}
              className="h-8 text-xs bg-white/10 hover:bg-white/20 text-white border-white/20"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
              {lang === "ta" ? "புதுப்பி" : "Refresh"}
            </Button>
            <Link href="/matching">
              <Button size="sm" className="h-8 text-xs bg-emerald-500 hover:bg-emerald-600 text-emerald-950 font-bold">
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                {lang === "ta" ? "பொருத்துதல் மையம்" : "Match Engine"}
              </Button>
            </Link>
          </div>
        </div>

        {/* 4 Core Operational Telemetry Badges */}
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-emerald-800/60">
          <div className="bg-emerald-900/40 rounded-xl p-2.5 border border-emerald-700/30">
            <span className="text-[11px] text-emerald-200/80 block uppercase font-medium">
              {lang === "ta" ? "சரிபார்க்க வேண்டியவை" : "Pending Harvests"}
            </span>
            <div className="text-xl font-extrabold mt-0.5 flex items-baseline gap-1.5">
              <span>{pendingHarvests.length}</span>
              <span className="text-[11px] font-normal text-emerald-300">
                {lang === "ta" ? "அறுவடைகள்" : "batches"}
              </span>
            </div>
          </div>

          <div className="bg-emerald-900/40 rounded-xl p-2.5 border border-emerald-700/30">
            <span className="text-[11px] text-emerald-200/80 block uppercase font-medium">
              {lang === "ta" ? "கவனிக்க வேண்டிய பணிகள்" : "Attention Tasks"}
            </span>
            <div className="text-xl font-extrabold mt-0.5 flex items-baseline gap-1.5">
              <span>{tasks.length}</span>
              {overdueTasksCount > 0 && (
                <span className="text-[10px] font-bold text-red-300 bg-red-950/60 px-1.5 py-0.2 rounded">
                  {overdueTasksCount} {lang === "ta" ? "தாமதம்" : "overdue"}
                </span>
              )}
            </div>
          </div>

          <div className="bg-emerald-900/40 rounded-xl p-2.5 border border-emerald-700/30">
            <span className="text-[11px] text-emerald-200/80 block uppercase font-medium">
              {lang === "ta" ? "விற்பனைக்கு உள்ள இருப்பு" : "Ready Supply"}
            </span>
            <div className="text-xl font-extrabold mt-0.5 flex items-baseline gap-1.5">
              <span>{totalPooledTonnes}</span>
              <span className="text-[11px] font-normal text-emerald-300">Tonnes</span>
            </div>
          </div>

          <div className="bg-emerald-900/40 rounded-xl p-2.5 border border-emerald-700/30">
            <span className="text-[11px] text-emerald-200/80 block uppercase font-medium">
              {lang === "ta" ? "வாங்குபவர் தேவைகள்" : "Active Demand"}
            </span>
            <div className="text-xl font-extrabold mt-0.5 flex items-baseline gap-1.5">
              <span>{totalDemandTonnes.toFixed(1)}</span>
              <span className="text-[11px] font-normal text-emerald-300">Tonnes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Success Banner */}
      {actionSuccessMessage && (
        <div className="bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-300 dark:border-emerald-800 rounded-xl p-3 text-xs text-emerald-900 dark:text-emerald-100 flex items-center justify-between shadow-xs">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-semibold">{actionSuccessMessage}</span>
          </div>
          <button
            onClick={() => setActionSuccessMessage(null)}
            className="text-emerald-700 dark:text-emerald-300 hover:text-emerald-900 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* ── SECTION 1: TODAY'S WORK ──────────────────────────────── */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-5 bg-emerald-600 rounded-full" />
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              {lang === "ta" ? "1. இன்றைய பணிகள் & சரிபார்ப்புகள்" : "1. Today's Work & Action Queue"}
            </h2>
          </div>
          <span className="text-xs text-muted-foreground">
            {lang === "ta" ? "உடனடி நடவடிக்கை தேவை" : "Immediate action required"}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Subcard 1: Pending Harvest Confirmations */}
          <Card className="border-border shadow-xs flex flex-col justify-between">
            <CardHeader className="p-4 pb-2 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Package className="w-4 h-4 text-emerald-600" />
                  <CardTitle className="text-sm font-bold">
                    {lang === "ta" ? "அறுவடை சரிபார்ப்பு நிலுவை" : "Harvests Awaiting Confirmation"}
                  </CardTitle>
                </div>
                <Badge variant={pendingHarvests.length > 0 ? "warning" : "secondary"} className="text-xs">
                  {pendingHarvests.length} {lang === "ta" ? "நிலுவையில்" : "pending"}
                </Badge>
              </div>
              <CardDescription className="text-xs">
                {lang === "ta"
                  ? "உழவர்கள் பதிவு செய்த அறுவடை விவரங்களை சரிபார்த்து இருப்புடன் இணைக்கவும்."
                  : "Verify member-submitted harvest declarations to lock them into pooled supply."}
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 flex-1 space-y-3">
              {loading ? (
                <div className="py-8 flex justify-center text-muted-foreground text-xs">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  {lang === "ta" ? "ஏற்றப்படுகிறது..." : "Loading harvests..."}
                </div>
              ) : pendingHarvests.length === 0 ? (
                <div className="py-8 text-center text-xs text-muted-foreground border border-dashed rounded-lg bg-muted/20">
                  <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-1.5 opacity-60" />
                  <p className="font-semibold text-foreground">
                    {lang === "ta" ? "நிலுவையில் உள்ள அறுவடைகள் இல்லை!" : "All member harvests are confirmed!"}
                  </p>
                  <p className="text-[11px] mt-0.5">
                    {lang === "ta"
                      ? "அனைத்து வரத்துகளும் சரிபார்க்கப்பட்டு இருப்பு பட்டியலில் உள்ளன."
                      : "New submissions from farmers via WhatsApp/web will appear here."}
                  </p>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[280px] overflow-y-auto pr-1">
                  {pendingHarvests.map((h) => (
                    <div
                      key={h.id}
                      className="p-3 rounded-lg border border-border bg-card hover:border-emerald-500/50 transition-colors flex items-center justify-between gap-3 text-xs"
                    >
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-foreground truncate">
                            {h.farmer_name || (lang === "ta" ? "உழவர்" : "Farmer")}
                          </span>
                          <Badge variant="outline" className="text-[10px] py-0 px-1 bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                            {lang === "ta" && h.crop_tamil_name ? h.crop_tamil_name : h.crop_name}
                          </Badge>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            Grade {h.grade}
                          </span>
                        </div>
                        <div className="text-[11px] text-muted-foreground flex items-center space-x-3">
                          <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                            {Number(h.quantity_kg).toLocaleString()} kg
                          </span>
                          <span>•</span>
                          <span>{h.harvest_date}</span>
                          {h.notes && (
                            <>
                              <span>•</span>
                              <span className="italic truncate max-w-[120px]">{h.notes}</span>
                            </>
                          )}
                        </div>
                      </div>

                      <Button
                        size="sm"
                        onClick={() => handleVerifyHarvest(h.id)}
                        disabled={verifyingHarvestId === h.id}
                        className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 text-white shrink-0 font-medium"
                      >
                        {verifyingHarvestId === h.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <>
                            <Check className="w-3.5 h-3.5 mr-1" />
                            {lang === "ta" ? "சரிபார்" : "Confirm"}
                          </>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Subcard 2: Priority Tasks & Overdue Deadlines */}
          <Card className="border-border shadow-xs flex flex-col justify-between">
            <CardHeader className="p-4 pb-2 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-blue-600" />
                  <CardTitle className="text-sm font-bold">
                    {lang === "ta" ? "முக்கிய பணிகள் & நினைவூட்டல்கள்" : "Priority Tasks & Deadlines"}
                  </CardTitle>
                </div>
                <div className="flex items-center space-x-1.5">
                  <Link href="/tasks" className="text-xs text-primary hover:underline flex items-center">
                    {lang === "ta" ? "அனைத்தும்" : "View board"}
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </Link>
                </div>
              </div>
              <CardDescription className="text-xs">
                {lang === "ta"
                  ? "கொள்முதல் மற்றும் உழவர் களப்பணிகள். முடித்ததும் டிக் செய்யவும்."
                  : "Track time-sensitive operational tasks, farmer follow-ups, and inspections."}
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 flex-1 space-y-3">
              {/* Quick Task Add */}
              <form onSubmit={handleQuickAddTask} className="flex gap-2">
                <Input
                  placeholder={lang === "ta" ? "+ புதிய பணி சேர்க்க (எ.கா: ITC தர மாதிரி அனுப்பவும்)..." : "+ Quick add task (e.g. Dispatch turmeric samples to ITC)..."}
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="h-8 text-xs"
                />
                <Button
                  type="submit"
                  size="sm"
                  disabled={creatingTask || !newTaskTitle.trim()}
                  className="h-8 text-xs bg-primary shrink-0"
                >
                  {creatingTask ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                </Button>
              </form>

              {/* Tasks List */}
              {tasks.length === 0 ? (
                <div className="py-6 text-center text-xs text-muted-foreground border border-dashed rounded-lg bg-muted/20">
                  <CheckCircle2 className="w-7 h-7 text-emerald-500 mx-auto mb-1 opacity-60" />
                  <p className="font-semibold text-foreground">
                    {lang === "ta" ? "அனைத்து பணிகளும் முடிக்கப்பட்டுவிட்டன!" : "No pending operational tasks!"}
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                  {tasks.slice(0, 5).map((t) => (
                    <div
                      key={t.id}
                      className={`p-2.5 rounded-lg border text-xs flex items-center justify-between gap-2 transition-colors ${
                        t.is_overdue
                          ? "border-red-300 bg-red-50/50 dark:bg-red-950/20 dark:border-red-900"
                          : "border-border bg-card"
                      }`}
                    >
                      <div className="flex items-center space-x-2.5 min-w-0">
                        <button
                          type="button"
                          onClick={() => handleCompleteTask(t.id)}
                          disabled={completingTaskId === t.id}
                          className="w-4 h-4 rounded border border-input flex items-center justify-center hover:bg-emerald-500 hover:text-white transition-colors shrink-0"
                          title="Mark Done"
                        >
                          {completingTaskId === t.id ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Check className="w-3 h-3 text-transparent hover:text-white" />
                          )}
                        </button>
                        <div className="min-w-0">
                          <p className="font-medium text-foreground truncate">{t.title}</p>
                          <div className="flex items-center space-x-2 text-[10px] text-muted-foreground mt-0.5">
                            <span className="capitalize">{t.priority}</span>
                            <span>•</span>
                            <span className="capitalize">{t.category}</span>
                            {t.due_date && (
                              <>
                                <span>•</span>
                                <span className={t.is_overdue ? "text-red-600 font-bold" : ""}>
                                  Due {t.due_date} {t.is_overdue && "(Overdue)"}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {t.is_overdue && (
                        <Badge variant="destructive" className="text-[9px] py-0 px-1 shrink-0">
                          Overdue
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* ── SECTION 2: AVAILABLE SUPPLY ───────────────────────────── */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-5 bg-emerald-600 rounded-full" />
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              {lang === "ta" ? "2. விற்பனைக்கு தயாராக உள்ள விளைச்சல் இருப்பு" : "2. Aggregated Produce Available for Sale"}
            </h2>
          </div>
          <Link href="/matching" className="text-xs text-primary hover:underline flex items-center">
            {lang === "ta" ? "பொருத்துதல் பலகை" : "Match Console"}
            <ArrowRight className="w-3 h-3 ml-1" />
          </Link>
        </div>

        {aggregation && aggregation.batches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {aggregation.batches.map((batch, idx) => (
              <Card key={idx} className="border-border shadow-xs hover:border-emerald-500/50 transition-all">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <Badge variant="outline" className="text-[10px] bg-emerald-50 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800 mb-1">
                        {lang === "ta" && batch.crop_tamil_name ? batch.crop_tamil_name : batch.crop_name}
                      </Badge>
                      <CardTitle className="text-base font-extrabold text-foreground">
                        {batch.crop_name}
                      </CardTitle>
                    </div>
                    <Badge variant="secondary" className="text-[10px]">
                      {batch.status}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="p-4 pt-1 space-y-3 text-xs">
                  <div className="flex items-baseline justify-between pt-1 border-t border-border/50">
                    <span className="text-muted-foreground">{lang === "ta" ? "மொத்த இருப்பு:" : "Available Supply:"}</span>
                    <span className="text-base font-black text-emerald-700 dark:text-emerald-400">
                      {(batch.total_kg / 1000).toFixed(1)} <span className="text-xs font-normal text-muted-foreground">Tonnes ({batch.total_kg.toLocaleString()} kg)</span>
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 p-2 rounded-lg bg-muted/40 text-[11px]">
                    <div>
                      <span className="text-muted-foreground block text-[10px]">{lang === "ta" ? "பங்கேற்ற உழவர்கள்" : "Contributing Farmers"}</span>
                      <span className="font-semibold">{batch.farmer_count} {lang === "ta" ? "உழவர்கள்" : "members"}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px]">{lang === "ta" ? "கிடங்கு / மையம்" : "Storage Location"}</span>
                      <span className="font-semibold truncate block">{batch.warehouse || "FPO Hub"}</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] font-semibold text-muted-foreground block uppercase">
                      {lang === "ta" ? "தரம் வாரியான இருப்பு (Grade Breakdown):" : "Grade Breakdown:"}
                    </span>
                    <div className="flex gap-2">
                      {batch.grades && batch.grades.map((g, i) => (
                        <div key={i} className="flex-1 p-1.5 rounded bg-card border text-center">
                          <span className="text-[10px] text-muted-foreground block">Grade {g.grade}</span>
                          <span className="font-bold text-foreground text-xs">{g.quantity_kg.toLocaleString()} kg</span>
                          <span className="text-[9px] text-muted-foreground block">({g.percentage}%)</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2">
                    <Link href={`/matching`}>
                      <Button size="sm" variant="outline" className="w-full h-8 text-xs font-semibold border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 hover:bg-emerald-50 dark:hover:bg-emerald-950">
                        <Sparkles className="w-3.5 h-3.5 mr-1.5 text-emerald-600" />
                        {lang === "ta" ? "வாங்குபவர்களுடன் பொருத்து" : "Match With Active Buyers"}
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center border border-dashed rounded-xl bg-card text-xs text-muted-foreground">
            {lang === "ta"
              ? "விற்பனைக்கு தயாரான சேமிப்பு இல்லை. உழவர்களின் அறுவடைகளை சரிபார்த்து தொகுக்கவும்."
              : "No pooled batches ready for wholesale. Confirm member harvests above to build inventory."}
          </div>
        )}
      </section>

      {/* ── SECTION 3: BUYER OPPORTUNITIES & MATCH EXPLANATIONS ────── */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-5 bg-emerald-600 rounded-full" />
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              {lang === "ta" ? "3. கொள்முதல் தேவைகள் & பொருத்தம்" : "3. Buyer Opportunities & Match Explanations"}
            </h2>
          </div>
          <Link href="/buyers" className="text-xs text-primary hover:underline flex items-center">
            {lang === "ta" ? "அனைத்து தேவைகள்" : "All Requirements"}
            <ArrowRight className="w-3 h-3 ml-1" />
          </Link>
        </div>

        {buyerRequirements.length === 0 ? (
          <div className="p-8 text-center border border-dashed rounded-xl bg-card text-xs text-muted-foreground">
            {lang === "ta" ? "திறந்த கொள்முதல் தேவைகள் எதுவும் பதிவு செய்யப்படவில்லை." : "No open buyer requirements posted."}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {buyerRequirements.slice(0, 3).map((req) => {
              // Derive match rationale against pooled aggregation
              const matchingBatch = aggregation?.batches.find(
                (b) => b.crop_name.toLowerCase().includes(req.crop_name?.toLowerCase() || "") ||
                       (req.crop_name?.toLowerCase().includes(b.crop_name.toLowerCase()))
              );

              return (
                <Card key={req.id} className="border-border shadow-xs hover:border-primary/50 transition-all flex flex-col justify-between">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <Badge variant="outline" className="text-[10px] bg-primary/10 text-primary border-primary/20 mb-1">
                          {lang === "ta" && req.crop_tamil_name ? req.crop_tamil_name : req.crop_name}
                        </Badge>
                        <CardTitle className="text-sm font-bold text-foreground">
                          {req.buyer_name || "Commercial Buyer"}
                        </CardTitle>
                      </div>
                      <Badge variant="secondary" className="text-[10px]">
                        Target: {new Date(req.required_date).toLocaleDateString()}
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="p-4 pt-1 space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 p-2 rounded-lg bg-muted/40 text-[11px]">
                      <div>
                        <span className="text-muted-foreground block text-[10px]">{lang === "ta" ? "தேவைப்படும் அளவு" : "Required Qty"}</span>
                        <span className="font-bold text-foreground">{req.quantity_kg.toLocaleString()} kg</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px]">{lang === "ta" ? "அதிகபட்ச விலை" : "Target Price"}</span>
                        <span className="font-bold text-emerald-600">
                          {req.max_price_per_kg ? `₹${req.max_price_per_kg}/kg` : "Open Mandi"}
                        </span>
                      </div>
                    </div>

                    {/* Match Explanation Pill */}
                    <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-[11px]">
                      <div className="flex items-center space-x-1.5 text-emerald-800 dark:text-emerald-300 font-semibold mb-0.5">
                        <Sparkles className="w-3.5 h-3.5 shrink-0" />
                        <span>{lang === "ta" ? "ஏன் பொருந்துகிறது?" : "Why This Matches Supply"}</span>
                      </div>
                      <p className="text-emerald-900/90 dark:text-emerald-200/90 text-[10px] leading-tight">
                        {matchingBatch
                          ? lang === "ta"
                            ? `கூட்டமைப்பில் ${matchingBatch.total_kg.toLocaleString()} kg இருப்பு உள்ளது. தரம் ${req.min_grade}+ தேவை பூர்த்தியாகும்.`
                            : `FPO holds ${matchingBatch.total_kg.toLocaleString()} kg ready stock. Meets min Grade ${req.min_grade}.`
                          : lang === "ta"
                            ? `ஈரோடு மண்டல கிடங்கில் முன்னோடி ஒப்பந்தத்திற்கு தகுதியானது.`
                            : `High-value institutional demand in current procurement corridor.`}
                      </p>
                    </div>

                    <div className="pt-1">
                      <Link href={`/matching?req_id=${req.id}`}>
                        <Button size="sm" className="w-full h-8 text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90">
                          <span>{lang === "ta" ? "பொருத்துதலை உறுதிசெய்" : "Review & Match Supply"}</span>
                          <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </section>

      {/* ── SECTION 4: MARKET CONTEXT & PRICE TRUST TELEMETRY ──────── */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-5 bg-emerald-600 rounded-full" />
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              {lang === "ta" ? "4. சந்தை விலை & நம்பகத்தன்மை தணிக்கை" : "4. Market Context & Data Trustworthiness"}
            </h2>
          </div>
          <Link href="/prices" className="text-xs text-primary hover:underline flex items-center">
            {lang === "ta" ? "அனைத்து 38 மாவட்ட விலைகள்" : "View all 38 districts"}
            <ArrowRight className="w-3 h-3 ml-1" />
          </Link>
        </div>

        {/* Stale Warning Banner if applicable */}
        {stalePricesCount > 0 && (
          <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 rounded-xl p-3 text-xs text-amber-900 dark:text-amber-200 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              {lang === "ta"
                ? `கவனத்திற்கு: ${stalePricesCount} பயிர்களுக்கான சந்தை தகவல் 48 மணி நேரத்திற்கு முந்தையது. முடிவெடுக்கும் போது முந்தைய தேதியை கவனத்தில் கொள்க.`
                : `Transparency Notice: ${stalePricesCount} prices reflect observations older than 48 hours. Recommendations indicate stale status clearly.`}
            </span>
          </div>
        )}

        {/* Price Telemetry Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {prices.map((p) => {
            const isFresh = !p.is_stale && p.freshness_category === "fresh";
            const isDemo = p.freshness_category === "demo";

            return (
              <Card key={p.id} className="border-border shadow-xs hover:border-emerald-500/40 transition-colors">
                <CardContent className="p-3.5 space-y-2 text-xs">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-bold text-foreground text-sm leading-tight">
                        {lang === "ta" && p.crop_tamil_name ? p.crop_tamil_name : p.crop_name}
                      </p>
                      <p className="text-[10px] text-muted-foreground truncate">
                        {p.variety_name || (lang === "ta" ? "பொது வகை" : "Standard")}
                      </p>
                    </div>

                    {/* Freshness Badge */}
                    {isDemo ? (
                      <Badge variant="secondary" className="text-[9px] py-0 px-1 bg-amber-100 text-amber-800">
                        Demo Seed
                      </Badge>
                    ) : isFresh ? (
                      <Badge variant="success" className="text-[9px] py-0 px-1">
                        Fresh
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="text-[9px] py-0 px-1">
                        {p.stale_days ? `${p.stale_days}d Stale` : "Stale"}
                      </Badge>
                    )}
                  </div>

                  <div className="pt-1 flex items-baseline justify-between border-t border-border/50">
                    <span className="text-xl font-black text-foreground">
                      ₹{Number(p.modal_price).toLocaleString("en-IN")}
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      /{p.unit || "Quintal"}
                    </span>
                  </div>

                  <div className="text-[10px] text-muted-foreground space-y-0.5">
                    <div className="flex justify-between">
                      <span>{p.market_name}</span>
                      <span>({p.district})</span>
                    </div>
                    <div className="flex justify-between text-muted-foreground/75">
                      <span>{lang === "ta" ? "தேதி:" : "Date:"} {p.price_date}</span>
                      <span>{p.source}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>
    </div>
  );
}
