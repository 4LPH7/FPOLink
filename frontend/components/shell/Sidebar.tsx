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
  ShieldCheck,
  Radio,
  Building2,
  GitCompare,
} from "lucide-react";
import { useLanguage } from "@/lib/i18n/context";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface NavItem {
  href: string;
  labelKey: "dashboard" | "prices" | "farmers" | "buyers" | "matching" | "admin" | "whatsapp";
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
        "flex flex-col h-full bg-card border-r border-border select-none",
        className
      )}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-border space-x-3 shrink-0">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-emerald-700 flex items-center justify-center text-white shadow-xs">
          <Sprout className="w-5 h-5 text-white" />
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
            {lang === "ta" ? "ஈரோடு மாவட்டம்" : "Erode District"}
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground/80">
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
                "flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all group",
                isActive
                  ? "bg-primary/10 text-primary font-semibold shadow-2xs"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <Icon
                  className={cn(
                    "w-4 h-4 shrink-0 transition-transform group-hover:scale-110",
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
      </div>

      {/* Bottom Status Card */}
      <div className="p-4 border-t border-border bg-muted/20 shrink-0">
        <div className="rounded-lg p-3 bg-card border border-border/80 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
              {lang === "ta" ? "நிலை" : "Operations"}
            </span>
            <Badge variant="success" className="text-[10px] px-1.5 py-0">
              <Radio className="w-2.5 h-2.5 mr-1 text-emerald-600 animate-pulse" />
              {lang === "ta" ? "நேரலை" : "Live"}
            </Badge>
          </div>
          <div className="text-xs font-semibold text-foreground truncate">
            {lang === "ta"
              ? "கொடுமுடி FPO"
              : "Kodumudi FPO"}
          </div>
          <div className="flex items-center space-x-1.5 text-[11px] text-muted-foreground">
            <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
            <span className="truncate">
              {lang === "ta" ? "DPDP தரவுப் பாதுகாப்பு" : "DPDP Protected"}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
