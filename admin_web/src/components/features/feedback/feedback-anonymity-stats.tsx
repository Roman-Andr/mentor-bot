import { Shield } from "lucide-react";
import { useTranslations } from "@/hooks/use-translations";
import { useFeedback } from "@/hooks/use-feedback";

export function FeedbackAnonymityStats() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <div className="mb-8 rounded-xl border bg-gradient-to-br from-slate-50 to-slate-100 p-6 dark:from-slate-900 dark:to-slate-800">
      <div className="mb-4 flex items-center gap-2">
        <Shield className="text-muted-foreground h-5 w-5" />
        <h3 className="font-semibold">{t("feedback.anonymityStats")}</h3>
      </div>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="bg-background rounded-lg border p-4">
          <div className="text-muted-foreground mb-2 text-sm">{t("feedback.pulseSurveysAnon")}</div>
          <div className="flex items-center gap-3">
            <div className="text-primary text-2xl font-bold">
              {f.pulseAnonymityStats?.anonymous?.count || 0}
            </div>
            <div className="bg-border h-8 w-px" />
            <div>
              <div className="text-muted-foreground text-sm">
                {f.pulseAnonymityStats?.attributed?.count || 0}
              </div>
              <div className="text-muted-foreground text-xs">{t("feedback.attributed")}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
