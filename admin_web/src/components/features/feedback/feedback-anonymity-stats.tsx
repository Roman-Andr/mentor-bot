import { Shield, User, UserX } from "lucide-react";
import { StatCard } from "./stat-card";
import { useTranslations } from "@/hooks/use-translations";
import { useFeedback } from "@/hooks/use-feedback";

export function FeedbackAnonymityStats() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      <StatCard
        title={t("feedback.pulseSurveysAnon")}
        value={f.pulseAnonymityStats?.anonymous?.count || 0}
        subtitle={`${t("feedback.attributed")}: ${f.pulseAnonymityStats?.attributed?.count || 0}`}
        icon={UserX}
        color="orange"
      />
      <StatCard
        title={t("feedback.experienceRatingsAnon")}
        value={f.experienceAnonymityStats?.anonymous?.count || 0}
        subtitle={`${t("feedback.attributed")}: ${f.experienceAnonymityStats?.attributed?.count || 0}`}
        icon={Shield}
        color="blue"
      />
      <StatCard
        title={t("feedback.commentsAnon")}
        value={f.commentAnonymityStats?.anonymous?.count || 0}
        subtitle={`${t("feedback.attributed")}: ${f.commentAnonymityStats?.attributed?.count || 0}`}
        icon={User}
        color="purple"
      />
    </div>
  );
}
