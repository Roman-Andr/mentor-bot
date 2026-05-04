"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, type TooltipProps } from "recharts";
import type { DepartmentSearchStats } from "@/types";

interface SearchByDepartmentChartProps {
  data: DepartmentSearchStats[];
}

const DEPARTMENT_COLORS = [
  "#3B82F6", // blue
  "#10B981", // green
  "#F59E0B", // amber
  "#EF4444", // red
  "#8B5CF6", // purple
  "#EC4899", // pink
  "#06B6D4", // cyan
  "#6366F1", // indigo
  "#14B8A6", // teal
  "#D97706", // orange
];

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: DepartmentSearchStats; name: string; value: number }> }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as DepartmentSearchStats;
    return (
      <div className="rounded-lg border border-gray-200 bg-white/95 px-3 py-2 text-sm font-medium text-gray-900 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100" style={{ pointerEvents: "none" }}>
        <div>{data.department_name}</div>
        <div>{payload[0].name}: {payload[0].value}</div>
      </div>
    );
  }
  return null;
};

export function SearchByDepartmentChart({ data }: SearchByDepartmentChartProps) {
  const t = useTranslations();

  const dataWithColors = data.map((item, index) => ({
    ...item,
    fill: DEPARTMENT_COLORS[index % DEPARTMENT_COLORS.length],
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.search.byDepartment")}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={dataWithColors}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <XAxis type="number" />
            <YAxis
              type="category"
              dataKey="department_name"
              width={150}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} wrapperStyle={{ transition: "none" }} />
            <Legend />
            <Bar dataKey="search_count" name={t("analytics.search.searchCount")} fill="#3B82F6" />
            <Bar dataKey="unique_users" name={t("analytics.search.uniqueUsers")} fill="#10B981" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
