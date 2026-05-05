"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Users, Clock, CheckCircle, AlertTriangle, UserPlus, Mail, RefreshCw, TrendingUp } from "lucide-react";
import { useDashboardData } from "@/shared/hooks/use-dashboard-data";
import { StatsCards } from "@/widgets/dashboard/stats-cards";
import { OnboardingProgress } from "@/widgets/dashboard/onboarding-progress";
import { ActivityFeed } from "@/widgets/dashboard/activity-feed";
import { DepartmentBreakdown } from "@/widgets/dashboard/department-breakdown";
import { EscalationSummary } from "@/widgets/dashboard/escalation-summary";
import { DashboardPageSkeleton } from "@/shared/ui/page-skeleton";
import Link from "next/link";

export function DashboardWidget() {
  const t = useTranslations();
  const { stats, progress, activity, departments, escalations, loading, error, refetch } = useDashboardData();

  const statsData = [
    {
      title: t("dashboard.totalUsers"),
      value: stats.total_users.toString(),
      change: "",
      changeType: "neutral" as const,
      icon: Users,
      color: "bg-blue-500",
      description: t("dashboard.registeredInSystem"),
    },
    {
      title: t("dashboard.activeUsers"),
      value: stats.active_newbies.toString(),
      change: "",
      changeType: "neutral" as const,
      icon: Clock,
      color: "bg-yellow-500",
      description: t("dashboard.currentlyOnboarding"),
    },
    {
      title: t("dashboard.completedOnboarding"),
      value: stats.completed_onboarding.toString(),
      change: "",
      changeType: stats.completed_onboarding > 0 ? ("positive" as const) : ("neutral" as const),
      icon: CheckCircle,
      color: "bg-green-500",
      description: t("dashboard.successfullyCompleted"),
    },
    {
      title: t("dashboard.escalations"),
      value: escalations.inProgress.toString(),
      change: escalations.inProgress > 0 ? t("dashboard.requiresAttention") : "",
      changeType: escalations.inProgress > 0 ? ("negative" as const) : ("neutral" as const),
      icon: AlertTriangle,
      color: "bg-red-500",
      description: t("dashboard.openEscalations"),
    },
  ];

  if (loading) return <DashboardPageSkeleton />;

  if (error) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-foreground text-2xl font-bold">{t("dashboard.title")}</h1>
            <p className="text-muted-foreground">{t("dashboard.welcome")}</p>
          </div>
        </div>
        <Card className="border-red-200 bg-red-50 dark:border-red-800/30 dark:bg-red-950/30">
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
            <AlertTriangle className="size-10 text-red-500" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            <Button variant="outline" size="sm" onClick={refetch} className="gap-2">
              <RefreshCw className="size-4" />
              {t("common.retry")}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-foreground text-2xl font-bold tracking-tight">{t("dashboard.title")}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">{t("dashboard.welcome")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/invitations">
            <Button variant="outline" size="sm" className="gap-2">
              <Mail className="size-4" />
              {t("invitations.sendInvitation")}
            </Button>
          </Link>
          <Link href="/users">
            <Button size="sm" className="gap-2">
              <UserPlus className="size-4" />
              {t("users.addUser")}
            </Button>
          </Link>
          <Button variant="ghost" size="icon" onClick={refetch} title={t("common.refresh")}>
            <RefreshCw className="size-4" />
          </Button>
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
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{t("dashboard.completionRate")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-4">
              <div className="relative flex size-24 items-center justify-center">
                <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted opacity-20" />
                  <circle
                    cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="8"
                    strokeDasharray={`${2 * Math.PI * 42}`}
                    strokeDashoffset={`${2 * Math.PI * 42 * (1 - Math.min(stats.average_completion_days / 90, 1))}`}
                    className="text-blue-500"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{stats?.average_completion_days || 0}</div>
                  <div className="text-muted-foreground text-xs">{t("dashboard.days")}</div>
                </div>
              </div>
              <p className="text-muted-foreground mt-3 text-center text-sm">{t("dashboard.daysAverage")}</p>
            </div>
            <div className="mt-2 space-y-2 border-t pt-3">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">{t("analytics.overdue")}</span>
                <span className="font-medium text-red-500">{stats.overdue_tasks}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">{t("dashboard.notStarted")}</span>
                <span className="text-muted-foreground font-medium">{stats.pending_tasks}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <EscalationSummary escalations={escalations} />
      </div>

      <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
        <TrendingUp className="size-3" />
        <span>{t("common.refresh")}: {new Date().toLocaleDateString()}</span>
      </div>
    </div>
  );
}
