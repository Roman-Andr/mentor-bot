"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { SearchTimeseriesPoint } from "@/types";

interface SearchTimeseriesChartProps {
  data: SearchTimeseriesPoint[];
}

const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as SearchTimeseriesPoint;
    const date = new Date(data.bucket).toLocaleDateString();
    return (
      <div className="rounded-lg border border-gray-200 bg-white/95 px-3 py-2 text-sm font-medium text-gray-900 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100" style={{ pointerEvents: "none" }}>
        <div>{date}</div>
        {payload.map((entry) => (
          <div key={entry.name}>
            {entry.name}: {entry.value}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function SearchTimeseriesChart({ data }: SearchTimeseriesChartProps) {
  const t = useTranslations();
  const [granularity, setGranularity] = useState<"day" | "week">("day");

  // This would normally trigger a refetch with the new granularity
  // For now, we'll just show the data we have

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    if (granularity === "day") {
      return date.toLocaleDateString();
    }
    return `Week of ${date.toLocaleDateString()}`;
  };

  const chartData = data.map((item) => ({
    ...item,
    formattedDate: formatDate(item.bucket),
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{t("analytics.search.searchTrend")}</CardTitle>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={granularity === "day" ? "default" : "outline"}
              onClick={() => setGranularity("day")}
            >
              {t("analytics.search.day")}
            </Button>
            <Button
              size="sm"
              variant={granularity === "week" ? "default" : "outline"}
              onClick={() => setGranularity("week")}
            >
              {t("analytics.search.week")}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <XAxis
              dataKey="formattedDate"
              tick={{ fontSize: 12 }}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} wrapperStyle={{ transition: "none" }} />
            <Legend />
            <Line
              type="monotone"
              dataKey="search_count"
              stroke="#3B82F6"
              name={t("analytics.search.searchCount")}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="unique_users"
              stroke="#10B981"
              name={t("analytics.search.uniqueUsers")}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
