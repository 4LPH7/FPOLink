"use client";

import React from "react";
import {
  Languages,
  Sprout,
  Smartphone,
  CheckCircle2,
  TrendingUp,
  Users,
  Bell,
  BarChart3,
} from "lucide-react";

interface NavbarProps {
  lang: "ta" | "en";
  setLang: (lang: "ta" | "en") => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  t: any;
}

export default function Navbar({
  lang,
  setLang,
  activeTab,
  setActiveTab,
  t,
}: NavbarProps) {
  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 transition-all shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & District Info */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-600 to-emerald-700 flex items-center justify-center text-white font-bold text-xl shadow-md shadow-green-600/20">
              <Sprout className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl text-gray-900 tracking-tight">
                  FPOLink <span className="text-green-600">TN</span>
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  {lang === "ta" ? "ஈரோடு மாவட்டம்" : "Erode District"}
                </span>
              </div>
              <p className="text-[11px] text-gray-500 font-medium hidden sm:block">
                {t.app.tagline}
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                activeTab === "dashboard"
                  ? "bg-green-50 text-green-700 font-semibold"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>{t.nav.dashboard}</span>
            </button>
            <button
              onClick={() => setActiveTab("prices")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                activeTab === "prices"
                  ? "bg-green-50 text-green-700 font-semibold"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>{t.nav.prices}</span>
            </button>
            <button
              onClick={() => setActiveTab("aggregation")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                activeTab === "aggregation"
                  ? "bg-green-50 text-green-700 font-semibold"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <Sprout className="w-4 h-4" />
              <span>{t.nav.aggregation}</span>
            </button>
            <button
              onClick={() => setActiveTab("farmers")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                activeTab === "farmers"
                  ? "bg-green-50 text-green-700 font-semibold"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <Users className="w-4 h-4" />
              <span>{t.nav.farmers}</span>
            </button>
            <button
              onClick={() => setActiveTab("alerts")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                activeTab === "alerts"
                  ? "bg-green-50 text-green-700 font-semibold"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`}
            >
              <Bell className="w-4 h-4" />
              <span>{t.nav.alerts}</span>
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>
            </button>
          </nav>

          {/* Right Action: Bot Status & Language Switcher */}
          <div className="flex items-center space-x-3">
            {/* Live Bot Pulse Badge */}
            <div className="hidden lg:inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-medium text-emerald-800">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <Smartphone className="w-3.5 h-3.5 text-emerald-700" />
              <span>{t.dashboard.bot_active}:</span>
              <span className="font-semibold">{t.dashboard.bot_status_live}</span>
            </div>

            {/* Language Switch Button */}
            <button
              onClick={() => setLang(lang === "ta" ? "en" : "ta")}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-lg text-xs font-semibold text-gray-700 bg-white hover:bg-gray-50 shadow-xs transition-all active:scale-95"
              title="மொழியை மாற்றவும் / Switch Language"
            >
              <Languages className="w-4 h-4 mr-1.5 text-green-600" />
              <span>{lang === "ta" ? "English" : "தமிழ்"}</span>
            </button>

            {/* FPO Staff Badge */}
            <div className="hidden sm:flex items-center space-x-2 pl-2 border-l border-gray-200 text-xs font-medium text-gray-700">
              <div className="w-8 h-8 rounded-full bg-green-100 text-green-800 flex items-center justify-center font-bold">
                E
              </div>
              <span className="text-gray-900 font-semibold">Kodumudi FPO</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
