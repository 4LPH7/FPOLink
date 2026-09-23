"use client";

import React from "react";
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
} from "lucide-react";

export default function AdminPage() {
  const { lang } = useLanguage();

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
      status: "degraded",
      note: "Sep 20 504 Timeout resolved; token valid until Sep 27, 2026",
      noteTa: "செப் 20 காலக்கெடு பிழை சரி செய்யப்பட்டது; டோக்கன் செப் 27, 2026 வரை செல்லுபடியாகும்",
      records: "88 records ingested",
      recordsTa: "88 பதிவுகள் பெறப்பட்டன",
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
          <Badge variant="success">
            <Radio className="w-2.5 h-2.5 mr-1 text-emerald-600 animate-pulse" />
            {lang === "ta" ? "அனைத்து இணைப்புகளும் தயார்" : "4 / 4 Adapters Active"}
          </Badge>
          <Button variant="outline" size="sm" className="h-8">
            <RefreshCw className="w-3.5 h-3.5 mr-1 text-muted-foreground" />
            {lang === "ta" ? "மீண்டும் இயக்கு" : "Run Ingestion"}
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "கடைசி முழுமையான சுழற்சி" : "Last Pipeline Run"}</CardDescription>
            <CardTitle className="text-xl">07:00 IST</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "முன்கணிப்பு மாதிரி இயக்கம் நிறைவு" : "ML Price Prediction Run Completed"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "CEDA டோக்கன் காலாவதி" : "CEDA Token Expiry"}</CardDescription>
            <CardTitle className="text-xl text-emerald-700">Sep 27, 2026</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "அங்கீகரிக்கப்பட்ட நேரலை அணுகல்" : "Authorized Live API Access Active"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "தரவுத்தள சேமிப்பு நிலை" : "Database & Health"}</CardDescription>
            <CardTitle className="text-xl text-emerald-700">PostgreSQL 16</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "/api/health DB இணைப்பு: நன்று" : "/api/health DB probe: 200 OK"}
          </CardContent>
        </Card>
      </div>

      {/* Adapters Status Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {lang === "ta" ? "வெளிப்புறத் தரவு இணைப்பிகள் அட்டவணை" : "Upstream Adapter Health Matrix"}
          </CardTitle>
          <CardDescription>
            {lang === "ta"
              ? "ஒவ்வொரு இணைப்பியின் இறுதி இயக்கம், பெறப்பட்ட பதிவுகள் மற்றும் எச்சரிக்கைகள்."
              : "Telemetry tracking error rates, 504 timeouts, and ingestion record volumes."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "இணைப்பி" : "Adapter"}</TableHead>
                <TableHead>{lang === "ta" ? "வகை" : "Category"}</TableHead>
                <TableHead>{lang === "ta" ? "கடைசி இயக்கம்" : "Last Run"}</TableHead>
                <TableHead>{lang === "ta" ? "பதிவுகள் / விவரம்" : "Ingestion Telemetry"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலை" : "Health Status"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {adapters.map((a, i) => (
                <TableRow key={i}>
                  <TableCell className="font-semibold text-foreground">
                    <div className="flex items-center space-x-2">
                      <Server className="w-4 h-4 text-muted-foreground" />
                      <span>{a.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{a.category}</Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {lang === "ta" ? a.lastRunTa : a.lastRunEn}
                  </TableCell>
                  <TableCell className="text-xs">
                    <div>{lang === "ta" ? a.recordsTa : a.records}</div>
                    {a.note && (
                      <div className="text-[11px] text-amber-700 dark:text-amber-400 mt-0.5">
                        ⚠️ {lang === "ta" ? a.noteTa : a.note}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    {a.status === "healthy" ? (
                      <Badge variant="success" className="space-x-1">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        <span>{lang === "ta" ? "இயக்கத்தில்" : "Healthy"}</span>
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="space-x-1">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        <span>{lang === "ta" ? "கண்காணிப்பில்" : "Degraded / 504 Recovered"}</span>
                      </Badge>
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
