"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/shell/Sidebar";
import { Header } from "@/components/shell/Header";
import { Sheet, SheetContent } from "@/components/ui/sheet";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex flex-col antialiased">
      {/* Mobile & Tablet Drawer Navigation */}
      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="p-0 w-72 max-w-xs">
          <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
        </SheetContent>
      </Sheet>

      <div className="flex flex-1 min-h-screen">
        {/* Desktop Fixed Sidebar (visible >= 1024px) */}
        <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 z-30">
          <Sidebar />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
          <Header onOpenMobileMenu={() => setMobileMenuOpen(true)} />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
