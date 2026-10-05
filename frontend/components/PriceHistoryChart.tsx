"use client";

import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface HistoryChartPoint {
  date: string;
  modal: number;
}

interface PriceHistoryChartProps {
  data: HistoryChartPoint[];
  strokeColor: string;
}

export default function PriceHistoryChart({ data, strokeColor }: PriceHistoryChartProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
          <Tooltip
            formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, "Modal Rate"]}
            labelFormatter={(lbl) => `Date: ${lbl}`}
            contentStyle={{
              backgroundColor: "#1e293b",
              color: "#fff",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Line
            type="monotone"
            dataKey="modal"
            stroke={strokeColor}
            strokeWidth={2.5}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
