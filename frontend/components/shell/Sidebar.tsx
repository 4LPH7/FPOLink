"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  Activity,
  MessageSquare,
  Sprout,
  Building2,
  GitCompare,
  ListTodo,
  Send,
} from "lucide-react";
import { useLanguage } from "@/lib/i18n/context";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  labelKey: "dashboard" | "prices" | "farmers" | "buyers" | "matching" | "admin" | "whatsapp" | "tasks" | "telegram";
  icon: React.ComponentType<{ className?: string }>;
  badgeKey?: string;
}

const navItems: NavItem[] = [
  { href: "/", labelKey: "dashboard", icon: LayoutDashboard },
  { href: "/prices", labelKey: "prices", icon: TrendingUp },
  { href: "/farmers", labelKey: "farmers", icon: Users },
  { href: "/buyers", labelKey: "buyers", icon: Building2 },
  { href: "/matching", labelKey: "matching", icon: GitCompare },
  { href: "/admin", labelKey: "admin", icon: Activity },
  { href: "/tasks", labelKey: "tasks", icon: ListTodo },
  { href: "/telegram", labelKey: "telegram", icon: Send },
  { href: "/whatsapp", labelKey: "whatsapp", icon: MessageSquare },
];

export function Sidebar({
  className,
  onNavigate,
}: {
  className?: string;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { lang, t } = useLanguage();

  return (
    <aside
      className={cn(
        "flex h-full select-none flex-col border-r border-border bg-card",
        className
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 shrink-0 items-center gap-3 border-b border-border px-5">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Sprout className="size-5" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <span className="font-extrabold text-lg text-foreground tracking-tight">
              FPOLink
            </span>
            <span className="text-primary font-bold text-lg">TN</span>
            <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">
              v0.1
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground font-medium truncate max-w-[150px]">
            {lang === "ta" ? "தமிழ்நாடு முழுவதும்" : "Tamil Nadu Statewide"}
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav aria-label={lang === "ta" ? "முக்கிய வழிசெலுத்தல்" : "Main navigation"} className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          {lang === "ta" ? "முக்கிய பக்கங்கள்" : "Main Navigation"}
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "group flex min-h-11 items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                isActive
                  ? "bg-primary/10 text-primary font-semibold shadow-2xs"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <Icon
                  className={cn(
                    "size-[18px] shrink-0",
                    isActive ? "text-primary" : "text-muted-foreground"
                  )}
                />
                <span className="truncate">{t.nav[item.labelKey]}</span>
              </div>
              {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Status Card */}
      <div className="shrink-0 border-t border-border p-4">
        <div className="rounded-xl bg-muted/60 px-3 py-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            {lang === "ta" ? "உங்கள் பணியிடம்" : "Your workspace"}
          </p>
          <p className="mt-1 truncate text-sm font-semibold text-foreground">
            {lang === "ta" ? "கொடுமுடி FPO" : "Kodumudi FPO"}
          </p>
        </div>
      </div>
    </aside>
  );
}
