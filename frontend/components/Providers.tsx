"use client";

import React from "react";
import { LanguageProvider } from "@/lib/i18n/context";
import { AppShell } from "@/components/shell/AppShell";
import { ApiStatusProvider } from "@/components/shell/ApiStatusContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <ApiStatusProvider>
        <AppShell>{children}</AppShell>
      </ApiStatusProvider>
    </LanguageProvider>
  );
}
