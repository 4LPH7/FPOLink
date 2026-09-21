"use client";

import React from "react";
import {
  Layers,
  Sprout,
  Store,
  CheckCircle2,
  Clock,
  ArrowRight,
  Boxes,
  Award,
} from "lucide-react";

interface AggregationSummaryProps {
  lang: "ta" | "en";
  t: any;
}

export default function AggregationSummary({ lang, t }: AggregationSummaryProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200/90 p-5 sm:p-6 shadow-xs">
      {/* Card Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-green-50 text-green-700 flex items-center justify-center font-bold">
            <Boxes className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-gray-900 tracking-tight">
              {t.nav.aggregation} & {t.dashboard.todays_produce}
            </h3>
            <p className="text-xs text-gray-500">
              {lang === "ta"
                ? "விவசாயிகளின் சிறிய விளைச்சல்களை தரவாரியாக தொகுத்து வணிக விற்பனைக்கு தயார் செய்தல்"
                : "Aggregating farm harvests into grade-sorted wholesale commercial batches"}
            </p>
          </div>
        </div>

        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800">
          12,600 kg {lang === "ta" ? "மொத்தம்" : "Total Pooled"}
        </span>
      </div>

      {/* Batch Lots Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
        {/* Turmeric Batch */}
        <div className="p-4 rounded-xl border border-yellow-200/70 bg-gradient-to-br from-yellow-50/40 to-amber-50/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xl">🌾</span>
              <div>
                <h4 className="font-bold text-gray-900 text-sm">
                  {lang === "ta" ? "மஞ்சள் தொகுதி #TUR-ERD-08" : "Turmeric Batch #TUR-ERD-08"}
                </h4>
                <span className="text-[11px] text-gray-500 font-medium">
                  {lang === "ta" ? "42 விவசாயிகள் விளைச்சல்" : "Contributed by 42 farmers"}
                </span>
              </div>
            </div>
            <span className="text-sm font-extrabold text-gray-900 bg-white px-2.5 py-1 rounded-lg border border-yellow-200 shadow-xs">
              8,400 kg
            </span>
          </div>

          {/* Grade Distribution Bar */}
          <div className="space-y-2 text-xs">
            <div className="flex justify-between font-semibold text-gray-700">
              <span>{lang === "ta" ? "தர நிர்ணயம் (Grade Breakdown):" : "Quality Grade Breakdown:"}</span>
              <span className="text-green-700 font-bold">57% Grade A</span>
            </div>

            {/* Multi-segment Bar */}
            <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden flex">
              <div style={{ width: "57%" }} className="bg-emerald-600" title="Grade A: 4,800 kg"></div>
              <div style={{ width: "33%" }} className="bg-amber-500" title="Grade B: 2,800 kg"></div>
              <div style={{ width: "10%" }} className="bg-orange-400" title="Grade C: 800 kg"></div>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-1 text-[11px]">
              <div className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60">
                <span className="text-gray-500 block">Grade A</span>
                <span className="font-bold text-gray-900">4,800 kg</span>
              </div>
              <div className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60">
                <span className="text-gray-500 block">Grade B</span>
                <span className="font-bold text-gray-900">2,800 kg</span>
              </div>
              <div className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60">
                <span className="text-gray-500 block">Grade C</span>
                <span className="font-bold text-gray-900">800 kg</span>
              </div>
            </div>
          </div>

          {/* Dispatch Status */}
          <div className="mt-3 pt-3 border-t border-yellow-200/60 flex items-center justify-between text-xs">
            <span className="text-emerald-700 font-bold flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              {lang === "ta" ? "வணிக விற்பனைக்கு தயார்" : "Ready for Wholesale Dispatch"}
            </span>
            <span className="text-gray-500 text-[11px]">
              {lang === "ta" ? "ஈரோடு கிடங்கு #2" : "Erode Warehouse #2"}
            </span>
          </div>
        </div>

        {/* Banana Batch */}
        <div className="p-4 rounded-xl border border-green-200/70 bg-gradient-to-br from-green-50/40 to-emerald-50/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xl">🍌</span>
              <div>
                <h4 className="font-bold text-gray-900 text-sm">
                  {lang === "ta" ? "வாழை தொகுதி #BAN-KOD-04" : "Banana Batch #BAN-KOD-04"}
                </h4>
                <span className="text-[11px] text-gray-500 font-medium">
                  {lang === "ta" ? "18 விவசாயிகள் விளைச்சல் (கொடுமுடி)" : "Contributed by 18 farmers (Kodumudi)"}
                </span>
              </div>
            </div>
            <span className="text-sm font-extrabold text-gray-900 bg-white px-2.5 py-1 rounded-lg border border-green-200 shadow-xs">
              4,200 kg
            </span>
          </div>

          {/* Grade Distribution Bar */}
          <div className="space-y-2 text-xs">
            <div className="flex justify-between font-semibold text-gray-700">
              <span>{lang === "ta" ? "தர நிர்ணயம் (Grade Breakdown):" : "Quality Grade Breakdown:"}</span>
              <span className="text-green-700 font-bold">71% Grade A</span>
            </div>

            {/* Multi-segment Bar */}
            <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden flex">
              <div style={{ width: "71%" }} className="bg-emerald-600" title="Grade A: 3,000 kg"></div>
              <div style={{ width: "29%" }} className="bg-amber-500" title="Grade B: 1,200 kg"></div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
              <div className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60">
                <span className="text-gray-500 block">Grade A (Export / Retail)</span>
                <span className="font-bold text-gray-900">3,000 kg</span>
              </div>
              <div className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60">
                <span className="text-gray-500 block">Grade B (Processing)</span>
                <span className="font-bold text-gray-900">1,200 kg</span>
              </div>
            </div>
          </div>

          {/* Dispatch Status */}
          <div className="mt-3 pt-3 border-t border-green-200/60 flex items-center justify-between text-xs">
            <span className="text-emerald-700 font-bold flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              {lang === "ta" ? "கொள்முதலாளர் ஒப்பந்தம் தயார்" : "Matched with Buyer Contract"}
            </span>
            <span className="text-gray-500 text-[11px]">
              {lang === "ta" ? "கொடுமுடி குளிர்பதன கிடங்கு" : "Kodumudi Cold Storage"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
