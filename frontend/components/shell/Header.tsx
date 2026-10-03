"use client";

import React from "react";
import { usePathname, useRouter } from "next/navigation";
import { Activity, ChevronRight, LogOut, Menu, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/i18n/context";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { Button } from "@/components/ui/button";
import { apiIsHealthy, useApiStatus } from "@/components/shell/ApiStatusContext";
import { clearTokens } from "@/lib/auth";
import { CommandPalette } from "@/components/shell/CommandPalette";

const pageTitles: Record<string, { en: string; ta: string }> = {
  "/": { en: "Overview", ta: "கண்ணோட்டம்" },
  "/prices": { en: "Market prices", ta: "சந்தை விலைகள்" },
  "/farmers": { en: "Farmers", ta: "விவசாயிகள்" },
  "/admin": { en: "Data operations", ta: "தரவு செயல்பாடுகள்" },
  "/admin/commodities": { en: "Commodity catalogue", ta: "பொருள் பட்டியல்" },
  "/whatsapp": { en: "WhatsApp activity", ta: "வாட்ஸ்அப் செயல்பாடு" },
  "/buyers": { en: "Buyers", ta: "கொள்முதலாளர்கள்" },
  "/matching": { en: "Demand matching", ta: "தேவை பொருத்தம்" },
};

export function Header({ onOpenMobileMenu }: { onOpenMobileMenu: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const { lang } = useLanguage();
  const health = useApiStatus();
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen((open) => !open);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const title = pageTitles[pathname] || { en: "FPO workspace", ta: "FPO செயல்பாடுகள்" };
  const healthy = apiIsHealthy(health);

  return (
    <header className="sticky top-0 z-20 flex min-h-16 items-center justify-between gap-3 border-b border-border bg-card/95 px-3 backdrop-blur sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-2 sm:gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={onOpenMobileMenu}
          className="size-11 shrink-0 lg:hidden"
          aria-label={lang === "ta" ? "வழிசெலுத்தலைத் திற" : "Open navigation menu"}
        >
          <Menu className="size-5" />
        </Button>
        <div className="hidden items-center gap-2 text-xs font-medium text-muted-foreground sm:flex">
          <span>FPOLink</span>
          <ChevronRight className="size-3.5" aria-hidden="true" />
        </div>
        <h1 className="truncate text-base font-semibold tracking-tight text-foreground sm:text-lg">
          {lang === "ta" ? title.ta : title.en}
        </h1>
      </div>

      <div className="flex min-w-0 shrink-0 items-center gap-1.5 sm:gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPaletteOpen(true)}
          className="h-10 min-w-10 gap-2 px-2.5 text-muted-foreground sm:w-52 sm:justify-start"
          aria-label={lang === "ta" ? "தேடல் மற்றும் வழிசெலுத்தல்" : "Search and navigate"}
        >
          <Search className="size-4 shrink-0" />
          <span className="hidden flex-1 text-left text-xs font-normal sm:inline">{lang === "ta" ? "தேடுக..." : "Search anything..."}</span>
          <kbd className="hidden rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium sm:inline">⌘K</kbd>
        </Button>
        <div
          role="status"
          aria-live="polite"
          title={health ? `${health.service}: ${health.status}; database: ${health.db}` : "Checking API status"}
          className="inline-flex min-h-9 items-center gap-2 rounded-full border border-border px-2.5 text-xs font-medium sm:px-3"
        >
            <span className={`size-2 rounded-full ${healthy ? "bg-emerald-600" : health ? "bg-amber-500" : "bg-muted-foreground"}`} />
          <Activity className="hidden size-3.5 text-muted-foreground sm:block" aria-hidden="true" />
          <span className="hidden sm:inline">
            {!health
              ? (lang === "ta" ? "API சரிபார்க்கிறது" : "Checking API")
              : healthy
                ? (lang === "ta" ? "API இயங்குகிறது" : "API healthy")
                : (lang === "ta" ? "API கவனம் தேவை" : "API attention")}
          </span>
          <span className="sm:hidden">{health ? (healthy ? "API" : "Check") : "…"}</span>
        </div>
        <LanguageSwitcher />
        <Button variant="ghost" size="icon" className="size-10" aria-label={lang === "ta" ? "வெளியேறு" : "Sign out"} title={lang === "ta" ? "வெளியேறு" : "Sign out"} onClick={() => { clearTokens(); router.replace("/login"); }}>
          <LogOut className="size-4" />
        </Button>
      </div>
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </header>
  );
}
