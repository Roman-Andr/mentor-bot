"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Clock, CheckCircle, AlertTriangle, TrendingUp } from "lucide-react";
import { useDashboardData } from "@/hooks/use-dashboard-data";
import { StatsCards } from "@/components/features/dashboard/stats-cards";
import { OnboardingProgress } from "@/components/features/dashboard/onboarding-progress";
import { ActivityFeed } from "@/components/features/dashboard/activity-feed";
import { DepartmentBreakdown } from "@/components/features/dashboard/department-breakdown";
import { EscalationSummary } from "@/components/features/dashboard/escalation-summary";

export default function DashboardPage() {
  const { stats, progress, activity, departments, escalations, loading, error } =
    useDashboardData();

  const statsData = [
    {
      title: "Всего пользователей",
      value: stats.total_users.toString(),
      change: "",
      changeType: "neutral",
      icon: Users,
      color: "bg-blue-500",
    },
    {
      title: "Новички в процессе",
      value: stats.active_newbies.toString(),
      change: "",
      changeType: "neutral",
      icon: Clock,
      color: "bg-yellow-500",
    },
    {
      title: "Завершили онбординг",
      value: stats.completed_onboarding.toString(),
      change: "",
      changeType: "neutral",
      icon: CheckCircle,
      color: "bg-green-500",
    },
    {
      title: "Просроченные задачи",
      value: stats.overdue_tasks.toString(),
      change: "",
      changeType: stats.overdue_tasks > 0 ? "negative" : "neutral",
      icon: AlertTriangle,
      color: "bg-red-500",
    },
  ];

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">Дашборд</h1>
            <p className="text-muted-foreground">Обзор процесса онбординга</p>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">Дашборд</h1>
            <p className="text-muted-foreground">Обзор процесса онбординга</p>
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
          <h1 className="text-foreground text-2xl font-bold">Дашборд</h1>
          <p className="text-muted-foreground">Обзор процесса онбординга</p>
        </div>
        <div className="text-muted-foreground flex items-center gap-2 text-sm">
          <TrendingUp className="size-4" />
          <span>Обновлено: {new Date().toLocaleDateString("ru-RU")}</span>
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
            <CardTitle>Среднее время онбординга</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="py-4 text-center">
              <div className="text-4xl font-bold text-blue-600">
                {stats?.average_completion_days || 0}
              </div>
              <p className="text-muted-foreground mt-2 text-sm">дней в среднем</p>
            </div>
          </CardContent>
        </Card>

        <EscalationSummary escalations={escalations} />
      </div>
    </div>
  );
}
