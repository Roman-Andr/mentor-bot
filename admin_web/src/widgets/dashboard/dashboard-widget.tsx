"use client";

import { useMemo } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Users, Clock, CheckCircle, AlertTriangle, RefreshCw, TrendingUp } from "lucide-react";
import { useDashboardData } from "@/shared/hooks/use-dashboard-data";
import { StatsCards } from "@/widgets/dashboard/stats-cards";
import { OnboardingProgress } from "@/widgets/dashboard/onboarding-progress";
import { ActivityFeed } from "@/widgets/dashboard/activity-feed";
import { DepartmentBreakdown } from "@/widgets/dashboard/department-breakdown";
import { CompletionRateCard } from "@/widgets/dashboard/completion-rate-card";
import { EscalationSummary } from "@/widgets/dashboard/escalation-summary";
import { DashboardPageSkeleton } from "@/shared/ui/page-skeleton";
import { DashboardHeader } from "@/widgets/dashboard/dashboard-header";

export function DashboardWidget() {
  const t = useTranslations();
  const { stats, progress, activity, departments, escalations, loading, error, refetch } =
    useDashboardData();

  const statsData = useMemo(
    () => [
      {
        title: t("dashboard.totalUsers"),
        value: stats.total_users.toString(),
        change: "",
        changeType: "neutral" as const,
        icon: Users,
        color: "bg-blue-500",
        description: t("dashboard.registeredInSystem"),
        href: "/users",
      },
      {
        title: t("dashboard.activeUsers"),
        value: stats.active_newbies.toString(),
        change: "",
        changeType: "neutral" as const,
        icon: Clock,
        color: "bg-yellow-500",
        description: t("dashboard.currentlyOnboarding"),
        href: "/checklists?status=in_progress",
      },
      {
        title: t("dashboard.completedOnboarding"),
        value: stats.completed_onboarding.toString(),
        change: "",
        changeType: stats.completed_onboarding > 0 ? ("positive" as const) : ("neutral" as const),
        icon: CheckCircle,
        color: "bg-green-500",
        description: t("dashboard.successfullyCompleted"),
        href: "/checklists?status=completed",
      },
      {
        title: t("dashboard.escalations"),
        value: escalations.inProgress.toString(),
        change: escalations.inProgress > 0 ? t("dashboard.requiresAttention") : "",
        changeType: escalations.inProgress > 0 ? ("negative" as const) : ("neutral" as const),
        icon: AlertTriangle,
        color: "bg-red-500",
        description: t("dashboard.openEscalations"),
        href: "/escalations?status=open",
      },
    ],
    [stats, escalations, t],
  );

  if (loading) return <DashboardPageSkeleton />;

  if (error) {
    return (
      <div className="space-y-6 p-6">
        <DashboardHeader t={t} />
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
    <div className="space-y-4 p-4 sm:space-y-6 sm:p-6">
      <DashboardHeader t={t} onRefresh={refetch} />

      <StatsCards statsData={statsData} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-7">
        <OnboardingProgress progress={progress} href="/checklists?status=in_progress" />
        <ActivityFeed activity={activity} href="/analytics?tab=history" />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <DepartmentBreakdown departments={departments} href="/users?tab=departments" />
        <CompletionRateCard stats={stats} href="/analytics?tab=completion" />
        <EscalationSummary escalations={escalations} />
      </div>

      <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
        <TrendingUp className="size-3" />
        <span>
          {t("common.refresh")}: {new Date().toLocaleDateString()}
        </span>
      </div>
    </div>
  );
}
