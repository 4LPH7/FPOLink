"use client";

import React from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n/context";
import StatCard from "@/components/StatCard";
import PriceChart from "@/components/PriceChart";
import AlertPanel from "@/components/AlertPanel";
import AggregationSummary from "@/components/AggregationSummary";
import FarmerInviteCard from "@/components/FarmerInviteCard";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  Users,
  Store,
  Smartphone,
  ArrowRight,
  ShieldCheck,
  Activity,
  Layers,
} from "lucide-react";

export default function DashboardHome() {
  const { lang, t } = useLanguage();

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
          value="1,250"
          subtitle={lang === "ta" ? "ஈரோடு & கொடுமுடி" : "Erode & Kodumudi"}
          change="+12%"
          changeType="positive"
          icon={Users}
          iconColor="text-emerald-700 bg-emerald-50 dark:bg-emerald-950"
        />
        <StatCard
          title={t.dashboard.turmeric_rate}
          value="₹12,350"
          subtitle={lang === "ta" ? "பெருந்துறை மண்டி (நேற்று: ₹12,200)" : "Perundurai (Prev: ₹12,200)"}
          change="+1.2%"
          changeType="positive"
          icon={TrendingUp}
          iconColor="text-amber-700 bg-amber-50 dark:bg-amber-950"
          badge={t.dashboard.hold_signal}
        />
        <StatCard
          title={t.dashboard.todays_produce}
          value="4.8 Tonnes"
          subtitle={lang === "ta" ? "மஞ்சள் (3.2T) • வாழை (1.6T)" : "Turmeric (3.2T) • Banana (1.6T)"}
          change="+24%"
          changeType="positive"
          icon={Store}
          iconColor="text-blue-700 bg-blue-50 dark:bg-blue-950"
        />
        <StatCard
          title={t.dashboard.bot_active}
          value={t.dashboard.bot_status_live}
          subtitle={lang === "ta" ? "98.4% விடை நேரம் (<2 விநாடி)" : "98.4% uptime (<2s latency)"}
          icon={Smartphone}
          iconColor="text-emerald-700 bg-emerald-50 dark:bg-emerald-950"
          badge="Live"
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
