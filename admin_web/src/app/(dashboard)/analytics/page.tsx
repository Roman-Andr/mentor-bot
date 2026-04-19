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

export default function AnalyticsPage() {
  const t = useTranslations();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [userCount, setUserCount] = useState(0);
  const [monthlyData, setMonthlyData] = useState<Array<{ month: string; newUsers: number; completed: number }>>([]);
  const [completionTimeData, setCompletionTimeData] = useState<Array<{ range: string; count: number }>>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsResult, usersResult, monthlyResult, completionResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
          api.analytics.monthlyStats(),
          api.analytics.completionTimeStats(),
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
      ? Object.entries(stats.by_department).map(([name, value]) => ({
          name,
          value,
          color: "", // Color is assigned in the chart component
        }))
      : [],
    [stats?.by_department]
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
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">{t("common.loading")}</div>
        </div>
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
