"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Leaf, LoaderCircle } from "lucide-react";
import { login } from "@/lib/auth";
import { useLanguage } from "@/lib/i18n/context";

export default function LoginPage() {
  const router = useRouter();
  const { lang } = useLanguage();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const result = await login(phone.trim(), password);
    setBusy(false);
    if (!result) {
      setError(lang === "ta" ? "தொலைபேசி அல்லது கடவுச்சொல் சரிபார்க்கவும்." : "Check your phone number and password, then try again.");
      return;
    }
    router.replace(result.password_change_required ? "/change-password" : "/");
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-100 via-background to-background px-4 py-10">
      <section className="w-full max-w-md rounded-3xl border border-border bg-card p-6 shadow-xl shadow-emerald-950/5 sm:p-9">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid size-12 place-items-center rounded-2xl bg-primary text-primary-foreground"><Leaf className="size-6" /></div>
          <div><p className="text-lg font-bold tracking-tight">FPOLink</p><p className="text-sm text-muted-foreground">Tamil Nadu FPO workspace</p></div>
        </div>
        <h1 className="text-2xl font-bold">{lang === "ta" ? "மீண்டும் வருக" : "Welcome back"}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{lang === "ta" ? "உங்கள் கணக்கில் உள்நுழையவும்." : "Sign in with your registered phone number."}</p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          <label className="block space-y-1.5 text-sm font-medium">
            <span>{lang === "ta" ? "தொலைபேசி எண்" : "Phone number"}</span>
            <input required autoComplete="tel" inputMode="tel" minLength={10} maxLength={15} value={phone} onChange={(event) => setPhone(event.target.value)} className="h-12 w-full rounded-xl border border-input bg-background px-3 outline-none transition focus-visible:ring-2 focus-visible:ring-ring" placeholder="9876543210" />
          </label>
          <label className="block space-y-1.5 text-sm font-medium">
            <span>{lang === "ta" ? "கடவுச்சொல்" : "Password"}</span>
            <input required type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} className="h-12 w-full rounded-xl border border-input bg-background px-3 outline-none transition focus-visible:ring-2 focus-visible:ring-ring" />
          </label>
          {error && <p role="alert" className="rounded-xl border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">{error}</p>}
          <button disabled={busy} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 font-semibold text-primary-foreground transition hover:brightness-95 disabled:opacity-60">
            {busy ? <LoaderCircle className="size-4 animate-spin" /> : <>{lang === "ta" ? "உள்நுழை" : "Sign in"}<ArrowRight className="size-4" /></>}
          </button>
        </form>
        <p className="mt-6 text-center text-xs leading-relaxed text-muted-foreground">{lang === "ta" ? "கணக்கு உதவிக்கு உங்கள் FPO நிர்வாகியை தொடர்பு கொள்ளவும்." : "Need access? Contact your FPO administrator."}</p>
      </section>
    </main>
  );
}
