"use client";

import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  CloudRain,
  ShieldCheck,
  CheckCircle2,
  Bell,
  X,
  Smartphone,
  Loader2,
  TrendingUp,
} from "lucide-react";
import { getLatestPrices, getWhatsAppActivity, getHealth } from "@/lib/api";

interface AlertPanelProps {
  lang: "ta" | "en";
  t: any;
}

interface LiveAlert {
  id: string;
  type: "anomaly" | "weather" | "dpdp" | "bot" | "info";
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

  useEffect(() => {
    async function buildAlerts() {
      const built: LiveAlert[] = [];

      try {
        // 1. WhatsApp bot status
        const wa = await getWhatsAppActivity(1);
        setBotEnabled(wa.enabled);

        if (!wa.enabled) {
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

        // 2. Price anomaly detection — flag if any price is unusually high
        const prices = await getLatestPrices("Erode");
        for (const price of prices) {
          // Simple spike check: modal > 1.5× min is suspicious
          if (
            price.modal_price &&
            price.min_price &&
            Number(price.modal_price) > Number(price.min_price) * 1.5
          ) {
            built.push({
              id: `anomaly-${price.id}`,
              type: "anomaly",
              level: "warning",
              titleTa: `${price.crop_tamil_name || price.crop_name} விலை முரண்பாடு — ${price.market_name}`,
              titleEn: `${price.crop_name} price spike — ${price.market_name}`,
              descTa: `மோடல் விலை ₹${Number(price.modal_price).toLocaleString("en-IN")}/கி — குறைந்தபட்சத்தை விட கணிசமாக அதிகம். மனித சரிபார்ப்பு பரிந்துரைக்கப்படுகிறது.`,
              descEn: `Modal ₹${Number(price.modal_price).toLocaleString("en-IN")}/q is significantly above min ₹${Number(price.min_price).toLocaleString("en-IN")}/q — verify with market.`,
            });
          }
        }

        // 3. DB health check
        const health = await getHealth();
        if (health.db !== "ok" && health.db !== "connected") {
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

        // 4. DPDP compliance note (static, always shown as info)
        built.push({
          id: "dpdp-compliance",
          type: "dpdp",
          level: "success",
          titleTa: "DPDP சட்டம்: தொலைபேசி மறைக்கல் செயல்படுத்தப்பட்டுள்ளது",
          titleEn: "DPDP Act: Phone masking enforced",
          descTa:
            "அனைத்து விவசாயி தொலைபேசி எண்களும் மறைக்கப்பட்டுள்ளன. ஒப்புதல் பதிவு (opt-in) செயல்படுத்தப்பட்டுள்ளது.",
          descEn:
            "All farmer phone numbers are masked in the UI. WhatsApp consent opt-in tracking is active.",
        });
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
                ? "நேரடி செயல்பாட்டு எச்சரிக்கைகள் — விலை முரண்பாடு & வாட்ஸ்அப் நிலை"
                : "Live operational alerts — price anomalies & WhatsApp status"}
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
                  {alert.type === "anomaly" && (
                    <TrendingUp className="w-5 h-5 text-amber-600" />
                  )}
                  {alert.type === "weather" && (
                    <CloudRain className="w-5 h-5 text-blue-600" />
                  )}
                  {alert.type === "dpdp" && (
                    <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  )}
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
          {botEnabled === null ? (
            <span className="text-gray-400">…</span>
          ) : botEnabled ? (
            <span className="text-emerald-700 font-bold flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1 animate-pulse" />
              {lang === "ta" ? "இணைக்கப்பட்டுள்ளது" : "Connected"}
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
