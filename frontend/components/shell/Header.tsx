"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Menu, MessageSquare, ChevronRight } from "lucide-react";
import { useLanguage } from "@/lib/i18n/context";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const pageTitles: Record<string, { en: string; ta: string }> = {
  "/": { en: "Executive Dashboard", ta: "நிர்வாகக் கட்டுப்பாட்டு பலகை" },
  "/prices": { en: "Market Prices & ML Forecasts", ta: "சந்தை விலைகள் & முன்கணிப்புகள்" },
  "/farmers": { en: "Farmer Directory & DPDP Consent", ta: "உழவர் பதிவேடு & ஒப்புதல் நிலை" },
  "/admin": { en: "Ingestion Adapters & Ops Health", ta: "தரவு இணைப்பிகள் & செயல்பாடுகள்" },
  "/whatsapp": { en: "WhatsApp Bot Live Monitor", ta: "வாட்ஸ்அப் போட் நேரலை கண்காணிப்பு" },
};

export function Header({
  onOpenMobileMenu,
}: {
  onOpenMobileMenu: () => void;
}) {
  const pathname = usePathname();
  const { lang } = useLanguage();

  const currentTitle = pageTitles[pathname] || {
    en: "FPO Operations",
    ta: "FPO செயல்பாடுகள்",
  };

  return (
    <header className="h-16 bg-card/95 backdrop-blur-md border-b border-border sticky top-0 z-40 px-4 sm:px-6 flex items-center justify-between transition-colors shadow-2xs">
      <div className="flex items-center space-x-3 min-w-0">
        {/* Mobile/Tablet menu trigger button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onOpenMobileMenu}
          className="lg:hidden shrink-0 text-muted-foreground hover:text-foreground h-9 w-9"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </Button>

        {/* Breadcrumb / Page Title */}
        <div className="flex items-center space-x-2 min-w-0">
          <span className="text-xs font-medium text-muted-foreground hidden sm:inline">
            FPOLink
          </span>
          <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/60 hidden sm:inline shrink-0" />
          <h1 className="text-sm sm:text-base font-bold text-foreground truncate">
            {lang === "ta" ? currentTitle.ta : currentTitle.en}
          </h1>
        </div>
      </div>

      {/* Right Controls: FPO Badge, Bot Status Pill, Language Switcher */}
      <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
        {/* District & FPO Badge (hidden on small mobile, visible on tablet+) */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="truncate max-w-[140px]">
            {lang === "ta" ? "கொடுமுடி • ஈரோடு" : "Kodumudi • Erode"}
          </span>
        </div>

        {/* WhatsApp Bot Status Pill */}
        <div className="hidden sm:flex items-center space-x-1 px-2 py-1 rounded-md text-xs font-medium bg-muted/60 text-muted-foreground border border-border">
          <MessageSquare className="w-3.5 h-3.5 text-primary shrink-0" />
          <span className="text-[11px] font-semibold text-foreground">
            {lang === "ta" ? "போட்: தயார்" : "Bot: Active"}
          </span>
        </div>

        {/* Language Switcher */}
        <LanguageSwitcher />
      </div>
    </header>
  );
}
