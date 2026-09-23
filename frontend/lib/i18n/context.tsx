"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import en from "./en.json";
import ta from "./ta.json";

export type Language = "ta" | "en";
export type Translations = typeof ta;

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  toggleLang: () => void;
  t: Translations;
  isTamil: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = "fpolink_lang";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  // Default to Tamil as required by FPOLink TN specification
  const [lang, setLangState] = useState<Language>("ta");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as Language | null;
      if (saved === "ta" || saved === "en") {
        setLangState(saved);
        document.documentElement.lang = saved;
      } else {
        document.documentElement.lang = "ta";
      }
    } catch {
      // localStorage may fail in private browsing or iframe
    }
  }, []);

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    if (typeof document !== "undefined") {
      document.documentElement.lang = newLang;
    }
    try {
      localStorage.setItem(STORAGE_KEY, newLang);
    } catch {
      // localStorage failure fallback
    }
  };

  const toggleLang = () => {
    setLang(lang === "ta" ? "en" : "ta");
  };

  const t = (lang === "ta" ? ta : en) as unknown as Translations;

  return (
    <LanguageContext.Provider
      value={{
        lang,
        setLang,
        toggleLang,
        t,
        isTamil: lang === "ta",
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
