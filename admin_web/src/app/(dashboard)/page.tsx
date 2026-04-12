"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Clock, CheckCircle, AlertTriangle, TrendingUp } from "lucide-react";
import { useDashboardData } from "@/hooks/use-dashboard-data";
import { StatsCards } from "@/components/features/dashboard/stats-cards";
import { OnboardingProgress } from "@/components/features/dashboard/onboarding-progress";
import { ActivityFeed } from "@/components/features/dashboard/activity-feed";
import { DepartmentBreakdown } from "@/components/features/dashboard/department-breakdown";
import { EscalationSummary } from "@/components/features/dashboard/escalation-summary";

export default function DashboardPage() {
  const t = useTranslations();
  const { stats, progress, activity, departments, escalations, loading, error } =
    useDashboardData();

  const statsData = [
    {
      title: t("dashboard.totalUsers"),
      value: stats.total_users.toString(),
      change: "",
      changeType: "neutral" as const,
      icon: Users,
      color: "bg-blue-500",
    },
    {
      title: t("dashboard.activeUsers"),
      value: stats.active_newbies.toString(),
      change: "",
      changeType: "neutral" as const,
      icon: Clock,
      color: "bg-yellow-500",
    },
    {
      title: t("dashboard.pendingTasks"),
      value: stats.completed_onboarding.toString(),
      change: "",
      changeType: "neutral" as const,
      icon: CheckCircle,
      color: "bg-green-500",
    },
    {
      title: t("dashboard.escalations"),
      value: stats.overdue_tasks.toString(),
      change: "",
      changeType: stats.overdue_tasks > 0 ? "negative" as const : "neutral" as const,
      icon: AlertTriangle,
      color: "bg-red-500",
    },
  ];

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">{t("dashboard.title")}</h1>
            <p className="text-muted-foreground">{t("dashboard.welcome")}</p>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">{t("common.loading")}</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">{t("dashboard.title")}</h1>
            <p className="text-muted-foreground">{t("dashboard.welcome")}</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex h-64 items-center justify-center">
            <div className="text-red-500">{error}</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold">{t("dashboard.title")}</h1>
          <p className="text-muted-foreground">{t("dashboard.welcome")}</p>
        </div>
        <div className="text-muted-foreground flex items-center gap-2 text-sm">
          <TrendingUp className="size-4" />
          <span>
            {t("common.refresh")}: {new Date().toLocaleDateString()}
          </span>
        </div>
      </div>

      <StatsCards statsData={statsData} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <OnboardingProgress progress={progress} />
        <ActivityFeed activity={activity} />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <DepartmentBreakdown departments={departments} />

        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.completionRate")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="py-4 text-center">
              <div className="text-4xl font-bold text-blue-600">
                {stats?.average_completion_days || 0}
              </div>
              <p className="text-muted-foreground mt-2 text-sm">{t("dashboard.daysAverage")}</p>
            </div>
          </CardContent>
        </Card>

        <EscalationSummary escalations={escalations} />
      </div>
    </div>
  );
}
