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
      className="flex items-center space-x-2 border-border/80 hover:border-primary/50 text-xs font-semibold px-2.5 py-1.5 h-8 bg-card shadow-2xs hover:bg-accent"
      title={lang === "ta" ? "Switch to English" : "தமிழுக்கு மாற்றவும்"}
    >
      <Languages className="w-3.5 h-3.5 text-primary" />
      <span className="font-bold">
        {lang === "ta" ? "தமிழ்" : "English"}
      </span>
      <span className="text-[10px] uppercase font-bold text-muted-foreground px-1 py-0.2 rounded bg-muted">
        {lang === "ta" ? "TA" : "EN"}
      </span>
    </Button>
  );
}
