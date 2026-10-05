import { API_BASE } from "./api";

const DIRECT_API_FALLBACK = "https://fpolink-api.onrender.com";

export async function authFetch(path: string, init: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("fpolink_access_token") : null;
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(init.headers || {}),
  };

  let res: Response | null = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  }).catch(() => null);

  // If same-origin proxy fails (network error, 502/504 Bad Gateway, etc.), fallback to live Render API via CORS
  if (!res || res.status >= 500) {
    const directUrl = `${DIRECT_API_FALLBACK}${path.startsWith("/") ? path : `/${path}`}`;
    res = await fetch(directUrl, {
      ...init,
      headers,
    }).catch(() => null);
  }

  if (!res) {
    throw new Error("Network error: unable to reach FPOLink server");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

