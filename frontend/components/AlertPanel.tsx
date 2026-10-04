"use client";

import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Bell,
  X,
  Smartphone,
  Loader2,
} from "lucide-react";
import { getWhatsAppActivity, getHealth } from "@/lib/api";

interface AlertPanelProps {
  lang: "ta" | "en";
  t: any;
}

interface LiveAlert {
  id: string;
  type: "bot" | "info";
  titleTa: string;
  titleEn: string;
  descTa: string;
  descEn: string;
  level: "warning" | "info" | "success" | "error";
}

export default function AlertPanel({ lang, t }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<LiveAlert[]>([]);
  const [dismissed, setDismissed] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [botEnabled, setBotEnabled] = useState<boolean | null>(null);
  const [botAvailable, setBotAvailable] = useState(false);

  useEffect(() => {
    async function buildAlerts() {
      const built: LiveAlert[] = [];

      try {
        // 1. WhatsApp bot status
        const wa = await getWhatsAppActivity(1);
        setBotEnabled(wa.enabled);
        setBotAvailable(wa.available);

        if (!wa.available) {
          built.push({
            id: "whatsapp-unavailable",
            type: "info",
            level: "info",
            titleTa: "வாட்ஸ்அப் நிலையைப் பெற முடியவில்லை",
            titleEn: "WhatsApp status unavailable",
            descTa: "செய்தி சேவை நிலையை உறுதிப்படுத்த API-ஐச் சரிபார்க்கவும்.",
            descEn: "Check the API connection to verify messaging service status.",
          });
        }

        if (wa.available && !wa.enabled) {
          built.push({
            id: "bot-killswitch",
            type: "bot",
            level: "error",
            titleTa: "வாட்ஸ்அப் பாட் நிறுத்தப்பட்டது (Kill-Switch ON)",
            titleEn: "WhatsApp Bot Kill-Switch is ON",
            descTa:
              "அனைத்து வாட்ஸ்அப் செய்திகளும் தடுக்கப்பட்டுள்ளன. நிர்வாகி .env-ல் WHATSAPP_ENABLED=false என அமைத்துள்ளார்.",
            descEn:
              "All outbound WhatsApp messages are blocked. Admin has set WHATSAPP_ENABLED=false in .env.",
          });
        }

        const health = await getHealth();
        if (health.status === "degraded" || (health.db !== "ok" && health.db !== "connected" && health.db !== "healthy")) {
          built.push({
            id: "db-health",
            type: "info",
            level: "error",
            titleTa: "தரவுத்தளம் இணைக்கப்படவில்லை",
            titleEn: "Database connection issue",
            descTa: `DB நிலை: ${health.db}. உடனடியாக நிர்வாகியிடம் தெரியப்படுத்துங்கள்.`,
            descEn: `DB status: ${health.db}. Contact admin immediately.`,
          });
        }

      } catch (err) {
        console.warn("AlertPanel load error:", err);
      } finally {
        setAlerts(built);
        setLoading(false);
      }
    }

    buildAlerts();
  }, []);

  const dismissAlert = (id: string) => {
    setDismissed((prev) => prev.includes(id) ? prev : [...prev, id]);
  };

  const visible = alerts.filter((a) => !dismissed.includes(a.id));

  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 p-5 sm:p-6 shadow-xs">
      <div className="flex items-center justify-between pb-4 border-b border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-gray-900 tracking-tight">
              {t.alerts_panel.title}
            </h3>
            <p className="text-xs text-gray-500">
              {lang === "ta"
              ? "வாட்ஸ்அப் சேவை மற்றும் தரவுத்தள நிலை"
              : "WhatsApp service and database status checks"}
            </p>
          </div>
        </div>

        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
          {loading ? "…" : visible.length}{" "}
          {lang === "ta" ? "செயலில்" : "Active"}
        </span>
      </div>

      {/* Alert List */}
      <div className="mt-4 space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-8 text-gray-400 text-sm">
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            {lang === "ta" ? "எச்சரிக்கைகள் ஏற்றப்படுகிறது..." : "Loading alerts..."}
          </div>
        ) : visible.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-xs">
            <CheckCircle2 className="w-8 h-8 mx-auto text-green-500 mb-2" />
            <p className="font-semibold">
              {lang === "ta" ? "எந்த புதிய எச்சரிக்கைகளும் இல்லை" : "All operational alerts clear"}
            </p>
          </div>
        ) : (
          visible.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-xl border transition-all flex items-start justify-between ${
                alert.level === "warning"
                  ? "bg-amber-50/70 border-amber-200 text-amber-900"
                  : alert.level === "error"
                  ? "bg-red-50/70 border-red-200 text-red-900"
                  : alert.level === "info"
                  ? "bg-blue-50/70 border-blue-200 text-blue-900"
                  : "bg-emerald-50/70 border-emerald-200 text-emerald-900"
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="mt-0.5">
                  {alert.type === "bot" && (
                    <Smartphone className="w-5 h-5 text-red-600" />
                  )}
                  {alert.type === "info" && (
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-bold tracking-tight">
                    {lang === "ta" ? alert.titleTa : alert.titleEn}
                  </h4>
                  <p className="text-xs mt-1 leading-relaxed opacity-85">
                    {lang === "ta" ? alert.descTa : alert.descEn}
                  </p>
                </div>
              </div>

              <button
                onClick={() => dismissAlert(alert.id)}
                className="text-gray-400 hover:text-gray-700 p-1 rounded-lg transition-colors ml-2"
                title={t.alerts_panel.dismiss}
                aria-label={t.alerts_panel.dismiss}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* WhatsApp Bot Heartbeat */}
      <div className="mt-5 pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-600 bg-gray-50 p-3 rounded-xl">
        <div className="flex items-center space-x-2">
          <Smartphone className="w-4 h-4 text-green-600" />
          <span className="font-semibold text-gray-800">
            {lang === "ta" ? "வாட்ஸ்அப் பாட் நிலை:" : "WhatsApp Cloud API Status:"}
          </span>
          {!botAvailable ? (
            <span className="font-medium text-amber-700">{lang === "ta" ? "தரவு கிடைக்கவில்லை" : "Unavailable"}</span>
          ) : botEnabled ? (
            <span className="text-emerald-700 font-bold flex items-center">
              <span className="size-2 rounded-full bg-emerald-500 mr-1" />
              {lang === "ta" ? "இயக்கப்பட்டுள்ளது" : "Enabled"}
            </span>
          ) : (
            <span className="text-red-600 font-bold">
              {lang === "ta" ? "நிறுத்தப்பட்டது (Kill-Switch ON)" : "Kill-Switch ON"}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
