"use client";

import React from "react";
import { ShieldCheck, Heart, ExternalLink } from "lucide-react";

interface FooterProps {
  lang: "ta" | "en";
}

export default function Footer({ lang }: FooterProps) {
  return (
    <footer className="mt-16 bg-white border-t border-gray-200 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-500">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-gray-800">FPOLink TN</span>
            <span>•</span>
            <span>© 2026. MIT License.</span>
            <span>•</span>
            <span className="inline-flex items-center text-green-700 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" />
              DPDP Act Compliant
            </span>
          </div>

          <div className="flex items-center space-x-4 text-gray-500">
            <span>
              {lang === "ta"
                ? "தரவு மூலங்கள்: Agmarknet (OGD), CEDA (அசோகா பல்கலைக்கழகம்), Open-Meteo"
                : "Data Provenance: Agmarknet (OGD), CEDA (Ashoka Univ), Open-Meteo"}
            </span>
          </div>

          <div className="flex items-center space-x-1 text-gray-600 font-medium">
            <span>
              {lang === "ta"
                ? "தமிழ்நாடு உழவர் உற்பத்தியாளர் நிறுவனங்களுக்காக அர்ப்பணிக்கப்பட்டது"
                : "Dedicated to the Farmer Producer Organizations of Tamil Nadu"}
            </span>
            <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500 ml-1" />
          </div>
        </div>
      </div>
    </footer>
  );
}
