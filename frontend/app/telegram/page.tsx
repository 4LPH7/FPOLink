"use client";

import React, { useEffect, useState } from "react";
import { authFetch } from "@/lib/authFetch";

export default function TelegramPage() {
  const [status, setStatus] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  const load = () => authFetch("/api/telegram/status").then(setStatus).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const setWebhook = async () => {
    try { const r = await authFetch("/api/telegram/set-webhook", { method: "POST" }); setMsg(JSON.stringify(r)); load(); }
    catch (e: any) { setError(e.message); }
  };

  return (
    <div className="space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Telegram Bot</h1>
      <p>Bot: <a className="text-green-700 underline" href="https://t.me/Fpo_Link_Bot" target="_blank" rel="noreferrer">@Fpo_Link_Bot</a></p>
      {error && <p className="text-red-600">{error}</p>}
      {status && (
        <table className="w-full rounded border text-sm">
          <tbody>
            {Object.entries(status).map(([k, v]) => (
              <tr key={k} className="border-b">
                <td className="p-2 font-medium">{k}</td>
                <td className="p-2 font-mono break-all">{typeof v === "object" ? JSON.stringify(v) : String(v)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <button onClick={setWebhook} className="rounded bg-green-700 px-4 py-2 text-white">Register webhook</button>
      {msg && <pre className="text-xs">{msg}</pre>}
    </div>
  );
}
