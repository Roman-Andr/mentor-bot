import { Shield, UserX } from "lucide-react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useFeedback } from "@/shared/hooks/use-feedback";
import { cn } from "@/shared/lib/utils";

function AnonStatCard({
  title,
  anonCount,
  attributedCount,
  className,
}: {
  title: string;
  anonCount: number;
  attributedCount: number;
  className?: string;
}) {
  const t = useTranslations();
  const total = anonCount + attributedCount;
  const anonPct = total > 0 ? Math.round((anonCount / total) * 100) : 0;

  return (
    <div className={cn("rounded-xl border bg-card p-4", className)}>
      <div className="mb-3 flex items-center gap-2">
        <Shield className="text-muted-foreground size-4" />
        <p className="text-sm font-medium">{title}</p>
      </div>
      <div className="flex items-end gap-3">
        <div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold">{anonCount}</span>
            <span className="text-muted-foreground text-sm">{t("feedback.anonymous")}</span>
          </div>
          <div className="text-muted-foreground text-xs">{attributedCount} {t("feedback.attributed")}</div>
        </div>
        <div className="flex-1">
          <div className="bg-muted mb-1 h-2 overflow-hidden rounded-full">
            <div
              className="h-full rounded-full bg-amber-400 transition-all"
              style={{ width: `${anonPct}%` }}
            />
          </div>
          <p className="text-muted-foreground text-right text-xs">{anonPct}% {t("feedback.anonymous")}</p>
        </div>
      </div>
    </div>
  );
}

export function FeedbackAnonymityStats() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <AnonStatCard
        title={t("feedback.pulseSurveysAnon")}
        anonCount={f.pulseAnonymityStats?.anonymous?.count || 0}
        attributedCount={f.pulseAnonymityStats?.attributed?.count || 0}
      />
      <AnonStatCard
        title={t("feedback.experienceRatingsAnon")}
        anonCount={f.experienceAnonymityStats?.anonymous?.count || 0}
        attributedCount={f.experienceAnonymityStats?.attributed?.count || 0}
      />
      <AnonStatCard
        title={t("feedback.commentsAnon")}
        anonCount={f.commentAnonymityStats?.anonymous?.count || 0}
        attributedCount={f.commentAnonymityStats?.attributed?.count || 0}
      />
    </div>
  );
}
