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
    <div className="group rounded-2xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md sm:p-5">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
        <div className={`flex size-10 shrink-0 items-center justify-center rounded-xl ${iconColor}`}>
          <Icon className="size-5" />
        </div>
      </div>

      <div className="mt-3">
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold tracking-tight text-foreground tabular-nums sm:text-3xl">
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
          <span className="ml-1 truncate text-muted-foreground">{subtitle}</span>
          )}
        </div>
      </div>
    </div>
  );
}
