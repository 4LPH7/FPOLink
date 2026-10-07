"use client";

import React, { createContext, useContext, useEffect, useState, useMemo } from "react";
import { getDistricts, DistrictItem } from "@/lib/api";

interface DistrictContextValue {
  selectedDistrict: string;
  setSelectedDistrict: (district: string) => void;
  districts: DistrictItem[];
  loading: boolean;
}

const DistrictContext = createContext<DistrictContextValue>({
  selectedDistrict: "all",
  setSelectedDistrict: () => {},
  districts: [],
  loading: true,
});

let cachedDistricts: DistrictItem[] | null = null;

export function DistrictProvider({ children }: { children: React.ReactNode }) {
  const [districts, setDistricts] = useState<DistrictItem[]>(cachedDistricts || []);
  const [selectedDistrict, setSelectedDistrictState] = useState<string>("all");
  const [loading, setLoading] = useState<boolean>(!cachedDistricts);

  useEffect(() => {
    // Load persisted preference if available
    try {
      const saved = localStorage.getItem("fpolink_selected_district");
      if (saved) {
        setSelectedDistrictState(saved);
      }
    } catch {
      // Ignore storage errors in restricted contexts
    }

    if (cachedDistricts && cachedDistricts.length > 0) {
      setDistricts(cachedDistricts);
      setLoading(false);
      return;
    }

    let active = true;
    getDistricts().then((data) => {
      if (!active) return;
      if (Array.isArray(data) && data.length > 0) {
        cachedDistricts = data;
        setDistricts(data);
      }
      setLoading(false);
    });

    return () => {
      active = false;
    };
  }, []);

  const setSelectedDistrict = (dist: string) => {
    setSelectedDistrictState(dist);
    try {
      localStorage.setItem("fpolink_selected_district", dist);
    } catch {
      // ignore
    }
  };

  const value = useMemo(
    () => ({
      selectedDistrict,
      setSelectedDistrict,
      districts,
      loading,
    }),
    [selectedDistrict, districts, loading]
  );

  return <DistrictContext.Provider value={value}>{children}</DistrictContext.Provider>;
}

export function useDistrict() {
  return useContext(DistrictContext);
}
