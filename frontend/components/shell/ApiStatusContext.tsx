"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { getHealth, HealthStatus } from "@/lib/api";

const ApiStatusContext = createContext<HealthStatus | null>(null);

export function ApiStatusProvider({ children }: { children: React.ReactNode }) {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      const result = await getHealth();
      if (active) setHealth(result);
    };
    void refresh();
    const interval = window.setInterval(refresh, 60_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return <ApiStatusContext.Provider value={health}>{children}</ApiStatusContext.Provider>;
}

export function useApiStatus() {
  return useContext(ApiStatusContext);
}

export function apiIsHealthy(health: HealthStatus | null) {
  const serviceHealthy = health?.status.toLowerCase() === "ok" || health?.status.toLowerCase() === "healthy";
  const databaseHealthy = health?.db.toLowerCase() === "ok" || health?.db.toLowerCase() === "healthy" || health?.db.toLowerCase() === "connected";
  return Boolean(serviceHealthy && databaseHealthy);
}
