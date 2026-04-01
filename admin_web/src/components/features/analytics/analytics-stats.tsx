"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, Users, Clock, CheckCircle } from "lucide-react";
import { ChecklistStats } from "@/lib/api";

interface AnalyticsStatsProps {
  stats: ChecklistStats | null;
  userCount: number;
}

export function AnalyticsStats({ stats, userCount }: AnalyticsStatsProps) {
  const t = useTranslations("analytics");

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("totalNewbies")}</p>
              <p className="text-2xl font-bold">{stats?.total || userCount}</p>
            </div>
            <Users className="size-8 text-blue-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("averageTime")}</p>
              <p className="text-2xl font-bold">
                {Math.round(stats?.avg_completion_days || 0)} {t("days")}
              </p>
            </div>
            <Clock className="size-8 text-purple-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("successfulCompletions")}</p>
              <p className="text-2xl font-bold">{Math.round(stats?.completion_rate || 0)}%</p>
            </div>
            <CheckCircle className="size-8 text-green-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("inProgressStatus")}</p>
              <p className="text-2xl font-bold">{stats?.in_progress || 0}</p>
            </div>
            <TrendingUp className="size-8 text-yellow-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
