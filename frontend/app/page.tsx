"use client";

import { useState } from "react";
import en from "@/lib/i18n/en.json";
import ta from "@/lib/i18n/ta.json";
import {
  TrendingUp,
  Users,
  Sprout,
  Store,
  Calendar,
  Languages,
  ArrowUpRight,
  ShieldCheck,
  Smartphone,
} from "lucide-react";

export default function Home() {
  const [lang, setLang] = useState<"ta" | "en">("ta");
  const t = lang === "ta" ? ta : en;

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-green-600 flex items-center justify-center text-white font-bold text-xl shadow-sm">
              F
            </div>
            <div>
              <span className="font-bold text-lg text-gray-900 tracking-tight">
                FPOLink TN
              </span>
              <span className="ml-2 text-xs bg-green-100 text-green-800 font-semibold px-2 py-0.5 rounded-full">
                ஈரோடு / Erode
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => setLang(lang === "ta" ? "en" : "ta")}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm transition-colors"
            >
              <Languages className="w-4 h-4 mr-1.5 text-gray-500" />
              {lang === "ta" ? "English" : "தமிழ்"}
            </button>
            <a
              href="/login"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 shadow-sm transition-colors"
            >
              {lang === "ta" ? "உள்நுழை" : "Sign In"}
            </a>
          </div>
        </div>
      </header>

      {/* Hero / Stat Overview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            {t.app.tagline}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            {lang === "ta"
              ? "ஈரோடு மாவட்ட உழவர் உற்பத்தியாளர் நிறுவனங்களுக்கான டிஜிட்டல் விலை நுண்ணறிவு மற்றும் அறுவடை தளம்"
              : "Digital price intelligence and harvest aggregation for Erode Farmer Producer Organizations"}
          </p>
        </div>

        {/* Primary Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase">
                {t.dashboard.members}
              </span>
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-2">1,250</p>
            <span className="text-xs text-green-600 font-medium flex items-center mt-1">
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> +12%{" "}
              {lang === "ta" ? "இந்த மாதம்" : "this month"}
            </span>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase">
                {t.dashboard.todays_produce}
              </span>
              <Sprout className="w-5 h-5 text-yellow-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-2">8,400 kg</p>
            <span className="text-xs text-gray-500 mt-1 block">
              {lang === "ta" ? "மஞ்சள் & வாழை" : "Turmeric & Banana"}
            </span>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase">
                {lang === "ta" ? "மஞ்சள் விலை (ஈரோடு)" : "Turmeric Mandi Rate"}
              </span>
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-2">₹12,050 / q</p>
            <span className="text-xs text-green-600 font-medium flex items-center mt-1">
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> +3.5% (Agmarknet)
            </span>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase">
                {lang === "ta" ? "வாட்ஸ்அப் பாட்" : "WhatsApp Bot"}
              </span>
              <Smartphone className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              {lang === "ta" ? "செயலில்" : "Active"}
            </p>
            <span className="text-xs text-gray-500 mt-1 block">
              {lang === "ta" ? "விலை, வானிலை, அறுவடை" : "Prices, Weather, Harvest"}
            </span>
          </div>
        </div>

        {/* Feature Overview Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center text-green-700 mb-4">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 text-lg">
              {t.dashboard.market_prices}
            </h3>
            <p className="text-sm text-gray-600 mt-2 leading-relaxed">
              {lang === "ta"
                ? "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடங்கள் மற்றும் மண்டிகளின் தினசரி மாதிரி, குறைந்தபட்ச மற்றும் அதிகபட்ச விலைகள்."
                : "Real daily modal, min, and max wholesale prices from Erode regulated markets and mandis."}
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center text-yellow-700 mb-4">
              <Store className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 text-lg">
              {t.nav.aggregation}
            </h3>
            <p className="text-sm text-gray-600 mt-2 leading-relaxed">
              {lang === "ta"
                ? "விவசாயிகளின் சிறிய விளைச்சல்களை தரவாரியாக (Grade A/B/C) தொகுத்து மொத்தமாக விற்பனை செய்தல்."
                : "Aggregate smallholder farm harvests into uniform, grade-sorted wholesale commercial batches."}
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700 mb-4">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 text-lg">
              DPDP Act & {lang === "ta" ? "பாதுகாப்பு" : "Security"}
            </h3>
            <p className="text-sm text-gray-600 mt-2 leading-relaxed">
              {lang === "ta"
                ? "விவசாயிகளின் தனிநபர் தரவு பாதுகாப்பு, வெளிப்படையான ஒப்புதல் மற்றும் பாதுகாப்பான Argon2id அங்கீகாரம்."
                : "Compliant consent logging, phone masking, and cryptographic Argon2id password authentication."}
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500">
          <p>FPOLink TN © 2026. MIT License.</p>
          <p className="mt-2 sm:mt-0">
            {lang === "ta"
              ? "தமிழ்நாடு உழவர் உற்பத்தியாளர் நிறுவனங்களுக்காக அர்ப்பணிக்கப்பட்டது"
              : "Dedicated to Farmer Producer Organizations of Tamil Nadu"}
          </p>
        </div>
      </footer>
    </main>
  );
}
