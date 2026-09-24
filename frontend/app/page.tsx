"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n/context";
import StatCard from "@/components/StatCard";
import PriceChart from "@/components/PriceChart";
import AlertPanel from "@/components/AlertPanel";
import AggregationSummary from "@/components/AggregationSummary";
import FarmerInviteCard from "@/components/FarmerInviteCard";
import {
  TrendingUp,
  Users,
  Store,
  Smartphone,
} from "lucide-react";
import {
  getFPOs,
  getLatestPrices,
  getFPODashboard,
  getWhatsAppActivity,
  FPODashboardStats,
} from "@/lib/api";
import { ensureToken } from "@/lib/auth";

const FPO_ID = process.env.NEXT_PUBLIC_FPO_ID || "d7342e5d-bac6-466e-a18b-366133137074";

export default function DashboardHome() {
  const { lang, t } = useLanguage();

  const [stats, setStats] = useState<FPODashboardStats | null>(null);
  const [turmericRate, setTurmericRate] = useState<string | null>(null);
  const [botEnabled, setBotEnabled] = useState<boolean | null>(null);

  useEffect(() => {
    async function loadKPIs() {
      try {
        const [token, prices, wa] = await Promise.all([
          ensureToken(),
          getLatestPrices("Erode"),
          getWhatsAppActivity(1),
        ]);

        // WhatsApp bot status
        setBotEnabled(wa.enabled);

        // Turmeric modal price from latest prices
        const turmericPrice = prices.find(
          (p) => p.crop_name?.toLowerCase().includes("turmeric") || p.crop_name?.toLowerCase().includes("மஞ்சள்")
        );
        if (turmericPrice) {
          setTurmericRate(
            `₹${Number(turmericPrice.modal_price).toLocaleString("en-IN")}`
          );
        }

        // Dashboard stats (requires auth)
        if (token) {
          const dash = await getFPODashboard(FPO_ID, token);
          setStats(dash);
        }
      } catch (err) {
        console.warn("Dashboard KPI load error:", err);
      }
    }
    loadKPIs();
  }, []);

  const memberCount = stats
    ? stats.member_count.toLocaleString("en-IN")
    : "—";

  const activeHarvestTonnes = stats
    ? stats.active_harvests_kg > 0
      ? `${(stats.active_harvests_kg / 1000).toFixed(1)} T`
      : "0 T"
    : "—";

  const cropBreakdown = stats?.crop_distribution
    ? Object.entries(stats.crop_distribution)
        .slice(0, 2)
        .map(([name]) => name)
        .join(" • ") || "—"
    : "—";

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="rounded-xl bg-gradient-to-r from-emerald-800 via-emerald-700 to-green-800 p-6 text-white shadow-xs relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-2">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-white/15 text-emerald-100 text-xs font-semibold backdrop-blur-xs">
            <span>🌾 {t.app.district}</span>
            <span>•</span>
            <span>{t.app.sync_status}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {lang === "ta"
              ? "கொடுமுடி உழவர் உற்பத்தியாளர் நிறுவனம்"
              : "Kodumudi Farmer Producer Organization"}
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 leading-tamil-relaxed">
            {lang === "ta"
              ? "ஈரோடு மாவட்ட உழவர் உற்பத்தியாளர் நிறுவனங்களுக்கான நேரலை மண்டி விலை நுண்ணறிவு, தானியங்கி முரண்பாடு எச்சரிக்கைகள், மற்றும் அறுவடை ஒருங்கிணைப்பு தளம்."
              : "Real-time mandi price intelligence, MAD anomaly telemetry, and grade-sorted harvest aggregation for Erode District FPOs."}
          </p>
        </div>
      </div>

      {/* Primary KPI Overview Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t.dashboard.members}
          value={memberCount}
          subtitle={lang === "ta" ? "ஈரோடு & கொடுமுடி" : "Erode & Kodumudi"}
          icon={Users}
          iconColor="text-emerald-700 bg-emerald-50 dark:bg-emerald-950"
        />
        <StatCard
          title={t.dashboard.turmeric_rate}
          value={turmericRate ?? "—"}
          subtitle={lang === "ta" ? "பெருந்துறை மண்டி (Agmarknet)" : "Perundurai mandi (Agmarknet)"}
          icon={TrendingUp}
          iconColor="text-amber-700 bg-amber-50 dark:bg-amber-950"
          badge={turmericRate ? t.dashboard.hold_signal : undefined}
        />
        <StatCard
          title={t.dashboard.todays_produce}
          value={activeHarvestTonnes}
          subtitle={cropBreakdown}
          icon={Store}
          iconColor="text-blue-700 bg-blue-50 dark:bg-blue-950"
        />
        <StatCard
          title={t.dashboard.bot_active}
          value={
            botEnabled === null
              ? "—"
              : botEnabled
              ? t.dashboard.bot_status_live
              : lang === "ta"
              ? "இயக்கம் நிறுத்தப்பட்டது"
              : "Kill-Switch ON"
          }
          subtitle={lang === "ta" ? "WhatsApp Cloud API நிலை" : "WhatsApp Cloud API status"}
          icon={Smartphone}
          iconColor="text-emerald-700 bg-emerald-50 dark:bg-emerald-950"
          badge={botEnabled ? "Live" : undefined}
        />
      </section>

      {/* Main Grid: Forecast & Alert Telemetry */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <PriceChart lang={lang} t={t} />
        </div>
        <div className="space-y-6">
          <AlertPanel lang={lang} t={t} />
          <AggregationSummary lang={lang} t={t} />
        </div>
      </section>

      {/* Farmer Onboarding Hub */}
      <section>
        <FarmerInviteCard lang={lang} t={t} onNavigateFarmerList={() => {}} />
      </section>
    </div>
  );
}
