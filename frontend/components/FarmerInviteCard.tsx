"use client";

import React, { useState } from "react";
import {
  Users,
  Smartphone,
  ShieldCheck,
  Share2,
  Check,
  ExternalLink,
  Plus,
} from "lucide-react";

interface FarmerInviteCardProps {
  lang: "ta" | "en";
  t: any;
  onNavigateFarmerList?: () => void;
}

const SAMPLE_FARMERS = [
  {
    id: "f-1",
    nameTa: "முத்துசாமி கே",
    nameEn: "Muthusamy K",
    villageTa: "கொடுமுடி",
    villageEn: "Kodumudi",
    cropTa: "மஞ்சள் & வாழை",
    cropEn: "Turmeric & Banana",
    acres: 3.5,
    phoneMasked: "98****3210",
    consent: true,
    alerts: true,
  },
  {
    id: "f-2",
    nameTa: "பழனிசாமி ஜி",
    nameEn: "Palanisamy G",
    villageTa: "பெருந்துறை",
    villageEn: "Perundurai",
    cropTa: "மஞ்சள்",
    cropEn: "Turmeric",
    acres: 4.2,
    phoneMasked: "93****4412",
    consent: true,
    alerts: true,
  },
  {
    id: "f-3",
    nameTa: "கந்தசாமி ஆர்",
    nameEn: "Kandasamy R",
    villageTa: "செம்மாம்பாளையம்",
    villageEn: "Semmampalayam",
    cropTa: "வாழை",
    cropEn: "Banana",
    acres: 2.8,
    phoneMasked: "94****8890",
    consent: true,
    alerts: false,
  },
];

export default function FarmerInviteCard({
  lang,
  t,
  onNavigateFarmerList,
}: FarmerInviteCardProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [inviteUrls, setInviteUrls] = useState<Record<string, string>>({});

  const getInviteUrl = (farmerId: string) => {
    if (inviteUrls[farmerId]) {
      return inviteUrls[farmerId];
    }
    const greeting = lang === "ta" ? "வணக்கம்" : "Hi";
    const botPhone = process.env.NEXT_PUBLIC_WHATSAPP_BOT_PHONE || "919876543210";
    return `https://wa.me/${botPhone}?text=${encodeURIComponent(`${greeting} [FARMER:${farmerId}]`)}`;
  };

  const fetchInviteUrl = async (farmerId: string) => {
    try {
      const res = await fetch(`/api/farmers/${farmerId}/whatsapp-invite`);
      if (res.ok) {
        const data = await res.json();
        if (data.invite_url) {
          setInviteUrls((prev) => ({ ...prev, [farmerId]: data.invite_url }));
          return data.invite_url;
        }
      }
    } catch {
      // Fallback
    }
    return getInviteUrl(farmerId);
  };

  const handleCopy = async (id: string) => {
    const url = await fetchInviteUrl(id);
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 p-5 sm:p-6 shadow-xs">
      <div className="flex items-center justify-between pb-4 border-b border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
            <Users className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-gray-900 tracking-tight">
              {t.nav.farmers} & {t.farmer.send_invite}
            </h3>
            <p className="text-xs text-gray-500">
              {lang === "ta"
                ? "விவசாயிகளை WhatsApp பாட்டில் இணைக்க 1-கிளிக் அழைப்பு இணைப்பு"
                : "1-Click wa.me invite link to onboard registered farmers onto WhatsApp bot"}
            </p>
          </div>
        </div>

        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
          1,250 {lang === "ta" ? "பதிவு செய்யப்பட்ட விவசாயிகள்" : "Registered"}
        </span>
      </div>

      {/* Farmers List */}
      <div className="mt-4 divide-y divide-gray-100">
        {SAMPLE_FARMERS.map((farmer) => (
          <div
            key={farmer.id}
            className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-gray-50/70 p-2 rounded-xl transition-colors"
          >
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-sm text-gray-900">
                  {lang === "ta" ? farmer.nameTa : farmer.nameEn}
                </span>
                <span className="text-xs text-gray-400 font-mono">
                  ({farmer.phoneMasked})
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-green-50 text-green-700 border border-green-200">
                  <ShieldCheck className="w-3 h-3 mr-0.5 text-green-600" />
                  DPDP
                </span>
              </div>
              <div className="flex items-center space-x-3 text-xs text-gray-500 mt-1">
                <span>📍 {lang === "ta" ? farmer.villageTa : farmer.villageEn}</span>
                <span>•</span>
                <span>🌾 {lang === "ta" ? farmer.cropTa : farmer.cropEn}</span>
                <span>•</span>
                <span>{farmer.acres} {t.common.acres}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              <a
                href={getInviteUrl(farmer.id)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-bold bg-green-600 hover:bg-green-700 text-white shadow-xs transition-all active:scale-95"
              >
                <Smartphone className="w-3.5 h-3.5 mr-1.5" />
                {t.farmer.send_invite}
                <ExternalLink className="w-3 h-3 ml-1 opacity-70" />
              </a>
              <button
                onClick={() => handleCopy(farmer.id)}
                className="p-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-100 transition-colors"
                title="Copy wa.me link"
              >
                {copiedId === farmer.id ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Share2 className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
        <span>
          {lang === "ta"
            ? "அனைத்து அழைப்புகளும் DPDP ஒப்புதல் விதிகளுக்கு உட்பட்டவை."
            : "All onboarding interactions comply with DPDP Act consent regulations."}
        </span>
        <button
          onClick={onNavigateFarmerList}
          className="text-green-700 font-bold hover:underline transition-colors active:scale-95 cursor-pointer"
        >
          {t.farmer.farmer_list} →
        </button>
      </div>
    </div>
  );
}
