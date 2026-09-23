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
  MessageSquare,
  Send,
  AlertOctagon,
  Clock,
  Radio,
  CheckCheck,
  ShieldCheck,
} from "lucide-react";

export default function WhatsAppPage() {
  const { lang } = useLanguage();

  const sampleInbound = [
    {
      id: "wamid.HBgLM...",
      waId: "9198421•••••",
      kind: "text",
      contentTa: "வணக்கம் (மெனு கோரப்பட்டது)",
      contentEn: "வணக்கம் (Requested Menu)",
      status: "processed",
      timeTa: "10 நிமிடங்களுக்கு முன்",
      timeEn: "10 mins ago",
    },
    {
      id: "wamid.HBgLN...",
      waId: "9197892•••••",
      kind: "button",
      contentTa: "பொத்தான்: மஞ்சள் விலை தகவல்",
      contentEn: "Button: Turmeric Price Rate",
      status: "processed",
      timeTa: "25 நிமிடங்களுக்கு முன்",
      timeEn: "25 mins ago",
    },
    {
      id: "wamid.HBgLO...",
      waId: "9194432•••••",
      kind: "text",
      contentTa: "அறுவடை பதிவு: மஞ்சள், 250 கிலோ",
      contentEn: "Harvest submit: Turmeric 250kg",
      status: "processed",
      timeTa: "45 நிமிடங்களுக்கு முன்",
      timeEn: "45 mins ago",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "வாட்ஸ்அப் போட் நேரலை கண்காணிப்பு" : "WhatsApp Bot Live Activity Monitor"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "உள்வரும் செய்திகள், உரையாடல் நிலைகள் மற்றும் தானியங்கி எச்சரிக்கைகளின் நேரலை பார்வை."
              : "Read-only staff visibility into inbound webhooks, conversation state, and delivery telemetry."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success">
            <Radio className="w-2.5 h-2.5 mr-1 text-emerald-600 animate-pulse" />
            {lang === "ta" ? "போட் இயங்குகிறது" : "WHATSAPP_ENABLED=true"}
          </Badge>
          <Button variant="outline" size="sm" className="h-8">
            <ShieldCheck className="w-3.5 h-3.5 mr-1 text-primary" />
            {lang === "ta" ? "அவசர நிறுத்தம் Runbook" : "Kill Switch Runbook"}
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "இன்றைய செய்திகள்" : "Today's Inbound"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold">128</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "100% செயலாக்கப்பட்டது (0 தோல்வி)" : "100% processed (0 failed)"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "மாதாந்திர ஒதுக்கீடு" : "Monthly Send Cap"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-foreground">
              342 <span className="text-sm font-normal text-muted-foreground">/ 5,000</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "6.8% வரவு செலவு பயன்பாடு" : "6.8% of ₹2,000 budget used"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "சராசரி பதில் நேரம்" : "Avg Response Time"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-emerald-700">1.4s</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "மெட்டா கிளவுட் API லேட்டன்சி" : "Meta Cloud API delivery latency"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "சுழற்சி துடைப்பான் நிலை" : "At-Least-Once Sweep"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-emerald-700">10 min</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "0 சிக்கிய செய்திகள்" : "0 stuck received rows"}
          </CardContent>
        </Card>
      </div>

      {/* Inbound Messages Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {lang === "ta" ? "சமீபத்திய உள்வரும் செய்திகள் பதிவேடு" : "Recent Inbound Webhook Activity"}
          </CardTitle>
          <CardDescription>
            {lang === "ta"
              ? "DPDP விதிகளின்படி உழவர் தொலைபேசி எண்கள் முகமூடி செய்யப்பட்டுள்ளன (PII Masking)."
              : "All farmer phone numbers masked (first 3, last 2) per DPDP compliance standards."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "செய்தி ID" : "Message ID"}</TableHead>
                <TableHead>{lang === "ta" ? "உழவர் எண் (மறைக்கப்பட்டது)" : "Farmer Phone (Masked)"}</TableHead>
                <TableHead>{lang === "ta" ? "வகை" : "Type"}</TableHead>
                <TableHead>{lang === "ta" ? "செய்தி உள்ளடக்கம்" : "Message Context"}</TableHead>
                <TableHead>{lang === "ta" ? "நேரம்" : "Timestamp"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலை" : "Lifecycle Status"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sampleInbound.map((row, i) => (
                <TableRow key={i}>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {row.id}
                  </TableCell>
                  <TableCell className="font-mono text-xs font-semibold">
                    {row.waId}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{row.kind}</Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    {lang === "ta" ? row.contentTa : row.contentEn}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {lang === "ta" ? row.timeTa : row.timeEn}
                  </TableCell>
                  <TableCell>
                    <Badge variant="success" className="space-x-1">
                      <CheckCheck className="w-3 h-3 mr-1" />
                      <span>{lang === "ta" ? "வெற்றிகரமாக முடிந்தது" : "Processed"}</span>
                    </Badge>
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
