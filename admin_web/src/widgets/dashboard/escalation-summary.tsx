import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { AlertTriangle, Users, Activity, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

interface EscalationCounts {
  hr: number;
  mentor: number;
  inProgress: number;
}

interface EscalationSummaryProps {
  escalations: EscalationCounts;
}

export function EscalationSummary({ escalations }: EscalationSummaryProps) {
  const t = useTranslations();
  const total = escalations.hr + escalations.mentor;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base">{t("dashboard.escalations")}</CardTitle>
        <Link href="/escalations">
          <Button variant="ghost" size="sm" className="gap-1 text-xs">
            <ExternalLink className="size-3" />
            {t("common.viewAll")}
          </Button>
        </Link>
      </CardHeader>
      <CardContent className="space-y-3">
        {total === 0 ? (
          <div className="flex flex-col items-center justify-center py-4 text-center">
            <div className="bg-muted mb-2 flex size-10 items-center justify-center rounded-full">
              <AlertTriangle className="text-muted-foreground size-5" />
            </div>
            <p className="text-muted-foreground text-sm">{t("escalations.noEscalations")}</p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between rounded-xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-800/30 dark:bg-red-950/30">
              <div className="flex items-center gap-2">
                <AlertTriangle className="size-4 text-red-500" />
                <span className="text-sm font-medium text-red-700 dark:text-red-400">
                  {t("dashboard.toHr")}
                </span>
              </div>
              <span className="text-lg font-bold text-red-700 dark:text-red-400">
                {escalations.hr}
              </span>
            </div>

            <div className="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-800/30 dark:bg-amber-950/30">
              <div className="flex items-center gap-2">
                <Users className="size-4 text-amber-600" />
                <span className="text-sm font-medium text-amber-700 dark:text-amber-400">
                  {t("dashboard.toMentor")}
                </span>
              </div>
              <span className="text-lg font-bold text-amber-700 dark:text-amber-400">
                {escalations.mentor}
              </span>
            </div>

            <div className="flex items-center justify-between rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 dark:border-blue-800/30 dark:bg-blue-950/30">
              <div className="flex items-center gap-2">
                <Activity className="size-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-700 dark:text-blue-400">
                  {t("dashboard.inWork")}
                </span>
              </div>
              <span className="text-lg font-bold text-blue-700 dark:text-blue-400">
                {escalations.inProgress}
              </span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
