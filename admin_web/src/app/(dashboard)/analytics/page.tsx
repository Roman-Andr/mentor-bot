"use client";

import { useState, useEffect, useMemo } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PDFExportButton } from "@/components/features/reports/pdf-export-button";
import { api } from "@/lib/api";
import type { ChecklistStats } from "@/types";
import { PageContent } from "@/components/layout/page-content";
import { AnalyticsStats } from "@/components/features/analytics/analytics-stats";
import { MonthlyChart } from "@/components/features/analytics/monthly-chart";
import { DepartmentChart } from "@/components/features/analytics/department-chart";
import { CompletionTimeChart } from "@/components/features/analytics/completion-time-chart";
import { ChecklistStatus } from "@/components/features/analytics/checklist-status";
import { departmentsApi } from "@/lib/api/departments";
import { AnalyticsPageSkeleton } from "@/components/ui/page-skeleton";

export default function AnalyticsPage() {
  const t = useTranslations();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [userCount, setUserCount] = useState(0);
  const [monthlyData, setMonthlyData] = useState<Array<{ month: string; newUsers: number; completed: number }>>([]);
  const [completionTimeData, setCompletionTimeData] = useState<Array<{ range: string; count: number }>>([]);
  const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({});

  useEffect(() => {
    async function loadData() {
      try {
        const [statsResult, usersResult, monthlyResult, completionResult, deptResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
          api.analytics.monthlyStats(),
          api.analytics.completionTimeStats(),
          departmentsApi.list({ limit: 1000 }),
        ]);

        if (statsResult.data) {
          setStats(statsResult.data);
        }
        if (usersResult.data) {
          setUserCount(usersResult.data.total);
        }
        if (monthlyResult.data) {
          setMonthlyData(monthlyResult.data.map(m => ({
            month: m.month,
            newUsers: m.new_checklists,
            completed: m.completed,
          })));
        }
        if (completionResult.data) {
          setCompletionTimeData(completionResult.data);
        }
        if (deptResult.data?.departments) {
          const map: Record<string, string> = {};
          deptResult.data.departments.forEach((dept) => {
            map[String(dept.id)] = dept.name;
          });
          setDepartmentMap(map);
        }
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const departmentData = useMemo(() =>
    stats?.by_department
      ? Object.entries(stats.by_department)
          .filter(([id]) => id !== "None" && id !== "null")
          .map(([id, value], index) => {
            const colors = [
              "#3b82f6", "#8b5cf6", "#22c55e", "#f97316", "#ec4899", "#06b6d4", "#eab308",
            ];
            return {
              name: departmentMap[id] || `Department ${id}`,
              value,
              color: colors[index % colors.length],
            };
          })
      : [],
    [stats, departmentMap]
  );

  const handleExport = () => {
    const rows = [
      [t("analytics.totalNewbies"), String(stats?.total || userCount)],
      [t("common.completed"), String(stats?.completed || 0)],
      [t("common.inProgress"), String(stats?.in_progress || 0)],
      [t("analytics.overdue"), String(stats?.overdue || 0)],
      [t("analytics.averageTime"), String(Math.round(stats?.avg_completion_days || 0))],
      [t("analytics.completionRate"), String(Math.round(stats?.completion_rate || 0))],
    ];

    const csvContent = rows
      .map((row) => row.join(","))
      .join("\n");

    const bom = "\uFEFF";
    const content = bom + csvContent;

    const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "analytics_export.csv";
    link.click();
  };

  if (loading) {
    return (
      <PageContent title={t("analytics.title")} subtitle={t("analytics.overview")}>
        <AnalyticsPageSkeleton />
      </PageContent>
    );
  }

  return (
    <PageContent
      title={t("analytics.title")}
      subtitle={t("analytics.overview")}
      actions={
        <div className="flex items-center gap-2">
          <PDFExportButton
            data={{
              stats,
              userCount,
              monthlyData,
              completionTimeData,
              departmentData,
            }}
            variant="outline"
            size="default"
          />
          <Button onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            CSV
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <AnalyticsStats stats={stats} userCount={userCount} />

        <div className="grid gap-6 lg:grid-cols-2">
          <MonthlyChart data={monthlyData} />
          <DepartmentChart data={departmentData} />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <CompletionTimeChart data={completionTimeData} />
          <ChecklistStatus stats={stats} />
        </div>
      </div>
    </PageContent>
  );
}
