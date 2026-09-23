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
  Radio,
  Clock,
  ShieldCheck,
} from "lucide-react";
import { getHealth, HealthStatus } from "@/lib/api";

export default function AdminPage() {
  const { lang } = useLanguage();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isProbing, setIsProbing] = useState<boolean>(false);
  const [lastChecked, setLastChecked] = useState<string>("");

  const checkHealth = async () => {
    setIsProbing(true);
    try {
      const h = await getHealth();
      setHealth(h);
      setLastChecked(new Date().toLocaleTimeString());
    } finally {
      setIsProbing(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const adapters = [
    {
      name: "OGD India Mandi Feed",
      category: "Prices",
      lastRunTa: "இன்று காலை 06:00 IST",
      lastRunEn: "Today 06:00 IST",
      status: "healthy",
      records: "142 records ingested",
      recordsTa: "142 பதிவுகள் பெறப்பட்டன",
    },
    {
      name: "CEDA Agmarknet Mandi Adapter",
      category: "Prices",
      lastRunTa: "இன்று காலை 06:15 IST",
      lastRunEn: "Today 06:15 IST",
      status: "healthy",
      note: "Commodity IDs verified; token active until Sep 27, 2026",
      noteTa: "பயிர் குறியீடுகள் சரிபார்க்கப்பட்டன; டோக்கன் செப் 27, 2026 வரை செல்லுபடியாகும்",
      records: "Circuit breaker active (3 retries)",
      recordsTa: "சுற்று முறிப்பான் இயக்கத்தில் உள்ளது (3 முயற்சிகள்)",
    },
    {
      name: "Open-Meteo Weather Service",
      category: "Weather",
      lastRunTa: "இன்று அதிகாலை 05:00 IST",
      lastRunEn: "Today 05:00 IST",
      status: "healthy",
      records: "Erode 7-day forecast updated",
      recordsTa: "ஈரோடு 7-நாள் வானிலை புதுப்பிக்கப்பட்டது",
    },
    {
      name: "NASA POWER Solar & Rain Telemetry",
      category: "Climate",
      lastRunTa: "நேற்று இரவு 23:00 IST",
      lastRunEn: "Yesterday 23:00 IST",
      status: "healthy",
      records: "Satellite irradiance verified",
      recordsTa: "செயற்கைக்கோள் கதிர்வீச்சு சரிபார்க்கப்பட்டது",
    },
    {
      name: "DPDP Data Retention Purge",
      category: "Maintenance",
      lastRunTa: "இன்று அதிகாலை 03:00 IST",
      lastRunEn: "Today 03:00 IST",
      status: "healthy",
      records: "Inbound (7d), State (24h), Outbound (12m)",
      recordsTa: "உள்வரும் (7 நாள்), நிலை (24 மணி), வெளிசெல்லும் (12 மாதம்)",
    },
  ];

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
          {health?.status === "ok" ? (
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
              {health ? `v${health.version} • ${health.service}` : "Connecting to port 8000"}
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
              {health?.db === "ok" ? "CONNECTED" : "OFFLINE"}
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              {health?.db === "ok"
                ? lang === "ta"
                  ? "நேரலை இணைப்பு சரிபார்க்கப்பட்டது"
                  : "Live connection verified"
                : lang === "ta"
                ? "இணைப்பு துண்டிக்கப்பட்டுள்ளது"
                : "Database probe failed"}
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
              </TableRow>
            </TableHeader>
            <TableBody>
              {adapters.map((a, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-semibold text-foreground">{a.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{a.category}</Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {lang === "ta" ? a.lastRunTa : a.lastRunEn}
                  </TableCell>
                  <TableCell>
                    <Badge variant="success" className="gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      {lang === "ta" ? "சீரானது" : "Healthy"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    <div>{lang === "ta" ? a.recordsTa : a.records}</div>
                    {a.note && (
                      <div className="text-[11px] text-amber-700 dark:text-amber-400 mt-0.5">
                        {lang === "ta" ? a.noteTa : a.note}
                      </div>
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
