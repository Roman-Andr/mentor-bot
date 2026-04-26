"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChecklistStats } from "@/types";

interface ChecklistStatusProps {
  stats: ChecklistStats | null;
}

export function ChecklistStatus({ stats }: ChecklistStatusProps) {
  const t = useTranslations();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.checklistStatus")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-green-50 p-3 dark:bg-green-950/50">
            <span className="text-sm text-green-700 dark:text-green-400">{t("common.completed")}</span>
            <span className="font-bold text-green-700 dark:text-green-400">{stats?.completed || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-blue-50 p-3 dark:bg-blue-950/50">
            <span className="text-sm text-blue-700 dark:text-blue-400">{t("common.inProgress")}</span>
            <span className="font-bold text-blue-700 dark:text-blue-400">{stats?.in_progress || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-yellow-50 p-3 dark:bg-yellow-950/50">
            <span className="text-sm text-yellow-700 dark:text-yellow-400">{t("common.notStarted")}</span>
            <span className="font-bold text-yellow-700 dark:text-yellow-400">{stats?.not_started || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-red-50 p-3 dark:bg-red-950/50">
            <span className="text-sm text-red-700 dark:text-red-400">{t("analytics.overdue") || "Overdue"}</span>
            <span className="font-bold text-red-700 dark:text-red-400">{stats?.overdue || 0}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
