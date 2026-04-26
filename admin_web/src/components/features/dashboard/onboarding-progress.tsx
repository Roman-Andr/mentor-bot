import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { OnboardingProgress as OnboardingProgressType } from "@/types";

interface OnboardingProgressProps {
  progress: OnboardingProgressType[];
}

export function OnboardingProgress({ progress }: OnboardingProgressProps) {
  const t = useTranslations();

  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>{t("dashboard.onboardingProgress")}</CardTitle>
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
                 <span className="text-muted-foreground inline-block w-[90px] truncate text-xs">
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
}
