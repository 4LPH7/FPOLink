"use client";

import React, { useState } from "react";
import en from "@/lib/i18n/en.json";
import ta from "@/lib/i18n/ta.json";
import Navbar from "@/components/Navbar";
import StatCard from "@/components/StatCard";
import PriceChart from "@/components/PriceChart";
import AlertPanel from "@/components/AlertPanel";
import MandiPricesTable from "@/components/MandiPricesTable";
import AggregationSummary from "@/components/AggregationSummary";
import FarmerInviteCard from "@/components/FarmerInviteCard";
import Footer from "@/components/Footer";
import {
  TrendingUp,
  Users,
  Sprout,
  Store,
  ShieldCheck,
  Smartphone,
  Sparkles,
  ArrowRight,
  Layers,
} from "lucide-react";

export default function Home() {
  const [lang, setLang] = useState<"ta" | "en">("ta");
  const [activeTab, setActiveTab] = useState("dashboard");

  const t = lang === "ta" ? ta : en;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900 selection:bg-green-100 selection:text-green-900">
      {/* Top App Bar & Language Switcher */}
      <Navbar
        lang={lang}
        setLang={setLang}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        t={t}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 flex-1">
        {/* Welcome Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-green-700 uppercase tracking-wider mb-1">
              <span>🌾 {t.app.district}</span>
              <span>•</span>
              <span>{t.app.sync_status}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
              {lang === "ta" ? "கொடுமுடி உழவர் உற்பத்தியாளர் நிறுவனம்" : "Kodumudi Farmer Producer Organization"}
            </h1>
            <p className="text-xs sm:text-sm text-gray-600 mt-1 max-w-3xl">
              {lang === "ta"
                ? "ஈரோடு மாவட்ட உழவர் உற்பத்தியாளர் நிறுவனங்களுக்கான நேரலை மண்டி விலை நுண்ணறிவு, தானியங்கி முரண்பாடு எச்சரிக்கைகள், மற்றும் அறுவடை ஒருங்கிணைப்பு தளம்."
                : "Real-time mandi price intelligence, MAD anomaly telemetry, and grade-sorted harvest aggregation for Erode District FPOs."}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href="https://wa.me/919876543210?text=%E0%AE%B5%E0%AE%A3%E0%AE%95%E0%AF%8D%E0%AE%95%E0%AE%AE%E0%AF%8D"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold text-white bg-green-600 hover:bg-green-700 shadow-sm transition-all active:scale-95"
            >
              <Smartphone className="w-4 h-4 mr-2" />
              {lang === "ta" ? "WhatsApp பாட் திறக்க" : "Open WhatsApp Bot"}
            </a>
          </div>
        </div>

        {/* Primary KPI Overview Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          <StatCard
            title={t.dashboard.members}
            value="1,250"
            subtitle={lang === "ta" ? "ஈரோடு & கொடுமுடி" : "Erode & Kodumudi"}
            change="+12%"
            changeType="positive"
            icon={Users}
            iconColor="text-green-600 bg-green-50"
          />

          <StatCard
            title={t.dashboard.todays_produce}
            value="8,400 kg"
            subtitle={lang === "ta" ? "மஞ்சள் & வாழை" : "Turmeric & Banana"}
            change="+8.4%"
            changeType="positive"
            icon={Sprout}
            iconColor="text-yellow-600 bg-yellow-50"
          />

          <StatCard
            title={t.dashboard.turmeric_rate}
            value="₹12,480"
            subtitle="பெருந்துறை மண்டி (Perundurai)"
            change="+2.4%"
            changeType="positive"
            icon={TrendingUp}
            iconColor="text-emerald-600 bg-emerald-50"
            badge="Agmarknet"
          />

          <StatCard
            title={t.dashboard.banana_rate}
            value="₹2,920"
            subtitle="கொடுமுடி மண்டி (Kodumudi)"
            change="+1.8%"
            changeType="positive"
            icon={TrendingUp}
            iconColor="text-blue-600 bg-blue-50"
            badge="Agmarknet"
          />
        </section>

        {/* Dynamic Tab Views */}
        {(activeTab === "dashboard" || activeTab === "prices") && (
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Interactive Price Chart (Spans 2 Columns) */}
            <div className="lg:col-span-2 space-y-6">
              <PriceChart lang={lang} t={t} />
              <MandiPricesTable lang={lang} t={t} />
            </div>

            {/* Alert & Notice Panel (Spans 1 Column) */}
            <div className="space-y-6">
              <AlertPanel lang={lang} t={t} />
              <AggregationSummary lang={lang} t={t} />
            </div>
          </section>
        )}

        {activeTab === "aggregation" && (
          <section className="space-y-6">
            <AggregationSummary lang={lang} t={t} />
            <MandiPricesTable lang={lang} t={t} />
          </section>
        )}

        {activeTab === "farmers" && (
          <section className="space-y-6">
            <FarmerInviteCard lang={lang} t={t} />
            <AggregationSummary lang={lang} t={t} />
          </section>
        )}

        {activeTab === "alerts" && (
          <section className="space-y-6">
            <AlertPanel lang={lang} t={t} />
            <PriceChart lang={lang} t={t} />
          </section>
        )}

        {/* Farmer Onboarding & WhatsApp Invite Hub (Always visible on dashboard bottom) */}
        {activeTab === "dashboard" && (
          <section>
            <FarmerInviteCard lang={lang} t={t} />
          </section>
        )}
      </main>

      {/* Footer */}
      <Footer lang={lang} />
    </div>
  );
}
