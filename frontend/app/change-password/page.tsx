"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { KeyRound, LoaderCircle } from "lucide-react";
import { changeRequiredPassword, getToken } from "@/lib/auth";
import { useLanguage } from "@/lib/i18n/context";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { lang } = useLanguage();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!getToken()) router.replace("/login");
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (newPassword.length < 12) {
      setError(lang === "ta" ? "புதிய கடவுச்சொல் குறைந்தது 12 எழுத்துகள் இருக்க வேண்டும்." : "Use at least 12 characters for your new password.");
      return;
    }
    if (newPassword !== confirmation) {
      setError(lang === "ta" ? "புதிய கடவுச்சொற்கள் பொருந்தவில்லை." : "The new passwords do not match.");
      return;
    }

    setBusy(true);
    const result = await changeRequiredPassword(currentPassword, newPassword);
    setBusy(false);
    if (!result.ok) {
      setError(result.message || (lang === "ta" ? "கடவுச்சொல்லை மாற்ற முடியவில்லை. மீண்டும் முயற்சிக்கவும்." : "Could not change the password. Check your current password and try again."));
      return;
    }
    router.replace("/");
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-100 via-background to-background px-4 py-10">
      <section className="w-full max-w-md rounded-3xl border border-border bg-card p-6 shadow-xl shadow-emerald-950/5 sm:p-9">
        <div className="mb-7 grid size-12 place-items-center rounded-2xl bg-primary text-primary-foreground">
          <KeyRound className="size-6" aria-hidden="true" />
        </div>
        <h1 className="text-2xl font-bold">{lang === "ta" ? "கடவுச்சொல்லை மாற்றவும்" : "Set a new password"}</h1>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          {lang === "ta" ? "உங்கள் கணக்கைப் பாதுகாக்க, தொடர்ந்து செல்லும் முன் புதிய கடவுச்சொல்லை அமைக்கவும்." : "For account security, change the temporary password before continuing."}
        </p>

        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          <label className="block space-y-1.5 text-sm font-medium">
            <span>{lang === "ta" ? "தற்போதைய கடவுச்சொல்" : "Current password"}</span>
            <input required type="password" autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} className="h-12 w-full rounded-xl border border-input bg-background px-3 outline-none transition focus-visible:ring-2 focus-visible:ring-ring" />
          </label>
          <label className="block space-y-1.5 text-sm font-medium">
            <span>{lang === "ta" ? "புதிய கடவுச்சொல்" : "New password"}</span>
            <input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} className="h-12 w-full rounded-xl border border-input bg-background px-3 outline-none transition focus-visible:ring-2 focus-visible:ring-ring" />
            <span className="block text-xs font-normal text-muted-foreground">{lang === "ta" ? "குறைந்தது 12 எழுத்துகள்" : "At least 12 characters"}</span>
          </label>
          <label className="block space-y-1.5 text-sm font-medium">
            <span>{lang === "ta" ? "புதிய கடவுச்சொல்லை உறுதிப்படுத்தவும்" : "Confirm new password"}</span>
            <input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="h-12 w-full rounded-xl border border-input bg-background px-3 outline-none transition focus-visible:ring-2 focus-visible:ring-ring" />
          </label>
          {error && <p role="alert" className="rounded-xl border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">{error}</p>}
          <button disabled={busy} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 font-semibold text-primary-foreground transition hover:brightness-95 disabled:opacity-60">
            {busy ? <LoaderCircle className="size-4 animate-spin" /> : (lang === "ta" ? "கடவுச்சொல்லை புதுப்பிக்கவும்" : "Update password")}
          </button>
        </form>
      </section>
    </main>
  );
}
