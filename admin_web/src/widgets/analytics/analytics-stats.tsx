"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { TrendingUp, Users, Clock, CheckCircle, AlertTriangle } from "lucide-react";
import type { ChecklistStats } from "@/shared/types";
import { cn } from "@/shared/lib/utils";

interface AnalyticsStatsProps {
  stats: ChecklistStats | null;
  userCount: number;
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  iconClass: string;
  gradientFrom: string;
  gradientTo: string;
  subtitle?: string;
}

function StatCard({
  label,
  value,
  icon: Icon,
  iconClass,
  gradientFrom,
  gradientTo,
  subtitle,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border bg-gradient-to-br p-5",
        gradientFrom,
        gradientTo,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{label}</p>
          <p className="mt-1.5 text-3xl font-bold">{value}</p>
          {subtitle && <p className="mt-1 text-xs opacity-60">{subtitle}</p>}
        </div>
        <div className={cn("rounded-xl p-2.5", iconClass)}>
          <Icon className="size-5" />
        </div>
      </div>
    </div>
  );
}

export function AnalyticsStats({ stats, userCount }: AnalyticsStatsProps) {
  const t = useTranslations();
  const completionRate = Math.round(stats?.completion_rate || 0);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label={t("analytics.totalNewbies")}
        value={stats?.total || userCount}
        icon={Users}
        iconClass="bg-blue-500/20 text-blue-500 dark:bg-blue-400/20 dark:text-blue-400"
        gradientFrom="from-blue-50 dark:from-blue-950/20"
        gradientTo="to-blue-100/50 dark:to-blue-900/10"
        subtitle={`${stats?.completed || 0} ${t("common.completed")}`}
      />
      <StatCard
        label={t("analytics.averageTime")}
        value={`${Math.round(stats?.avg_completion_days || 0)} ${t("common.days")}`}
        icon={Clock}
        iconClass="bg-violet-500/20 text-violet-500 dark:bg-violet-400/20 dark:text-violet-400"
        gradientFrom="from-violet-50 dark:from-violet-950/20"
        gradientTo="to-violet-100/50 dark:to-violet-900/10"
      />
      <StatCard
        label={t("analytics.successfulCompletions")}
        value={`${completionRate}%`}
        icon={CheckCircle}
        iconClass="bg-emerald-500/20 text-emerald-500 dark:bg-emerald-400/20 dark:text-emerald-400"
        gradientFrom="from-emerald-50 dark:from-emerald-950/20"
        gradientTo="to-emerald-100/50 dark:to-emerald-900/10"
        subtitle={`${stats?.completed || 0} / ${stats?.total || 0}`}
      />
      <StatCard
        label={t("analytics.inProgressStatus")}
        value={stats?.in_progress || 0}
        icon={stats?.overdue ? AlertTriangle : TrendingUp}
        iconClass={
          stats?.overdue
            ? "bg-red-500/20 text-red-500 dark:bg-red-400/20 dark:text-red-400"
            : "bg-amber-500/20 text-amber-500 dark:bg-amber-400/20 dark:text-amber-400"
        }
        gradientFrom={
          stats?.overdue
            ? "from-red-50 dark:from-red-950/20"
            : "from-amber-50 dark:from-amber-950/20"
        }
        gradientTo={
          stats?.overdue
            ? "to-red-100/50 dark:to-red-900/10"
            : "to-amber-100/50 dark:to-amber-900/10"
        }
        subtitle={stats?.overdue ? `${stats.overdue} ${t("analytics.overdue")}` : undefined}
      />
    </div>
  );
}
