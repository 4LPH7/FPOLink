/**
 * FPOLink TN — Auth token store
 *
 * Lightweight localStorage-based token manager.
 * No NextAuth dependency — keeps the stack simple for the pilot.
 */

import { API_BASE } from "./api";

const TOKEN_KEY = "fpolink_access_token";
const REFRESH_KEY = "fpolink_refresh_token";
const PASSWORD_CHANGE_KEY = "fpolink_password_change_required";

// ─── Storage helpers ─────────────────────────────────────────

export function saveTokens(accessToken: string, refreshToken?: string | null): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
  else localStorage.removeItem(REFRESH_KEY);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(PASSWORD_CHANGE_KEY);
}

export function passwordChangeRequired(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(PASSWORD_CHANGE_KEY) === "true";
}

// ─── Login ───────────────────────────────────────────────────

export interface LoginResult {
  access_token: string;
  refresh_token?: string | null;
  password_change_required?: boolean;
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
    let res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
      cache: "no-store",
    }).catch(() => null);

    // If proxy failed or returned an error status other than 401/422,
    // fallback to direct live Render API endpoint (supported by CORS)
    if (!res || (res.status !== 200 && res.status !== 401 && res.status !== 422)) {
      res = await fetch("https://fpolink-api.onrender.com/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, password }),
        cache: "no-store",
      }).catch(() => null);
    }

    if (!res || !res.ok) return null;

    const data: LoginResult = await res.json();
    saveTokens(data.access_token, data.refresh_token);
    if (data.password_change_required) {
      localStorage.setItem(PASSWORD_CHANGE_KEY, "true");
    } else {
      localStorage.removeItem(PASSWORD_CHANGE_KEY);
    }
    return data;
  } catch (err) {
    console.warn("Login failed:", err);
    return null;
  }
}

export async function changeRequiredPassword(
  currentPassword: string,
  newPassword: string
): Promise<{ ok: boolean; message?: string }> {
  const token = getToken();
  if (!token) return { ok: false };

  try {
    let res = await fetch(`${API_BASE}/api/auth/change-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
      cache: "no-store",
    }).catch(() => null);

    if (!res || res.status >= 500) {
      res = await fetch("https://fpolink-api.onrender.com/api/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
        cache: "no-store",
      }).catch(() => null);
    }

    if (!res) return { ok: false, message: "Network error: unable to reach server" };

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return {
        ok: false,
        message: typeof data.detail === "string" ? data.detail : undefined,
      };
    }

    saveTokens(data.access_token, data.refresh_token);
    localStorage.removeItem(PASSWORD_CHANGE_KEY);
    return { ok: true };
  } catch (err) {
    console.warn("Password change failed:", err);
    return { ok: false };
  }
}

/**
 * Return the signed-in user's token, or null when the user is signed out.
 */
export async function ensureToken(): Promise<string | null> {
  return getToken();
}
