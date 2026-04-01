"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, ChecklistStats } from "@/lib/api";
import { AnalyticsStats } from "@/components/features/analytics/analytics-stats";
import { MonthlyChart } from "@/components/features/analytics/monthly-chart";
import { DepartmentChart } from "@/components/features/analytics/department-chart";
import { CompletionTimeChart } from "@/components/features/analytics/completion-time-chart";
import { ChecklistStatus } from "@/components/features/analytics/checklist-status";

const monthlyData = [
  { month: "Sep", newUsers: 12, completed: 8 },
  { month: "Oct", newUsers: 18, completed: 14 },
  { month: "Nov", newUsers: 15, completed: 12 },
  { month: "Dec", newUsers: 22, completed: 18 },
  { month: "Jan", newUsers: 28, completed: 20 },
  { month: "Feb", newUsers: 25, completed: 22 },
  { month: "Mar", newUsers: 20, completed: 15 },
];

const completionTimeData = [
  { range: "1-7 days", count: 15 },
  { range: "8-14 days", count: 28 },
  { range: "15-21 days", count: 35 },
  { range: "22-30 days", count: 18 },
  { range: ">30 days", count: 8 },
];

export default function AnalyticsPage() {
  const t = useTranslations("analytics");
  const tCommon = useTranslations("common");
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
        { name: "Development", value: 45, color: "#3B82F6" },
        { name: "Design", value: 18, color: "#8B5CF6" },
        { name: "QA", value: 15, color: "#10B981" },
        { name: "Marketing", value: 22, color: "#F59E0B" },
      ];

  const handleExport = () => {
    const csvContent = [
      [t("totalNewbies"), String(stats?.total || userCount)],
      [tCommon("completed"), String(stats?.completed || 0)],
      [tCommon("inProgress"), String(stats?.in_progress || 0)],
      [t("overdue"), String(stats?.overdue || 0)],
      [t("averageTime"), String(Math.round(stats?.avg_completion_days || 0))],
      [t("completionRate"), String(Math.round(stats?.completion_rate || 0))],
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
            <h1 className="text-foreground text-2xl font-bold">{t("title")}</h1>
            <p className="text-muted-foreground">{t("overview")}</p>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">{tCommon("loading")}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold">{t("title")}</h1>
          <p className="text-muted-foreground">{t("overview")}</p>
        </div>
        <Button className="gap-2" onClick={handleExport}>
          <Download className="size-4" />
          {tCommon("export")}
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
