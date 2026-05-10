import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

interface CompletionRateCardProps {
  stats: {
    average_completion_days: number;
    overdue_tasks: number;
    pending_tasks: number;
  };
  href?: string;
}

export function CompletionRateCard({ stats, href }: CompletionRateCardProps) {
  const t = useTranslations();

  const card = (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base">{t("dashboard.completionRate")}</CardTitle>
        {href && (
          <Link href={href}>
            <Button variant="ghost" size="sm" className="gap-1 text-xs">
              <ExternalLink className="size-3" />
              <span className="hidden sm:inline">{t("common.viewAll")}</span>
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-4">
          <div className="relative flex size-24 items-center justify-center">
            <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                className="text-muted opacity-20"
              />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={`${2 * Math.PI * 42}`}
                strokeDashoffset={`${2 * Math.PI * 42 * (1 - Math.min(stats.average_completion_days / 90, 1))}`}
                className="text-blue-500"
                strokeLinecap="round"
              />
            </svg>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats?.average_completion_days || 0}
              </div>
              <div className="text-xs text-muted-foreground">{t("dashboard.days")}</div>
            </div>
          </div>
          <p className="mt-3 text-center text-sm text-muted-foreground">
            {t("dashboard.daysAverage")}
          </p>
        </div>
        <div className="mt-2 space-y-2 border-t pt-3">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">{t("analytics.overdue")}</span>
            <span className="font-medium text-red-500">{stats.overdue_tasks}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">{t("dashboard.notStarted")}</span>
            <span className="font-medium text-muted-foreground">{stats.pending_tasks}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return card;
}
