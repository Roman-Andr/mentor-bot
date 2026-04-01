import { useTranslations } from "next-intl";
import { StatsGrid } from "@/components/ui/stat-card";
import { Mail, CheckCircle, Clock, XCircle } from "lucide-react";

interface InvitationStatsProps {
  stats: {
    total: number;
    pending: number;
    accepted: number;
    expired: number;
  };
}

export function InvitationStats({ stats }: InvitationStatsProps) {
  const t = useTranslations("invitations");

  return (
    <StatsGrid
      stats={[
        { label: t("totalInvitations") || "Total Invitations", value: stats.total, icon: Mail },
        { label: t("pendingCount") || "Pending", value: stats.pending, icon: Clock },
        { label: t("acceptedCount") || "Accepted", value: stats.accepted, icon: CheckCircle },
        { label: t("expiredCount") || "Expired", value: stats.expired, icon: XCircle },
      ]}
    />
  );
}
