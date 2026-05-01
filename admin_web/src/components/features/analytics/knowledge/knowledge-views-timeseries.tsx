"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TimeseriesPoint {
  bucket: string;
  views: number;
  unique_viewers: number;
}

interface KnowledgeViewsTimeseriesProps {
  data: TimeseriesPoint[];
  onGranularityChange: (granularity: "day" | "week") => void;
  currentGranularity: "day" | "week";
}

export function KnowledgeViewsTimeseries({ data, onGranularityChange, currentGranularity }: KnowledgeViewsTimeseriesProps) {
  const t = useTranslations();

  const chartData = data.map((item) => ({
    date: new Date(item.bucket).toLocaleDateString(),
    views: item.views,
    uniqueViewers: item.unique_viewers,
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{t("analytics.knowledge.viewsOverTime")}</CardTitle>
          <div className="flex gap-2">
            <Button
              variant={currentGranularity === "day" ? "default" : "outline"}
              size="sm"
              onClick={() => onGranularityChange("day")}
            >
              {t("analytics.knowledge.day")}
            </Button>
            <Button
              variant={currentGranularity === "week" ? "default" : "outline"}
              size="sm"
              onClick={() => onGranularityChange("week")}
            >
              {t("analytics.knowledge.week")}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="views"
              name={t("analytics.knowledge.views")}
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="uniqueViewers"
              name={t("analytics.knowledge.uniqueViewers")}
              stroke="#10B981"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
