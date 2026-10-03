"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Building2, LayoutDashboard, Menu, TrendingUp, Users } from "lucide-react";
import { Sidebar } from "@/components/shell/Sidebar";
import { Header } from "@/components/shell/Header";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n/context";
import { apiIsHealthy, useApiStatus } from "@/components/shell/ApiStatusContext";
import { getToken, passwordChangeRequired } from "@/lib/auth";

type MobileNavKey = "dashboard" | "prices" | "farmers" | "buyers";

const mobileItems: Array<{ href: string; labelKey: MobileNavKey; icon: typeof LayoutDashboard }> = [
  { href: "/", labelKey: "dashboard", icon: LayoutDashboard },
  { href: "/prices", labelKey: "prices", icon: TrendingUp },
  { href: "/farmers", labelKey: "farmers", icon: Users },
  { href: "/buyers", labelKey: "buyers", icon: Building2 },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const { t, lang } = useLanguage();
  const health = useApiStatus();
  const apiHealthy = apiIsHealthy(health);

  useEffect(() => {
    if (pathname === "/login") {
      setAuthenticated(true);
      return;
    }
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    if (passwordChangeRequired()) {
      if (pathname !== "/change-password") {
        router.replace("/change-password");
      }
      setAuthenticated(pathname === "/change-password");
      return;
    }
    setAuthenticated(true);
  }, [pathname, router]);

  if (pathname === "/login" || pathname === "/change-password") return <>{children}</>;
  if (!authenticated) return <div className="min-h-screen bg-background" aria-busy="true" />;

  return (
    <div className="min-h-screen bg-background antialiased">
      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="w-[min(19rem,88vw)] p-0">
          <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
        </SheetContent>
      </Sheet>

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col lg:flex">
        <Sidebar />
      </aside>

      <div className="flex min-h-screen min-w-0 flex-col lg:pl-64">
        <Header onOpenMobileMenu={() => setMobileMenuOpen(true)} />
        {health && !apiHealthy && (
          <div role="status" className="border-b border-amber-300 bg-amber-50 px-4 py-2.5 text-sm text-amber-950 sm:px-6 lg:px-8">
            <div className="mx-auto flex max-w-[1440px] items-start gap-2">
              <span className="mt-1 size-2 shrink-0 rounded-full bg-amber-600" aria-hidden="true" />
              <p>
                {t.app.api_degraded}
                <span className="ml-1 font-medium">{health.db}</span>
              </p>
            </div>
          </div>
        )}
        <main key={pathname} className="route-content mx-auto w-full max-w-[1440px] min-w-0 flex-1 space-y-6 px-4 py-5 pb-28 sm:px-6 sm:py-7 lg:px-8 lg:pb-10">
          {children}
        </main>
      </div>

      <nav aria-label="Primary navigation" className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-card/95 px-2 pb-[max(env(safe-area-inset-bottom),0.5rem)] pt-2 backdrop-blur lg:hidden">
        <div className="mx-auto grid max-w-lg grid-cols-5 gap-1">
          {mobileItems.map(({ href, labelKey, icon: Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted"
                )}
              >
                <Icon className="size-5" aria-hidden="true" />
                <span>{t.nav[labelKey]}</span>
              </Link>
            );
          })}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(true)}
            className="flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-medium text-muted-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label={lang === "ta" ? "மேலும் வழிசெலுத்தல்" : "More navigation"}
          >
            <Menu className="size-5" aria-hidden="true" />
            <span>{lang === "ta" ? "மேலும்" : "More"}</span>
          </button>
        </div>
      </nav>
    </div>
  );
}
