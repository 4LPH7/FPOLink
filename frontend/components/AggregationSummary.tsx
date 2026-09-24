"use client";

import React, { useEffect, useState } from "react";
import { Boxes, CheckCircle2, Clock, Loader2 } from "lucide-react";
import { getHarvestAggregation, HarvestAggregation, HarvestBatch } from "@/lib/api";

interface AggregationSummaryProps {
  lang: "ta" | "en";
  t: any;
}

const CROP_EMOJI: Record<string, string> = {
  turmeric: "🌾",
  மஞ்சள்: "🌾",
  banana: "🍌",
  வாழை: "🍌",
  coconut: "🥥",
  தேங்காய்: "🥥",
};

function cropEmoji(name: string): string {
  const key = Object.keys(CROP_EMOJI).find((k) =>
    name.toLowerCase().includes(k)
  );
  return key ? CROP_EMOJI[key] : "🌱";
}

function BatchCard({ batch, lang }: { batch: HarvestBatch; lang: "ta" | "en" }) {
  const displayName =
    lang === "ta" && batch.crop_tamil_name
      ? batch.crop_tamil_name
      : batch.crop_name;

  const gradeA = batch.grades.find((g) => g.grade === "A");
  const gradeB = batch.grades.find((g) => g.grade === "B");
  const gradeC = batch.grades.find((g) => g.grade === "C");

  const pctA = gradeA?.percentage ?? 0;
  const pctB = gradeB?.percentage ?? 0;
  const pctC = gradeC?.percentage ?? 0;

  const isReady =
    batch.status === "AGGREGATED" || batch.status === "VERIFIED";

  return (
    <div className="p-4 rounded-xl border border-gray-200/70 bg-gradient-to-br from-gray-50/40 to-white">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xl">{cropEmoji(batch.crop_name)}</span>
          <div>
            <h4 className="font-bold text-gray-900 text-sm">{displayName}</h4>
            <span className="text-[11px] text-gray-500 font-medium">
              {lang === "ta"
                ? `${batch.farmer_count} விவசாயிகள் விளைச்சல்`
                : `${batch.farmer_count} farmer${batch.farmer_count !== 1 ? "s" : ""}`}
            </span>
          </div>
        </div>
        <span className="text-sm font-extrabold text-gray-900 bg-white px-2.5 py-1 rounded-lg border border-gray-200 shadow-xs">
          {batch.total_kg.toLocaleString("en-IN")} kg
        </span>
      </div>

      {/* Grade Breakdown Bar */}
      {batch.grades.length > 0 && (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between font-semibold text-gray-700">
            <span>
              {lang === "ta" ? "தர நிர்ணயம்:" : "Grade Breakdown:"}
            </span>
            {gradeA && (
              <span className="text-green-700 font-bold">
                {Math.round(pctA)}% Grade A
              </span>
            )}
          </div>

          <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden flex">
            {pctA > 0 && (
              <div
                style={{ width: `${pctA}%` }}
                className="bg-emerald-600"
                title={`Grade A: ${gradeA?.quantity_kg ?? 0} kg`}
              />
            )}
            {pctB > 0 && (
              <div
                style={{ width: `${pctB}%` }}
                className="bg-amber-500"
                title={`Grade B: ${gradeB?.quantity_kg ?? 0} kg`}
              />
            )}
            {pctC > 0 && (
              <div
                style={{ width: `${pctC}%` }}
                className="bg-orange-400"
                title={`Grade C: ${gradeC?.quantity_kg ?? 0} kg`}
              />
            )}
          </div>

          <div
            className={`grid gap-2 pt-1 text-[11px]`}
            style={{ gridTemplateColumns: `repeat(${batch.grades.length}, 1fr)` }}
          >
            {batch.grades.map((g) => (
              <div
                key={g.grade}
                className="bg-white/80 p-1.5 rounded-lg border border-gray-200/60"
              >
                <span className="text-gray-500 block">Grade {g.grade}</span>
                <span className="font-bold text-gray-900">
                  {g.quantity_kg.toLocaleString("en-IN")} kg
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status + Warehouse */}
      <div className="mt-3 pt-3 border-t border-gray-200/60 flex items-center justify-between text-xs">
        <span
          className={`font-bold flex items-center ${
            isReady ? "text-emerald-700" : "text-amber-700"
          }`}
        >
          {isReady ? (
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
          ) : (
            <Clock className="w-3.5 h-3.5 mr-1" />
          )}
          {isReady
            ? lang === "ta"
              ? "வணிக விற்பனைக்கு தயார்"
              : "Ready for Dispatch"
            : lang === "ta"
            ? "சரிபார்ப்பு நிலுவையில்"
            : "Pending Verification"}
        </span>
        {batch.warehouse && (
          <span className="text-gray-500 text-[11px]">{batch.warehouse}</span>
        )}
      </div>
    </div>
  );
}

export default function AggregationSummary({ lang, t }: AggregationSummaryProps) {
  const [data, setData] = useState<HarvestAggregation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHarvestAggregation()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  const totalKg = data?.total_pooled_kg ?? 0;

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
          {totalKg > 0
            ? `${totalKg.toLocaleString("en-IN")} kg ${lang === "ta" ? "மொத்தம்" : "Pooled"}`
            : lang === "ta"
            ? "தரவு இல்லை"
            : "No batches"}
        </span>
      </div>

      {/* Content */}
      <div className="mt-5">
        {loading ? (
          <div className="flex items-center justify-center py-10 text-gray-400 text-sm">
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            {lang === "ta" ? "தரவு ஏற்றப்படுகிறது..." : "Loading aggregation data..."}
          </div>
        ) : !data || data.batches.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-xs space-y-2">
            <Boxes className="w-8 h-8 mx-auto opacity-30" />
            <p className="font-semibold text-gray-500">
              {lang === "ta"
                ? "தற்போது செயலில் உள்ள அறுவடை தொகுதிகள் இல்லை"
                : "No active harvest batches"}
            </p>
            <p className="text-[11px]">
              {lang === "ta"
                ? "விவசாயிகள் வாட்ஸ்அப்பில் அறுவடை சமர்ப்பிக்கும்போது இங்கே காட்டப்படும்"
                : "Batches appear here when farmers submit harvests via WhatsApp"}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {data.batches.map((batch, i) => (
              <BatchCard key={`${batch.crop_name}-${i}`} batch={batch} lang={lang} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
