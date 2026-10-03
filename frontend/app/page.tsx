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
  const [turmericPriceDate, setTurmericPriceDate] = useState<string | null>(null);
  const [marketCheckedAt, setMarketCheckedAt] = useState<Date | null>(null);
  const [botEnabled, setBotEnabled] = useState<boolean | null>(null);
  const [botAvailable, setBotAvailable] = useState(false);

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
        setBotAvailable(wa.available);

        // Turmeric modal price from latest prices
        const turmericPrice = prices.find(
          (p) => p.crop_name?.toLowerCase().includes("turmeric") || p.crop_name?.toLowerCase().includes("மஞ்சள்")
        );
        setMarketCheckedAt(new Date());
        if (turmericPrice) {
          setTurmericRate(
            `₹${Number(turmericPrice.modal_price).toLocaleString("en-IN")}`
          );
          setTurmericPriceDate(turmericPrice.price_date);
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

  useEffect(() => {
    let active = true;
    let inFlight = false;

    const refreshMarketPrice = async () => {
      if (!active || inFlight || document.visibilityState !== "visible") return;
      inFlight = true;
      try {
        const prices = await getLatestPrices("Erode");
        if (!active) return;
        const turmericPrice = prices.find(
          (price) => price.crop_name?.toLowerCase().includes("turmeric") || price.crop_name?.toLowerCase().includes("மஞ்சள்")
        );
        if (turmericPrice) {
          setTurmericRate(`₹${Number(turmericPrice.modal_price).toLocaleString("en-IN")}`);
          setTurmericPriceDate(turmericPrice.price_date);
        }
        setMarketCheckedAt(new Date());
      } catch (err) {
        console.warn("Dashboard market price refresh failed:", err);
      } finally {
        inFlight = false;
      }
    };

    const interval = window.setInterval(() => void refreshMarketPrice(), 60_000);
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") void refreshMarketPrice();
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
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
      <div className="relative overflow-hidden rounded-2xl border border-emerald-900/10 bg-emerald-950 p-5 text-white shadow-xs sm:p-7">
        <div className="relative z-10 max-w-3xl space-y-2">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-white/15 text-emerald-100 text-xs font-semibold backdrop-blur-xs">
            <span>🌾 {t.app.district}</span>
            <span>•</span>
            <span>{lang === "ta" ? "கொடுமுடி FPO" : "Kodumudi FPO"}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {lang === "ta"
              ? "கொடுமுடி உழவர் உற்பத்தியாளர் நிறுவனம்"
              : "Kodumudi Farmer Producer Organization"}
          </h1>
          <p className="max-w-2xl text-sm leading-relaxed text-emerald-50/85 sm:text-base">
            {lang === "ta"
              ? "ஈரோடு மாவட்ட FPO செயல்பாடுகளுக்கான சந்தை விலைத் தகவல், அறுவடை மதிப்பீடு மற்றும் கொள்முதல் ஒருங்கிணைப்பு."
              : "Market prices, harvest estimates and buyer coordination for Erode District FPO operations."}
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
          subtitle={[
            turmericPriceDate ? `${lang === "ta" ? "விலை தேதி" : "Price date"}: ${turmericPriceDate}` : (lang === "ta" ? "சந்தைத் தரவு இல்லை" : "No market record"),
            marketCheckedAt ? `${lang === "ta" ? "சரிபார்த்தது" : "Checked"} ${marketCheckedAt.toLocaleTimeString(lang === "ta" ? "ta-IN" : "en-IN", { hour: "2-digit", minute: "2-digit" })}` : null,
          ].filter(Boolean).join(" · ")}
          icon={TrendingUp}
          iconColor="text-amber-700 bg-amber-50 dark:bg-amber-950"
        />
        <StatCard
          title={lang === "ta" ? "செயலில் உள்ள அறுவடை மதிப்பீடு" : "Active harvest estimates"}
          value={activeHarvestTonnes}
          subtitle={cropBreakdown}
          icon={Store}
          iconColor="text-blue-700 bg-blue-50 dark:bg-blue-950"
        />
        <StatCard
          title={t.dashboard.bot_active}
          value={
            !botAvailable
              ? "—"
              : botEnabled
              ? (lang === "ta" ? "அமைப்பில் இயக்கப்பட்டுள்ளது" : "Enabled by configuration")
              : lang === "ta"
              ? "இயக்கம் நிறுத்தப்பட்டது"
              : "Kill-Switch ON"
          }
          subtitle={lang === "ta" ? "செய்தி சேவை இயக்க நிலை" : "Messaging service setting"}
          icon={Smartphone}
          iconColor="text-emerald-700 bg-emerald-50 dark:bg-emerald-950"
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
