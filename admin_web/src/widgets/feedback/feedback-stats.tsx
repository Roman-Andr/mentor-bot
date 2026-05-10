import { TrendingUp, Star, MessageCircle, Activity } from "lucide-react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useFeedback } from "@/shared/hooks/use-feedback";
import { cn } from "@/shared/lib/utils";

interface FeedbackStatCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ElementType;
  iconClass: string;
  gradientFrom: string;
  gradientTo: string;
  badge?: string;
}

function FeedbackStatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconClass,
  gradientFrom,
  gradientTo,
  badge,
}: FeedbackStatCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border bg-gradient-to-br p-6",
        gradientFrom,
        gradientTo,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="mt-2 text-3xl font-bold">{value}</p>
          <p className="mt-1 text-xs opacity-70">{subtitle}</p>
        </div>
        <div className={cn("rounded-xl p-3", iconClass)}>
          <Icon className="size-5" />
        </div>
      </div>
      {badge && (
        <div className="mt-3 flex items-center gap-1 text-xs opacity-70">
          <Activity className="size-3" />
          {badge}
        </div>
      )}
    </div>
  );
}

export function FeedbackStats() {
  const t = useTranslations();
  const f = useFeedback();

  const avgPulse = f.pulseStats?.average_rating;
  const avgExp = f.experienceStats?.average_rating;

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <FeedbackStatCard
        title={t("feedback.pulseSurveys")}
        value={f.pulseStats?.total_responses || 0}
        subtitle={`${t("feedback.avgRating")}: ${avgPulse?.toFixed(1) || "—"}/10`}
        icon={TrendingUp}
        iconClass="bg-blue-500/20 text-blue-500 dark:bg-blue-400/20 dark:text-blue-400"
        gradientFrom="from-blue-50 dark:from-blue-950/20"
        gradientTo="to-blue-100/50 dark:to-blue-900/10"
        badge={avgPulse ? `${t("feedback.avgRating")} ${avgPulse.toFixed(1)}/10` : undefined}
      />
      <FeedbackStatCard
        title={t("feedback.experienceRatings")}
        value={f.experienceStats?.total_ratings || 0}
        subtitle={`${t("feedback.avgRating")}: ${avgExp?.toFixed(1) || "—"}/5`}
        icon={Star}
        iconClass="bg-emerald-500/20 text-emerald-500 dark:bg-emerald-400/20 dark:text-emerald-400"
        gradientFrom="from-emerald-50 dark:from-emerald-950/20"
        gradientTo="to-emerald-100/50 dark:to-emerald-900/10"
        badge={avgExp ? `${t("feedback.avgRating")} ${avgExp.toFixed(1)}/5` : undefined}
      />
      <FeedbackStatCard
        title={t("feedback.comments")}
        value={f.totalComments}
        subtitle={`${f.commentsWithReply} ${t("feedback.withReply")}`}
        icon={MessageCircle}
        iconClass="bg-violet-500/20 text-violet-500 dark:bg-violet-400/20 dark:text-violet-400"
        gradientFrom="from-violet-50 dark:from-violet-950/20"
        gradientTo="to-violet-100/50 dark:to-violet-900/10"
      />
    </div>
  );
}
