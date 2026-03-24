"use client";

import { useState, useEffect } from "react";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, ChecklistStats } from "@/lib/api";
import { AnalyticsStats } from "@/components/features/analytics/analytics-stats";
import { MonthlyChart } from "@/components/features/analytics/monthly-chart";
import { DepartmentChart } from "@/components/features/analytics/department-chart";
import { CompletionTimeChart } from "@/components/features/analytics/completion-time-chart";
import { ChecklistStatus } from "@/components/features/analytics/checklist-status";

const monthlyData = [
  { month: "Сен", newUsers: 12, completed: 8 },
  { month: "Окт", newUsers: 18, completed: 14 },
  { month: "Ноя", newUsers: 15, completed: 12 },
  { month: "Дек", newUsers: 22, completed: 18 },
  { month: "Янв", newUsers: 28, completed: 20 },
  { month: "Фев", newUsers: 25, completed: 22 },
  { month: "Мар", newUsers: 20, completed: 15 },
];

const completionTimeData = [
  { range: "1-7 дней", count: 15 },
  { range: "8-14 дней", count: 28 },
  { range: "15-21 дней", count: 35 },
  { range: "22-30 дней", count: 18 },
  { range: ">30 дней", count: 8 },
];

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [userCount, setUserCount] = useState(0);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsResult, usersResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
        ]);

        if (statsResult.data) {
          setStats(statsResult.data);
        }
        if (usersResult.data) {
          setUserCount(usersResult.data.total);
        }
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const departmentData = stats?.by_department
    ? Object.entries(stats.by_department).map(([name, value], index) => ({
        name,
        value,
        color: ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444"][index % 5],
      }))
    : [
        { name: "Разработка", value: 45, color: "#3B82F6" },
        { name: "Дизайн", value: 18, color: "#8B5CF6" },
        { name: "QA", value: 15, color: "#10B981" },
        { name: "Маркетинг", value: 22, color: "#F59E0B" },
      ];

  const handleExport = () => {
    const csvContent = [
      ["Метрика", "Значение"],
      ["Всего новичков", stats?.total || userCount],
      ["Завершено", stats?.completed || 0],
      ["В процессе", stats?.in_progress || 0],
      ["Просрочено", stats?.overdue || 0],
      ["Среднее время (дней)", stats?.avg_completion_days || 0],
      ["Процент завершения", stats?.completion_rate || 0],
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "analytics_export.csv";
    link.click();
  };

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">Аналитика</h1>
            <p className="text-muted-foreground">Статистика и отчёты по онбордингу</p>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold">Аналитика</h1>
          <p className="text-muted-foreground">Статистика и отчёты по онбордингу</p>
        </div>
        <Button className="gap-2" onClick={handleExport}>
          <Download className="size-4" />
          Экспорт в CSV
        </Button>
      </div>

      <AnalyticsStats stats={stats} userCount={userCount} />

      <div className="grid gap-4 md:grid-cols-2">
        <MonthlyChart data={monthlyData} />
        <DepartmentChart data={departmentData} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <CompletionTimeChart data={completionTimeData} />
        <ChecklistStatus stats={stats} />
      </div>
    </div>
  );
}
