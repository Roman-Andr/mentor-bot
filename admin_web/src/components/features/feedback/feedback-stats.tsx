import { TrendingUp, Star, MessageCircle } from "lucide-react";
import { StatCard } from "./stat-card";
import { useTranslations } from "@/hooks/use-translations";
import { useFeedback } from "@/hooks/use-feedback";

export function FeedbackStats() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <StatCard
        title={t("feedback.pulseSurveys")}
        value={f.pulseStats?.total_responses || 0}
        subtitle={`${t("feedback.avgRating")}: ${f.pulseStats?.average_rating?.toFixed(1) || "-"}/10`}
        icon={TrendingUp}
        color="blue"
      />
      <StatCard
        title={t("feedback.experienceRatings")}
        value={f.experienceStats?.total_ratings || 0}
        subtitle={`${t("feedback.avgRating")}: ${f.experienceStats?.average_rating?.toFixed(1) || "-"}/5`}
        icon={Star}
        color="green"
      />
      <StatCard
        title={t("feedback.comments")}
        value={f.totalComments}
        subtitle={`${f.commentsWithReply} ${t("feedback.withReply")}`}
        icon={MessageCircle}
        color="purple"
      />
    </div>
  );
}
