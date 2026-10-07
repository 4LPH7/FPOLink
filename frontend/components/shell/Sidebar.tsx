"use client";

import React, { useState, useEffect, useMemo } from "react";
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
import { useDistrict } from "@/lib/district-context";
import { getFPOs, FPO } from "@/lib/api";
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

const TAMIL_DISTRICT_MAP: Record<string, string> = {
  ariyalur: "அரியலூர்",
  chengalpattu: "செங்கல்பட்டு",
  chennai: "சென்னை",
  coimbatore: "கோயம்புத்தூர்",
  cuddalore: "கடலூர்",
  dharmapuri: "தர்மபுரி",
  dindigul: "திண்டுக்கல்",
  erode: "ஈரோடு",
  kallakurichi: "கள்ளக்குறிச்சி",
  kanchipuram: "காஞ்சிபுரம்",
  kanyakumari: "கன்னியாகுமரி",
  karur: "கரூர்",
  krishnagiri: "கிருஷ்ணகிரி",
  madurai: "மதுரை",
  mayiladuthurai: "மயிலாடுதுறை",
  nagapattinam: "நாகப்பட்டினம்",
  namakkal: "நாமக்கல்",
  nilgiris: "நீலகிரி",
  perambalur: "பெரம்பலூர்",
  pudukkottai: "புதுக்கோட்டை",
  ramanathapuram: "ராமநாதபுரம்",
  ranipet: "ராணிப்பேட்டை",
  salem: "சேலம்",
  sivaganga: "சிவகங்கை",
  tenkasi: "தென்காசி",
  thanjavur: "தஞ்சாவூர்",
  theni: "தேனி",
  thoothukudi: "தூத்துக்குடி",
  tiruchirappalli: "திருச்சிராப்பள்ளி",
  tirunelveli: "திருநெல்வேலி",
  tirupathur: "திருப்பத்தூர்",
  tiruppur: "திருப்பூர்",
  tiruvallur: "திருவள்ளூர்",
  tiruvannamalai: "திருவண்ணாமலை",
  tiruvarur: "திருவாரூர்",
  vellore: "வேலூர்",
  viluppuram: "விழுப்புரம்",
  virudhunagar: "விருதுநகர்",
};

export function Sidebar({
  className,
  onNavigate,
}: {
  className?: string;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { lang, t } = useLanguage();
  const { selectedDistrict, districts } = useDistrict();
  const [fpos, setFpos] = useState<FPO[]>([]);

  useEffect(() => {
    let mounted = true;
    getFPOs().then((list) => {
      if (mounted && Array.isArray(list) && list.length > 0) {
        setFpos(list);
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  const activeDistrictObj = useMemo(() => {
    if (!selectedDistrict || selectedDistrict === "all") return null;
    return districts.find(
      (d) => d.name.toLowerCase() === selectedDistrict.toLowerCase()
    );
  }, [selectedDistrict, districts]);

  const activeDistrictTamil = useMemo(() => {
    if (!selectedDistrict || selectedDistrict === "all") return "";
    const lower = selectedDistrict.toLowerCase().trim();
    return TAMIL_DISTRICT_MAP[lower] || activeDistrictObj?.tamil_name || selectedDistrict;
  }, [selectedDistrict, activeDistrictObj]);

  const workspaceName = useMemo(() => {
    if (!selectedDistrict || selectedDistrict === "all") {
      return lang === "ta" ? "தமிழ்நாடு உழவர் கூட்டமைப்பு" : "Tamil Nadu State Collective";
    }
    const matchedFpo = fpos.find(
      (f) => f.district.toLowerCase() === selectedDistrict.toLowerCase()
    );
    if (matchedFpo) {
      return matchedFpo.name;
    }
    return lang === "ta"
      ? `${activeDistrictTamil} உழவர் கூட்டமைப்பு`
      : `${selectedDistrict} FPO Collective`;
  }, [selectedDistrict, fpos, activeDistrictTamil, lang]);

  const workspaceSubtitle = useMemo(() => {
    if (!selectedDistrict || selectedDistrict === "all") {
      return lang === "ta" ? "அனைத்து 38 மாவட்டங்கள்" : "Statewide (38 Districts)";
    }
    return lang === "ta"
      ? `${activeDistrictTamil} மண்டல செயல்பாடுகள்`
      : `${selectedDistrict} District Operations`;
  }, [selectedDistrict, activeDistrictTamil, lang]);

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
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              {lang === "ta" ? "உங்கள் பணியிடம்" : "Your workspace"}
            </p>
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-semibold bg-primary/10 text-primary">
              {selectedDistrict === "all"
                ? (lang === "ta" ? "மாநிலம்" : "Statewide")
                : (lang === "ta" && activeDistrictTamil ? activeDistrictTamil : selectedDistrict)}
            </span>
          </div>
          <p className="mt-1.5 truncate text-sm font-semibold text-foreground" title={workspaceName}>
            {workspaceName}
          </p>
          <p className="text-[11px] text-muted-foreground truncate">
            {workspaceSubtitle}
          </p>
        </div>
      </div>
    </aside>
  );
}
