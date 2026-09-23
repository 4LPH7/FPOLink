"use client";

import React from "react";
import { LanguageProvider } from "@/lib/i18n/context";
import { AppShell } from "@/components/shell/AppShell";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <AppShell>{children}</AppShell>
    </LanguageProvider>
  );
}
