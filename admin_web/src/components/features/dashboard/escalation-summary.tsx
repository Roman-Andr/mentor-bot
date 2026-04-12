import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("dashboard.escalations")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-red-50 p-3">
            <span className="text-sm text-red-700">{t("dashboard.toHr")}</span>
            <span className="font-bold text-red-700">{escalations.hr}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-yellow-50 p-3">
            <span className="text-sm text-yellow-700">{t("dashboard.toMentor")}</span>
            <span className="font-bold text-yellow-700">{escalations.mentor}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-blue-50 p-3">
            <span className="text-sm text-blue-700">{t("dashboard.inWork")}</span>
            <span className="font-bold text-blue-700">{escalations.inProgress}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
