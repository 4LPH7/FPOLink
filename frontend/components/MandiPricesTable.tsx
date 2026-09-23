"use client";

import React, { useState, useEffect } from "react";
import { Store, Search, ShieldCheck, ArrowUpRight, ArrowDownRight, Minus, ExternalLink, RefreshCw } from "lucide-react";
import { getLatestPrices, MarketPrice } from "@/lib/api";

interface MandiPricesTableProps {
  lang: "ta" | "en";
  t: any;
}

export default function MandiPricesTable({ lang, t }: MandiPricesTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [cropFilter, setCropFilter] = useState("all");
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getLatestPrices("Erode");
        setPrices(data);
      } catch (err) {
        console.warn("Failed to load prices:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredRows = prices.filter((row) => {
    const matchesSearch =
      row.market_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.crop_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (row.crop_tamil_name && row.crop_tamil_name.includes(searchTerm));

    if (cropFilter === "all") return matchesSearch;
    return matchesSearch && row.crop_name.toLowerCase().includes(cropFilter);
  });

  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 shadow-xs overflow-hidden">
      {/* Table Header & Controls */}
      <div className="p-5 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-gray-900 tracking-tight flex items-center">
              <Store className="w-5 h-5 text-emerald-600 mr-2" />
              {lang === "ta" ? "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடங்களின் தினசரி விலை நிலவரம்" : "Erode Mandi Daily Auction Rates"}
            </h3>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
              {lang === "ta" ? "நேரலை மண்டி தரவு" : "Live Mandi Data"}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            {lang === "ta"
              ? "Agmarknet (OGD) மற்றும் ஒழுங்குமுறை சந்தைகளின் நேரலை மேற்கோள்கள்"
              : "Live price feeds verified from official Agmarknet and regulated mandi sources"}
          </p>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col sm:flex-row items-center gap-2">
          <div className="relative w-full sm:w-60">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={lang === "ta" ? "சந்தை அல்லது பயிரைத் தேடு..." : "Search mandi or crop..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
          </div>

          <div className="inline-flex p-1 bg-gray-100 rounded-xl text-xs font-medium w-full sm:w-auto">
            <button
              onClick={() => setCropFilter("all")}
              className={`flex-1 sm:flex-initial px-3 py-1 rounded-lg transition-all ${
                cropFilter === "all" ? "bg-white text-emerald-700 font-bold shadow-xs" : "text-gray-500"
              }`}
            >
              {lang === "ta" ? "அனைத்தும்" : "All"}
            </button>
            <button
              onClick={() => setCropFilter("turmeric")}
              className={`flex-1 sm:flex-initial px-3 py-1 rounded-lg transition-all ${
                cropFilter === "turmeric" ? "bg-white text-emerald-700 font-bold shadow-xs" : "text-gray-500"
              }`}
            >
              {lang === "ta" ? "மஞ்சள்" : "Turmeric"}
            </button>
            <button
              onClick={() => setCropFilter("banana")}
              className={`flex-1 sm:flex-initial px-3 py-1 rounded-lg transition-all ${
                cropFilter === "banana" ? "bg-white text-emerald-700 font-bold shadow-xs" : "text-gray-500"
              }`}
            >
              {lang === "ta" ? "வாழை" : "Banana"}
            </button>
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12 text-muted-foreground text-sm">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            <span>Loading live prices...</span>
          </div>
        ) : filteredRows.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground text-sm">
            No market price observations available.
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
                <th className="py-3 px-6">{lang === "ta" ? "பயிர் / வகை" : "Crop"}</th>
                <th className="py-3 px-6">{lang === "ta" ? "சந்தை" : "Mandi"}</th>
                <th className="py-3 px-4">{lang === "ta" ? "குறைந்தபட்சம்" : "Min Price"}</th>
                <th className="py-3 px-4">{lang === "ta" ? "அதிகபட்சம்" : "Max Price"}</th>
                <th className="py-3 px-6">{lang === "ta" ? "மாதிரி விலை" : "Modal Price"}</th>
                <th className="py-3 px-4 text-right">{lang === "ta" ? "ஆதாரம்" : "Source"}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-xs">
              {filteredRows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50/60 transition-colors">
                  <td className="py-4 px-6 font-semibold text-gray-900">
                    <div>{lang === "ta" ? row.crop_tamil_name || row.crop_name : row.crop_name}</div>
                    <span className="text-[10px] text-gray-400 capitalize">{row.crop_name}</span>
                  </td>
                  <td className="py-4 px-6 text-gray-700">
                    <div className="font-medium">{row.market_name}</div>
                    <span className="text-[11px] text-gray-400">{row.district}</span>
                  </td>
                  <td className="py-4 px-4 font-mono text-gray-600">
                    ₹{Math.round(row.min_price * 100).toLocaleString()}
                  </td>
                  <td className="py-4 px-4 font-mono text-gray-600">
                    ₹{Math.round(row.max_price * 100).toLocaleString()}
                  </td>
                  <td className="py-4 px-6 font-mono font-bold text-gray-900">
                    ₹{Math.round(row.modal_price * 100).toLocaleString()}
                    <span className="text-[10px] font-normal text-gray-400 ml-1">/qtl</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-600 uppercase">
                      {row.source}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
