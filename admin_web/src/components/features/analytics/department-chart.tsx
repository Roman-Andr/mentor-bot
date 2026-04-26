"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, TooltipProps } from "recharts";

interface DepartmentData {
  name: string;
  value: number;
  color?: string;
}

interface DepartmentChartProps {
  data: DepartmentData[];
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

const CustomTooltip = (props: TooltipProps<number, string>) => {
  const { active, payload } = props;
  if (active && payload && payload.length) {
    const data = payload[0].payload as DepartmentData;
    return (
      <div className="rounded-lg border border-gray-200 bg-white/95 px-3 py-2 text-sm font-medium text-gray-900 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100" style={{ pointerEvents: "none" }}>
        {data.name}: {data.value}
      </div>
    );
  }
  return null;
};

export function DepartmentChart({ data }: DepartmentChartProps) {
  const t = useTranslations();

  const dataWithColors = data.map((item, index) => ({
    ...item,
    color: item.color || DEPARTMENT_COLORS[index % DEPARTMENT_COLORS.length],
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.byDepartments")}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={dataWithColors}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={100}
              activeOuterRadius={100}
              paddingAngle={2}
              dataKey="value"
              label={false}
            >
              {dataWithColors.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} wrapperStyle={{ transition: "none" }} />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value, entry) => {
                const data = entry.payload as { name: string; value: number };
                return `${data.name}: ${data.value}`;
              }}
              wrapperStyle={{ paddingTop: "20px" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
