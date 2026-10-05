"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface ForecastChartPoint {
  date: string;
  predicted: number;
  lower: number;
  upper: number;
}

interface ForecastAreaChartProps {
  data: ForecastChartPoint[];
}

export default function ForecastAreaChart({ data }: ForecastAreaChartProps) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
          <Tooltip
            formatter={(val: any, name: string) => [
              `₹${Number(val).toLocaleString()}`,
              name === "predicted"
                ? "Predicted (p50)"
                : name === "upper"
                ? "Upper Bound (p90)"
                : "Lower Bound (p10)",
            ]}
            contentStyle={{
              backgroundColor: "#1e293b",
              color: "#fff",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="upper"
            stroke="transparent"
            fill="#10b981"
            fillOpacity={0.15}
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="transparent"
            fill="#ffffff"
            fillOpacity={1.0}
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#10b981"
            strokeWidth={3}
            dot={{ r: 4, fill: "#10b981" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
