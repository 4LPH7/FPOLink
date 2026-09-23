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
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  AlertOctagon,
  Radio,
  CheckCheck,
  ShieldCheck,
  RefreshCw,
  Terminal,
  Clock,
  AlertCircle,
  Inbox,
} from "lucide-react";
import {
  getWhatsAppActivity,
  getWhatsAppUsage,
  WhatsAppActivitySummary,
  WhatsAppUsageSummary,
} from "@/lib/api";

export default function WhatsAppPage() {
  const { lang } = useLanguage();
  const [runbookOpen, setRunbookOpen] = useState(false);
  const [activity, setActivity] = useState<WhatsAppActivitySummary | null>(null);
  const [usage, setUsage] = useState<WhatsAppUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const [act, use] = await Promise.all([
        getWhatsAppActivity(25),
        getWhatsAppUsage(),
      ]);
      setActivity(act);
      setUsage(use);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const totalInbound = activity?.total_inbound ?? 0;
  const totalOutbound = usage?.total_messages ?? (activity?.total_outbound ?? 0);
  const monthlyCap = usage?.monthly_cap ?? 5000;
  const deliveryRate = usage ? `${usage.delivery_rate_pct.toFixed(1)}%` : "100.0%";
  const estCost = usage ? `₹${usage.estimated_cost_inr.toFixed(2)}` : "₹0.00";
  const circuitTripped = usage?.circuit_breaker_tripped ?? false;

  const messages = activity?.inbound_messages || [];

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
          <Badge variant={circuitTripped ? "destructive" : "success"}>
            <Radio className={`w-2.5 h-2.5 mr-1 ${circuitTripped ? "text-destructive" : "text-emerald-600 animate-pulse"}`} />
            {circuitTripped
              ? (lang === "ta" ? "சுற்று முறிப்பான் இயக்கப்பட்டது" : "CIRCUIT BREAKER TRIPPED")
              : (lang === "ta" ? "போட் இயங்குகிறது" : "WHATSAPP_ENABLED=true")}
          </Badge>

          {/* Kill Switch Runbook Drawer */}
          <Sheet open={runbookOpen} onOpenChange={setRunbookOpen}>
            <Button
              variant="outline"
              size="sm"
              className="h-8"
              onClick={() => setRunbookOpen(true)}
            >
              <ShieldCheck className="w-3.5 h-3.5 mr-1 text-primary" />
              {lang === "ta" ? "அவசர நிறுத்தம் Runbook" : "Kill Switch Runbook"}
            </Button>
            <SheetContent side="right" className="w-[340px] sm:w-[480px]">
              <SheetHeader>
                <SheetTitle className="text-lg flex items-center gap-2">
                  <AlertOctagon className="w-5 h-5 text-destructive" />
                  {lang === "ta" ? "அவசர நிறுத்தம் (Kill Switch)" : "Emergency Kill Switch"}
                </SheetTitle>
                <SheetDescription>
                  {lang === "ta"
                    ? "வாட்ஸ்அப் கிளவுட் API வழியாக செய்திகள் அனுப்பப்படுவதை உடனடியாக நிறுத்துவதற்கான வழிமுறை."
                    : "Zero-downtime operational procedure to halt all outbound WhatsApp transmissions."}
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-4 text-xs">
                <div className="rounded-md border p-3 bg-muted/50 space-y-2">
                  <div className="font-semibold text-foreground flex items-center gap-1.5">
                    <Terminal className="w-4 h-4 text-primary" />
                    <span>Step 1: Set Environment Kill Switch</span>
                  </div>
                  <pre className="p-2 rounded bg-background font-mono text-[11px] overflow-x-auto">
                    WHATSAPP_ENABLED=false
                  </pre>
                  <p className="text-muted-foreground">
                    Webhooks immediately return HTTP 503 Service Unavailable, preventing cost exhaustion.
                  </p>
                </div>

                <div className="rounded-md border p-3 bg-muted/50 space-y-2">
                  <div className="font-semibold text-foreground flex items-center gap-1.5">
                    <Terminal className="w-4 h-4 text-primary" />
                    <span>Step 2: Restart Containers</span>
                  </div>
                  <pre className="p-2 rounded bg-background font-mono text-[11px] overflow-x-auto">
                    docker compose restart backend worker
                  </pre>
                </div>

                <div className="rounded-md border p-3 bg-muted/50 space-y-2">
                  <div className="font-semibold text-foreground flex items-center gap-1.5">
                    <Terminal className="w-4 h-4 text-primary" />
                    <span>Step 3: Verification Probe</span>
                  </div>
                  <pre className="p-2 rounded bg-background font-mono text-[11px] overflow-x-auto">
                    curl -i http://localhost:8000/api/whatsapp/webhook
                  </pre>
                  <p className="text-muted-foreground">
                    Confirm HTTP 503 response code is returned.
                  </p>
                </div>
              </div>
            </SheetContent>
          </Sheet>

          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={refreshData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Real KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "உள்வந்த செய்திகள் (மொத்தம்)" : "Total Inbound Messages"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold">{totalInbound}</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta"
              ? "PostgreSQL-இல் பதிவுசெய்யப்பட்ட நேரலை செய்திகள்"
              : "Live messages persisted in database"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "வெளிச்செல்லும் செய்திகள் / வரம்பு" : "Outbound Messages / Cap"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-foreground">
              {totalOutbound} <span className="text-sm font-normal text-muted-foreground">/ {monthlyCap.toLocaleString()}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta"
              ? `மதிப்பிடப்பட்ட செலவு: ${estCost}`
              : `Month-to-date estimated cost: ${estCost}`}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "செய்தி வழங்கல் வெற்றி விகிதம்" : "Delivery Success Rate"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-emerald-700">{deliveryRate}</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "வெற்றிகரமாக வழங்கப்பட்ட விகிதம்" : "Resolved messages successfully delivered"}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{lang === "ta" ? "தானியங்கி துடைப்பான் சுழற்சி" : "At-Least-Once Sweep"}</CardDescription>
            <CardTitle className="text-2xl font-extrabold text-emerald-700">
              {circuitTripped ? "HALTED" : "ACTIVE"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {lang === "ta" ? "10 நிமிட பின்னணி பணி" : "Periodic 10-minute worker cron job"}
          </CardContent>
        </Card>
      </div>

      {/* Inbound Messages Table (100% Real Live Data) */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {lang === "ta" ? "சமீபத்திய உள்வரும் செய்திகள் பதிவேடு" : "Recent Inbound Webhook Activity"}
          </CardTitle>
          <CardDescription>
            {lang === "ta"
              ? "DPDP விதிகளின்படி உழவர் தொலைபேசி எண்கள் முகமூடி செய்யப்பட்டுள்ளன (PII Masking)."
              : "Direct live stream from PostgreSQL whatsapp_inbound table."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <RefreshCw className="w-5 h-5 animate-spin mr-2" />
              <span>{lang === "ta" ? "ஏற்றுகிறது..." : "Loading live activity..."}</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
              <Inbox className="w-10 h-10 mb-2 opacity-40" />
              <p className="font-medium text-sm">
                {lang === "ta" ? "உள்வரும் செய்திகள் எதுவும் இல்லை" : "No inbound messages recorded yet"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {lang === "ta"
                  ? "விவசாயிகள் வாட்ஸ்அப்பில் செய்தி அனுப்பும்போது இங்கே தோன்றும்."
                  : "Incoming farmer messages received via Meta Cloud API webhook will appear here in real time."}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{lang === "ta" ? "செய்தி ID" : "Message ID"}</TableHead>
                  <TableHead>{lang === "ta" ? "மறுமுயற்சி எண்ணிக்கை" : "Retry Count"}</TableHead>
                  <TableHead>{lang === "ta" ? "நிலை" : "Lifecycle Status"}</TableHead>
                  <TableHead className="text-right">{lang === "ta" ? "பெறப்பட்ட நேரம்" : "Received At"}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {messages.map((row) => (
                  <TableRow key={row.message_id}>
                    <TableCell className="font-mono text-xs font-medium text-foreground">
                      {row.message_id}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {row.retry_count > 0 ? (
                        <Badge variant="warning">{row.retry_count} retries</Badge>
                      ) : (
                        <span className="text-muted-foreground">0</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {row.status === "processed" ? (
                        <Badge variant="success" className="space-x-1">
                          <CheckCheck className="w-3 h-3 mr-1" />
                          <span>{lang === "ta" ? "செயலாக்கப்பட்டது" : "Processed"}</span>
                        </Badge>
                      ) : row.status === "failed" ? (
                        <Badge variant="destructive" className="space-x-1">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          <span>{lang === "ta" ? "தோல்வி" : "Failed"}</span>
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="space-x-1">
                          <Clock className="w-3 h-3 mr-1" />
                          <span>{row.status}</span>
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right text-xs font-mono text-muted-foreground">
                      {row.received_at ? new Date(row.received_at).toLocaleString() : "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
