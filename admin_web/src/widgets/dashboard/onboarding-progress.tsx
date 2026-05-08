import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";
import type { OnboardingProgress as OnboardingProgressType } from "@/shared/types";

interface OnboardingProgressProps {
  progress: OnboardingProgressType[];
  href?: string;
}

export function OnboardingProgress({ progress, href }: OnboardingProgressProps) {
  const t = useTranslations();

  const card = (
    <Card className="col-span-1 md:col-span-2 lg:col-span-4 transition-shadow hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle>{t("dashboard.onboardingProgress")}</CardTitle>
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
        <div className="space-y-4">
          {progress.length > 0 ? (
            progress.map((item, index) => (
              <div key={`${item.user_id}-${index}`} className="flex items-center gap-4">
                <div className="min-w-0 flex-1">
                  <div className="mb-1 flex items-center justify-between">
                    <p className="truncate text-sm font-medium">{item.user_name}</p>
                    <p className="text-muted-foreground text-xs">{item.completion_percentage}%</p>
                  </div>
                  <div className="bg-muted h-2 w-full rounded-full">
                    <div
                      className={`h-2 rounded-full ${
                        item.completion_percentage >= 80
                          ? "bg-green-500 dark:bg-green-600"
                          : item.completion_percentage >= 50
                            ? "bg-yellow-500 dark:bg-yellow-600"
                            : "bg-red-500 dark:bg-red-600"
                      }`}
                      style={{ width: `${item.completion_percentage}%` }}
                    />
                  </div>
                </div>
                 <span className="text-muted-foreground shrink-0 text-xs">
                   {item.status === "COMPLETED"
                     ? t("common.completed")
                     : item.days_remaining > 0
                       ? `${item.days_remaining} ${t("dashboard.daysRemaining")}`
                       : `${Math.abs(item.days_remaining)} ${t("dashboard.daysOverdue")}`}
                 </span>
              </div>
            ))
          ) : (
            <p className="text-muted-foreground py-4 text-center text-sm">{t("common.noData")}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return card;
}
