/**
 * FPOLink TN — Auth token store
 *
 * Lightweight localStorage-based token manager.
 * No NextAuth dependency — keeps the stack simple for the pilot.
 */

import { API_BASE } from "./api";

const TOKEN_KEY = "fpolink_access_token";
const REFRESH_KEY = "fpolink_refresh_token";

// ─── Storage helpers ─────────────────────────────────────────

export function saveTokens(accessToken: string, refreshToken?: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// ─── Login ───────────────────────────────────────────────────

export interface LoginResult {
  access_token: string;
  refresh_token: string;
}

/**
 * Log in with phone + password, persist tokens, and return them.
 * Returns null on failure (bad creds or network error).
 */
export async function login(
  phone: string,
  password: string
): Promise<LoginResult | null> {
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
      cache: "no-store",
    });

    if (!res.ok) return null;

    const data: LoginResult = await res.json();
    saveTokens(data.access_token, data.refresh_token);
    return data;
  } catch (err) {
    console.warn("Login failed:", err);
    return null;
  }
}

/**
 * Ensure a valid token is available. Attempts a fresh login with staff
 * credentials if none is stored. Returns the token or null.
 *
 * For the pilot, we use the admin credentials since all dashboard users
 * are FPO staff with the same access level. Replace with a proper login
 * form before any public rollout.
 */
export async function ensureToken(): Promise<string | null> {
  const existing = getToken();
  if (existing) return existing;

  // Auto-login with the pilot staff credential
  const STAFF_PHONE =
    process.env.NEXT_PUBLIC_STAFF_PHONE || "9999900000";
  const STAFF_PASS =
    process.env.NEXT_PUBLIC_STAFF_PASS || "admin123";

  const result = await login(STAFF_PHONE, STAFF_PASS);
  return result?.access_token ?? null;
}
