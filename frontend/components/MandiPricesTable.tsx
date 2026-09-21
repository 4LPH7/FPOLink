"use client";

import React, { useState } from "react";
import { Store, Search, ShieldCheck, ArrowUpRight, ArrowDownRight, Minus, ExternalLink } from "lucide-react";
import { MANDI_DATA, type MandiRow } from "@/lib/marketData";

interface MandiPricesTableProps {
  lang: "ta" | "en";
  t: any;
}

export default function MandiPricesTable({ lang, t }: MandiPricesTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [cropFilter, setCropFilter] = useState("all");

  const filteredRows = MANDI_DATA.filter((row) => {
    const matchesSearch =
      row.mandiEn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.mandiTa.includes(searchTerm) ||
      row.cropEn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.cropTa.includes(searchTerm);

    if (cropFilter === "all") return matchesSearch;
    if (cropFilter === "turmeric") return matchesSearch && row.cropEn.includes("Turmeric");
    if (cropFilter === "banana") return matchesSearch && row.cropEn.includes("Banana");
    if (cropFilter === "coconut") return matchesSearch && row.cropEn.includes("Coconut");
    return matchesSearch;
  });

  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 shadow-xs overflow-hidden">
      {/* Table Header & Controls */}
      <div className="p-5 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-gray-900 tracking-tight flex items-center">
              <Store className="w-5 h-5 text-green-600 mr-2" />
              {lang === "ta" ? "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடங்களின் தினசரி விலை நிலவரம்" : "Erode Mandi Daily Auction Rates"}
            </h3>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
              {lang === "ta" ? "மாதிரி குறிப்புத் தரவு" : "Sample Reference Data"}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            {lang === "ta"
              ? "மாதிரி குறிப்புத் தரவு (செப்டம்பர் 2026) — Agmarknet (OGD) மற்றும் CEDA வடிவமைப்பின்படி"
              : "Sample reference rates (September 2026) — formatted to Agmarknet (OGD) & CEDA schemas"}
          </p>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex items-center space-x-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder={lang === "ta" ? "மண்டி அல்லது பயிர் தேடுக..." : "Search mandi or crop..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-600 transition-all w-48 sm:w-56"
            />
          </div>

          {/* Crop Dropdown */}
          <select
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
            className="text-xs rounded-xl border border-gray-200 bg-gray-50 px-2.5 py-1.5 font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-600"
          >
            <option value="all">{t.common.all}</option>
            <option value="turmeric">{t.crops.turmeric}</option>
            <option value="banana">{t.crops.banana}</option>
            <option value="coconut">{t.crops.coconut}</option>
          </select>
        </div>
      </div>

      {/* Mandi Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-50/80 text-gray-600 font-semibold border-b border-gray-100 uppercase tracking-wider text-[11px]">
            <tr>
              <th className="py-3 px-4 sm:px-6">{t.harvest.crop}</th>
              <th className="py-3 px-4 sm:px-6">{t.price.mandi}</th>
              <th className="py-3 px-4 sm:px-6">{t.price.modal_price}</th>
              <th className="py-3 px-4 sm:px-6 hidden md:table-cell">{t.price.min_price} – {t.price.max_price}</th>
              <th className="py-3 px-4 sm:px-6">{t.price.change}</th>
              <th className="py-3 px-4 sm:px-6 hidden sm:table-cell">{t.price.source}</th>
              <th className="py-3 px-4 sm:px-6 hidden lg:table-cell">{t.price.date}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredRows.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-green-50/40 transition-colors group"
              >
                <td className="py-3.5 px-4 sm:px-6 font-bold text-gray-900">
                  {lang === "ta" ? row.cropTa : row.cropEn}
                </td>
                <td className="py-3.5 px-4 sm:px-6 text-gray-700 font-medium">
                  {lang === "ta" ? row.mandiTa : row.mandiEn}
                </td>
                <td className="py-3.5 px-4 sm:px-6">
                  <span className="font-extrabold text-sm text-gray-900">
                    ₹{row.modal.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-gray-500 font-medium ml-1">/ q</span>
                </td>
                <td className="py-3.5 px-4 sm:px-6 text-gray-600 hidden md:table-cell font-mono">
                  ₹{row.min.toLocaleString()} – ₹{row.max.toLocaleString()}
                </td>
                <td className="py-3.5 px-4 sm:px-6">
                  <span
                    className={`inline-flex items-center font-bold px-2 py-0.5 rounded-full text-[11px] ${
                      row.change >= 0
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {row.change >= 0 ? (
                      <ArrowUpRight className="w-3 h-3 mr-0.5" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3 mr-0.5" />
                    )}
                    {row.change >= 0 ? "+" : ""}
                    {row.change}%
                  </span>
                </td>
                <td className="py-3.5 px-4 sm:px-6 hidden sm:table-cell">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-gray-100 text-gray-700">
                    <ShieldCheck className="w-3 h-3 mr-1 text-green-600" />
                    {row.source.toUpperCase()}
                  </span>
                </td>
                <td className="py-3.5 px-4 sm:px-6 text-gray-500 hidden lg:table-cell font-mono">
                  {row.date}
                </td>
              </tr>
            ))}

            {filteredRows.length === 0 && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-gray-400">
                  {t.common.no_data}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
