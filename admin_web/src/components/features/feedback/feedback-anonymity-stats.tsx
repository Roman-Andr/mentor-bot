import { Shield } from "lucide-react";
import { useTranslations } from "@/hooks/use-translations";
import { useFeedback } from "@/hooks/use-feedback";

export function FeedbackAnonymityStats() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border rounded-xl p-6 mb-8">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-muted-foreground" />
        <h3 className="font-semibold">{t("feedback.anonymityStats")}</h3>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-background border rounded-lg p-4">
          <div className="text-sm text-muted-foreground mb-2">{t("feedback.pulseSurveysAnon")}</div>
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold text-primary">
              {f.pulseAnonymityStats?.anonymous?.count || 0}
            </div>
            <div className="h-8 w-px bg-border" />
            <div>
              <div className="text-sm text-muted-foreground">
                {f.pulseAnonymityStats?.attributed?.count || 0}
              </div>
              <div className="text-xs text-muted-foreground">{t("feedback.attributed")}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
