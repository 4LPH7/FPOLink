"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";
import { ArrowRight, Command, Search } from "lucide-react";
import { useLanguage } from "@/lib/i18n/context";

const commands = [
  { href: "/", en: "Overview", ta: "கண்ணோட்டம்", group: "Workspace" },
  { href: "/prices", en: "Market prices", ta: "சந்தை விலைகள்", group: "Workspace" },
  { href: "/farmers", en: "Farmers", ta: "விவசாயிகள்", group: "Workspace" },
  { href: "/buyers", en: "Buyers", ta: "கொள்முதலாளர்கள்", group: "Workspace" },
  { href: "/matching", en: "Demand matching", ta: "தேவை பொருத்தம்", group: "Workspace" },
  { href: "/admin", en: "Data operations", ta: "தரவு செயல்பாடுகள்", group: "Operations" },
  { href: "/whatsapp", en: "WhatsApp activity", ta: "வாட்ஸ்அப் செயல்பாடு", group: "Operations" },
];

export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const router = useRouter();
  const { lang } = useLanguage();
  const inputRef = useRef<HTMLInputElement>(null);
  const [mounted, setMounted] = useState(false);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const visible = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    if (!normalized) return commands;
    return commands.filter((command) =>
      `${command.en} ${command.ta} ${command.href}`.toLocaleLowerCase().includes(normalized)
    );
  }, [query]);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setActiveIndex(0);
    const frame = requestAnimationFrame(() => inputRef.current?.focus());
    return () => cancelAnimationFrame(frame);
  }, [open]);

  useEffect(() => {
    if (activeIndex >= visible.length) setActiveIndex(Math.max(visible.length - 1, 0));
  }, [activeIndex, visible.length]);

  if (!open || !mounted) return null;

  const navigate = (href: string) => {
    onClose();
    router.push(href);
  };

  return createPortal((
    <div className="command-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section
        role="dialog"
        aria-modal="true"
        aria-label={lang === "ta" ? "பக்கத்தைத் தேடுக" : "Search pages"}
        className="command-panel"
        onKeyDown={(event) => {
          if (event.key === "Escape") onClose();
          if (event.key === "ArrowDown") {
            event.preventDefault();
            setActiveIndex((index) => (index + 1) % Math.max(visible.length, 1));
          }
          if (event.key === "ArrowUp") {
            event.preventDefault();
            setActiveIndex((index) => (index - 1 + visible.length) % Math.max(visible.length, 1));
          }
          if (event.key === "Enter" && visible[activeIndex]) navigate(visible[activeIndex].href);
        }}
      >
        <div className="flex items-center gap-3 border-b border-border px-4">
          <Search className="size-5 shrink-0 text-primary" aria-hidden="true" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => { setQuery(event.target.value); setActiveIndex(0); }}
            placeholder={lang === "ta" ? "பக்கங்கள் மற்றும் செயல்பாடுகளைத் தேடுக..." : "Search pages and workspace..."}
            className="h-14 min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            aria-label={lang === "ta" ? "தேடல்" : "Search"}
          />
          <kbd className="hidden rounded-md border border-border bg-muted px-2 py-1 text-[10px] text-muted-foreground sm:inline">ESC</kbd>
        </div>

        <div className="max-h-[min(60vh,420px)] overflow-y-auto p-2">
          {visible.length === 0 ? (
            <p className="px-3 py-10 text-center text-sm text-muted-foreground">
              {lang === "ta" ? "பொருத்தமான பக்கம் கிடைக்கவில்லை" : "No matching pages found"}
            </p>
          ) : visible.map((item, index) => (
            <button
              key={item.href}
              type="button"
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => navigate(item.href)}
              className={`group flex min-h-12 w-full items-center gap-3 rounded-xl px-3 text-left transition-colors ${index === activeIndex ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"}`}
            >
              <span className={`grid size-8 place-items-center rounded-lg ${index === activeIndex ? "bg-white/15" : "bg-muted"}`}>
                <Command className="size-4" aria-hidden="true" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-semibold">{lang === "ta" ? item.ta : item.en}</span>
                <span className={`block text-[11px] ${index === activeIndex ? "text-white/70" : "text-muted-foreground"}`}>{item.group}</span>
              </span>
              <ArrowRight className={`size-4 ${index === activeIndex ? "opacity-100" : "opacity-0 group-hover:opacity-60"}`} aria-hidden="true" />
            </button>
          ))}
        </div>
        <footer className="flex items-center justify-between border-t border-border bg-muted/35 px-4 py-2.5 text-[11px] text-muted-foreground">
          <span>{lang === "ta" ? "வழிசெலுத்த அம்புக்குறிகள் · திற Enter" : "Navigate with arrows · open with Enter"}</span>
          <span className="hidden items-center gap-1 sm:inline-flex"><kbd className="rounded border border-border bg-card px-1.5 py-0.5">Ctrl</kbd><kbd className="rounded border border-border bg-card px-1.5 py-0.5">K</kbd></span>
        </footer>
      </section>
    </div>
  ), document.body);
}
