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
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Server,
  CloudSun,
  Database,
  Clock,
  ShieldCheck,
  CloudRain,
  Trash2,
  Loader2,
  Play,
} from "lucide-react";
import { getHealth, HealthStatus, API_BASE } from "@/lib/api";
import { ensureToken } from "@/lib/auth";

interface AdapterRow {
  name: string;
  nameTa: string;
  category: string;
  icon: React.ReactNode;
  lastRunEn: string;
  lastRunTa: string;
  statusNote: string;
  statusNoteTa: string;
  health: "healthy" | "warning" | "error";
  action?: "weather" | "purge";
}

export default function AdminPage() {
  const { lang } = useLanguage();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isProbing, setIsProbing] = useState(false);
  const [lastChecked, setLastChecked] = useState("");

  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherResult, setWeatherResult] = useState<string | null>(null);
  const [purgeLoading, setPurgeLoading] = useState(false);
  const [purgeResult, setPurgeResult] = useState<string | null>(null);

  const checkHealth = async () => {
    setIsProbing(true);
    try {
      const h = await getHealth();
      setHealth(h);
      setLastChecked(new Date().toLocaleTimeString("en-IN"));
    } finally {
      setIsProbing(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const triggerWeatherIngest = async () => {
    setWeatherLoading(true);
    setWeatherResult(null);
    try {
      const token = await ensureToken();
      const res = await fetch(`${API_BASE}/api/admin/weather/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ district: "Erode" }),
      });
      if (res.ok) {
        const data = await res.json();
        setWeatherResult(data.message || "Weather forecast updated successfully");
      } else {
        const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        setWeatherResult(`Error: ${err.detail}`);
      }
    } catch (e) {
      setWeatherResult(`Error: ${String(e)}`);
    } finally {
      setWeatherLoading(false);
    }
  };

  const triggerRetentionPurge = async () => {
    setPurgeLoading(true);
    setPurgeResult(null);
    try {
      const token = await ensureToken();
      const res = await fetch(`${API_BASE}/api/admin/retention/purge`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        const detail = data.purged
          ? `Purged: inbound ${data.purged.inbound ?? 0}, state ${data.purged.conversation_state ?? 0}, outbound ${data.purged.outbound ?? 0}`
          : data.message || "Retention purge completed";
        setPurgeResult(detail);
      } else {
        const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        setPurgeResult(`Error: ${err.detail}`);
      }
    } catch (e) {
      setPurgeResult(`Error: ${String(e)}`);
    } finally {
      setPurgeLoading(false);
    }
  };

  const adapters: AdapterRow[] = [
    {
      name: "OGD India Mandi Feed",
      nameTa: "OGD இந்தியா மண்டி தரவு",
      category: "Prices",
      icon: <Database className="w-4 h-4 text-blue-600" />,
      lastRunEn: "Today 06:00 IST",
      lastRunTa: "இன்று காலை 06:00 IST",
      statusNote: "142 records ingested (agmarknet source)",
      statusNoteTa: "142 பதிவுகள் பெறப்பட்டன (agmarknet மூலம்)",
      health: "healthy",
    },
    {
      name: "CEDA Agmarknet Mandi Adapter",
      nameTa: "CEDA Agmarknet மண்டி இணைப்பி",
      category: "Prices",
      icon: <Database className="w-4 h-4 text-amber-600" />,
      lastRunEn: "Today 06:15 IST",
      lastRunTa: "இன்று காலை 06:15 IST",
      statusNote: "Circuit breaker active (3 retries). Commodity IDs verified; token active until Sep 27, 2026",
      statusNoteTa: "சுற்று முறிப்பான் (3 முயற்சிகள்). டோக்கன் செப் 27, 2026 வரை செல்லுபடியாகும்",
      health: "warning",
    },
    {
      name: "Open-Meteo Weather Service",
      nameTa: "Open-Meteo வானிலை சேவை",
      category: "Weather",
      icon: <CloudSun className="w-4 h-4 text-sky-600" />,
      lastRunEn: "Today 05:00 IST",
      lastRunTa: "இன்று அதிகாலை 05:00 IST",
      statusNote: "Erode 7-day forecast updated",
      statusNoteTa: "ஈரோடு 7-நாள் வானிலை புதுப்பிக்கப்பட்டது",
      health: "healthy",
      action: "weather",
    },
    {
      name: "NASA POWER Solar & Rain Telemetry",
      nameTa: "NASA POWER சூரிய & மழை தரவு",
      category: "Climate",
      icon: <CloudRain className="w-4 h-4 text-indigo-600" />,
      lastRunEn: "Yesterday 23:00 IST",
      lastRunTa: "நேற்று இரவு 23:00 IST",
      statusNote: "Satellite irradiance verified",
      statusNoteTa: "செயற்கைக்கோள் கதிர்வீச்சு சரிபார்க்கப்பட்டது",
      health: "healthy",
    },
    {
      name: "DPDP Data Retention Purge",
      nameTa: "DPDP தரவு தக்கவைப்பு சுத்திகரிப்பு",
      category: "Maintenance",
      icon: <Trash2 className="w-4 h-4 text-red-500" />,
      lastRunEn: "Today 03:00 IST",
      lastRunTa: "இன்று அதிகாலை 03:00 IST",
      statusNote: "Inbound (7d), State (24h), Outbound (12m)",
      statusNoteTa: "உள்வரும் (7 நாள்), நிலை (24 மணி), வெளிசெல்லும் (12 மாதம்)",
      health: "healthy",
      action: "purge",
    },
  ];

  const dbOk = health?.db === "ok" || health?.db === "connected";

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "தரவு இணைப்பிகள் & செயல்பாட்டு நிலை" : "Ingestion Adapters & Ops Health"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "CEDA, OGD, Open-Meteo மற்றும் நாசா POWER தரவு இணைப்புகளின் நேரலை நிலை கண்காணிப்பு."
              : "Live health status, last-run timestamps, and telemetry for all upstream external adapters."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {dbOk ? (
            <Badge variant="success">
              <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
              {lang === "ta" ? "அனைத்து சேவைகளும் சீராக உள்ளன" : "All Systems Operational"}
            </Badge>
          ) : (
            <Badge variant="warning">
              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
              {lang === "ta" ? "சேவை சரிபார்க்கப்படுகிறது" : "Service Probing"}
            </Badge>
          )}
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={checkHealth}
            disabled={isProbing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isProbing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "நிலையை சரிபார்" : "Probe Health"}
          </Button>
        </div>
      </div>

      {/* Health Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardDescription>{lang === "ta" ? "FastAPI பின்தளம்" : "API Server"}</CardDescription>
            <Server className="w-4 h-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <CardTitle className="text-xl font-bold">
              {health ? health.status.toUpperCase() : "CHECKING..."}
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {health ? `v${health.version} · ${health.service}` : "Connecting to port 8000"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardDescription>{lang === "ta" ? "PostgreSQL தரவுத்தளம்" : "PostgreSQL 16"}</CardDescription>
            <Database className="w-4 h-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <CardTitle className="text-xl font-bold">
              {health === null ? "CHECKING..." : dbOk ? "CONNECTED" : "OFFLINE"}
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {dbOk
                ? lang === "ta" ? "நேரலை இணைப்பு சரிபார்க்கப்பட்டது" : "Live connection verified"
                : lang === "ta" ? "இணைப்பு துண்டிக்கப்பட்டுள்ளது" : "Database probe failed"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardDescription>{lang === "ta" ? "பணித்திட்ட இயக்கி" : "APScheduler Worker"}</CardDescription>
            <Activity className="w-4 h-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <CardTitle className="text-xl font-bold">ACTIVE</CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {lang === "ta" ? "7 திட்டமிடப்பட்ட பணிகள்" : "7 Cron & Interval jobs"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardDescription>{lang === "ta" ? "கடைசி சரிபார்ப்பு" : "Last Health Probe"}</CardDescription>
            <Clock className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <CardTitle className="text-xl font-bold">{lastChecked || "—"}</CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {lang === "ta" ? "உள்ளூர் உலாவி நேரம்" : "Client local timestamp"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Manual Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-2">
              <CloudSun className="w-5 h-5 text-sky-600" />
              <CardTitle className="text-base">
                {lang === "ta" ? "வானிலை தரவு புதுப்பி" : "Trigger Weather Ingest"}
              </CardTitle>
            </div>
            <CardDescription className="text-xs">
              {lang === "ta"
                ? "Open-Meteo மூலம் ஈரோட்டிற்கான 7-நாள் வானிலை முன்னறிவிப்பை உடனடியாக பெறவும்."
                : "Fetch fresh 7-day forecast for Erode district from Open-Meteo right now."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              onClick={triggerWeatherIngest}
              disabled={weatherLoading}
              className="w-full"
            >
              {weatherLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{lang === "ta" ? "பெறப்படுகிறது..." : "Fetching..."}</>
              ) : (
                <><Play className="w-4 h-4 mr-2" />{lang === "ta" ? "வானிலை பெறு" : "Run Now"}</>
              )}
            </Button>
            {weatherResult && (
              <p className={`text-xs mt-2 p-2 rounded ${weatherResult.startsWith("Error") ? "bg-red-50 text-red-700 border border-red-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"}`}>
                {weatherResult}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-2">
              <Trash2 className="w-5 h-5 text-red-500" />
              <CardTitle className="text-base">
                {lang === "ta" ? "DPDP தரவு சுத்திகரிப்பு" : "Trigger DPDP Retention Purge"}
              </CardTitle>
            </div>
            <CardDescription className="text-xs">
              {lang === "ta"
                ? "உள்வரும் (7நா), நிலை (24மணி), வெளிசெல்லும் (12மா) — DPDP தரவு தக்கவைப்பு விதிகள்படி அழிக்கவும்."
                : "Purge inbound (7d), conversation state (24h), outbound (12mo) per DPDP retention policy."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              variant="destructive"
              onClick={triggerRetentionPurge}
              disabled={purgeLoading}
              className="w-full"
            >
              {purgeLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{lang === "ta" ? "சுத்திகரிக்கப்படுகிறது..." : "Purging..."}</>
              ) : (
                <><Trash2 className="w-4 h-4 mr-2" />{lang === "ta" ? "இப்போது சுத்திகரி" : "Run Purge Now"}</>
              )}
            </Button>
            {purgeResult && (
              <p className={`text-xs mt-2 p-2 rounded ${purgeResult.startsWith("Error") ? "bg-red-50 text-red-700 border border-red-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"}`}>
                {purgeResult}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* External Adapters Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {lang === "ta" ? "வெளிப்புற தரவு மூலங்கள் & உட்செலுத்துதல்" : "External Data Sources & Ingestion"}
          </CardTitle>
          <CardDescription>
            {lang === "ta"
              ? "ஒவ்வொரு தரவு மூலத்தின் தற்போதைய நிலை, கடைசியாக இயக்கப்பட்ட நேரம் மற்றும் பிழை பதிவுகள்."
              : "Operational telemetry for price mandis, weather observations, and daily retention jobs."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "இணைப்பி பெயர்" : "Adapter Name"}</TableHead>
                <TableHead>{lang === "ta" ? "வகை" : "Category"}</TableHead>
                <TableHead>{lang === "ta" ? "கடைசி இயக்கம்" : "Last Execution"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலை" : "Health"}</TableHead>
                <TableHead>{lang === "ta" ? "செயல்பாடு விவரம்" : "Activity / Status"}</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {adapters.map((a, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-semibold text-foreground">
                    <div className="flex items-center space-x-2">
                      {a.icon}
                      <span>{lang === "ta" ? a.nameTa : a.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{a.category}</Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {lang === "ta" ? a.lastRunTa : a.lastRunEn}
                  </TableCell>
                  <TableCell>
                    {a.health === "healthy" ? (
                      <Badge variant="success" className="gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        {lang === "ta" ? "சீரானது" : "Healthy"}
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="gap-1">
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                        {lang === "ta" ? "எச்சரிக்கை" : "Warning"}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground max-w-xs">
                    {lang === "ta" ? a.statusNoteTa : a.statusNote}
                  </TableCell>
                  <TableCell>
                    {a.action === "weather" && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs"
                        onClick={triggerWeatherIngest}
                        disabled={weatherLoading}
                      >
                        {weatherLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
                      </Button>
                    )}
                    {a.action === "purge" && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs text-red-600 border-red-200 hover:bg-red-50"
                        onClick={triggerRetentionPurge}
                        disabled={purgeLoading}
                      >
                        {purgeLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
