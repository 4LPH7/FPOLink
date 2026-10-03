"use client";

import React from "react";
import { Languages } from "lucide-react";
import { useLanguage } from "@/lib/i18n/context";
import { Button } from "@/components/ui/button";

export function LanguageSwitcher() {
  const { lang, toggleLang } = useLanguage();

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLang}
      className="flex h-10 items-center gap-1.5 border-border/80 px-2.5 text-xs font-semibold shadow-2xs hover:border-primary/50 hover:bg-accent sm:gap-2"
      title={lang === "ta" ? "Switch to English" : "தமிழுக்கு மாற்றவும்"}
    >
      <Languages className="w-3.5 h-3.5 text-primary" />
      <span className="hidden font-bold sm:inline">
        {lang === "ta" ? "தமிழ்" : "English"}
      </span>
      <span className="text-[10px] uppercase font-bold text-muted-foreground px-1 py-0.2 rounded bg-muted">
        {lang === "ta" ? "TA" : "EN"}
      </span>
    </Button>
  );
}
