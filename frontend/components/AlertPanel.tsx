"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CloudRain,
  ShieldCheck,
  CheckCircle2,
  Bell,
  X,
  ChevronRight,
  Sparkles,
  Smartphone,
} from "lucide-react";

interface AlertPanelProps {
  lang: "ta" | "en";
  t: any;
}

export default function AlertPanel({ lang, t }: AlertPanelProps) {
  const [alerts, setAlerts] = useState([
    {
      id: "alert-1",
      type: "anomaly",
      titleTa: "பெருந்துறை ஒழுங்குமுறை விற்பனைக்கூடத்தில் விலை முரண்பாடு",
      titleEn: "Price Anomaly at Perundurai Regulated Market",
      descTa: "மஞ்சள் விலை வரலாற்று சராசரியை விட 9.8% உயர்ந்து ₹12,850/குவிண்டால் என பதிவாகியுள்ளது (MAD முரண்பாடு உறுதிப்படுத்தப்பட்டது).",
      descEn: "Turmeric spiked +9.8% above rolling MAD median to ₹12,850/q. Statistical anomaly flagged for human verification.",
      level: "warning",
      timeTa: "3 மணி நேரத்திற்கு முன்",
      timeEn: "3h ago",
    },
    {
      id: "alert-2",
      type: "weather",
      titleTa: "ஈரோடு வானிலை எச்சரிக்கை: லேசான மழை வாய்ப்பு",
      titleEn: "Erode Weather Advisory: Light Rain Inbound",
      descTa: "அடுத்த 48 மணி நேரத்தில் கொடுமுடி மற்றும் பெருந்துறை பகுதிகளில் 12 மிமீ மழை பெய்ய வாய்ப்புள்ளது. மஞ்சள் களத்துமேட்டு உலர்த்தலில் கவனம் தேவை.",
      descEn: "12mm precipitation forecast for Kodumudi & Perundurai taluks over 48h. Protect open-air turmeric drying yards.",
      level: "info",
      timeTa: "5 மணி நேரத்திற்கு முன்",
      timeEn: "5h ago",
    },
    {
      id: "alert-3",
      type: "dpdp",
      titleTa: "DPDP சட்டம்: அனைத்து விவசாயிகளின் எண்களும் குறியாக்கம் செய்யப்பட்டுள்ளன",
      titleEn: "DPDP Act Compliance: 100% Phone Masking Enforced",
      descTa: "உறுப்பினர்களின் தனிநபர் தரவு பாதுகாப்பு மற்றும் வெளிப்படையான ஒப்புதல் பதிவு (Consent Logging) முறையாக செயல்படுத்தப்பட்டுள்ளது.",
      descEn: "All 1,250 registered farmer contact numbers are masked (98****3210) with verified opt-in audit logs.",
      level: "success",
      timeTa: "நேற்று",
      timeEn: "Yesterday",
    },
  ]);

  const dismissAlert = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

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
                ? "தானியங்கி முரண்பாடு ஆய்வு & வானிலை வழிகாட்டல்"
                : "Automated anomaly flags and advisory telemetry"}
            </p>
          </div>
        </div>

        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
          {alerts.length} {lang === "ta" ? "செயலில்" : "Active"}
        </span>
      </div>

      {/* Alert List */}
      <div className="mt-4 space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`p-4 rounded-xl border transition-all flex items-start justify-between ${
              alert.level === "warning"
                ? "bg-amber-50/70 border-amber-200 text-amber-900"
                : alert.level === "info"
                ? "bg-blue-50/70 border-blue-200 text-blue-900"
                : "bg-emerald-50/70 border-emerald-200 text-emerald-900"
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className="mt-0.5">
                {alert.type === "anomaly" && (
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                )}
                {alert.type === "weather" && (
                  <CloudRain className="w-5 h-5 text-blue-600" />
                )}
                {alert.type === "dpdp" && (
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                )}
              </div>

              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold tracking-tight">
                    {lang === "ta" ? alert.titleTa : alert.titleEn}
                  </h4>
                  <span className="text-[10px] font-semibold opacity-60">
                    • {lang === "ta" ? alert.timeTa : alert.timeEn}
                  </span>
                </div>
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
        ))}

        {alerts.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-xs">
            <CheckCircle2 className="w-8 h-8 mx-auto text-green-500 mb-2" />
            <p className="font-semibold">
              {lang === "ta" ? "எந்த புதிய எச்சரிக்கைகளும் இல்லை" : "All operational alerts clear"}
            </p>
          </div>
        )}
      </div>

      {/* WhatsApp Bot Heartbeat Card */}
      <div className="mt-5 pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-600 bg-gray-50 p-3 rounded-xl">
        <div className="flex items-center space-x-2">
          <Smartphone className="w-4 h-4 text-green-600" />
          <span className="font-semibold text-gray-800">
            {lang === "ta" ? "வாட்ஸ்அப் பாட் நிலை:" : "WhatsApp Cloud API Status:"}
          </span>
          <span className="text-emerald-700 font-bold flex items-center">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1 animate-pulse"></span>
            {lang === "ta" ? "இணைக்கப்பட்டுள்ளது (Kill-Switch: OFF)" : "Connected (Kill-Switch: OFF)"}
          </span>
        </div>
        <span className="text-[11px] text-gray-500 mt-1 sm:mt-0 font-medium">
          {lang === "ta" ? "0 தவறவிட்ட கோரிக்கைகள் (Webhook Latency: 42ms)" : "0 unhandled requests (Webhook Latency: 42ms)"}
        </span>
      </div>
    </div>
  );
}
