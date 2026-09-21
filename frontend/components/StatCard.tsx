"use client";

import React from "react";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon: React.ComponentType<{ className?: string }>;
  iconColor?: string;
  badge?: string;
}

export default function StatCard({
  title,
  value,
  subtitle,
  change,
  changeType = "positive",
  icon: Icon,
  iconColor = "text-green-600 bg-green-50",
  badge,
}: StatCardProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-gray-200/80 shadow-xs hover:shadow-md transition-all hover:border-gray-300 group">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-500 tracking-wider uppercase">
          {title}
        </span>
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${iconColor} transition-transform group-hover:scale-105`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3">
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            {value}
          </span>
          {badge && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800">
              {badge}
            </span>
          )}
        </div>

        <div className="mt-2 flex items-center justify-between text-xs">
          {change && (
            <span
              className={`inline-flex items-center font-semibold ${
                changeType === "positive"
                  ? "text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded"
                  : changeType === "negative"
                  ? "text-red-700 bg-red-50 px-1.5 py-0.5 rounded"
                  : "text-gray-600 bg-gray-50 px-1.5 py-0.5 rounded"
              }`}
            >
              {changeType === "positive" && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
              {changeType === "negative" && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
              {changeType === "neutral" && <Minus className="w-3.5 h-3.5 mr-0.5" />}
              {change}
            </span>
          )}
          {subtitle && (
            <span className="text-gray-500 font-medium truncate ml-1">{subtitle}</span>
          )}
        </div>
      </div>
    </div>
  );
}
