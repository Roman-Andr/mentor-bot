import { useTranslations } from "@/hooks/use-translations";
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
  const t = useTranslations();

  return (
    <StatsGrid
      stats={[
        { label: t("invitations.totalInvitations") || "Total Invitations", value: stats.total, icon: Mail },
        { label: t("invitations.pendingCount") || "Pending", value: stats.pending, icon: Clock },
        { label: t("invitations.acceptedCount") || "Accepted", value: stats.accepted, icon: CheckCircle },
        { label: t("invitations.expiredCount") || "Expired", value: stats.expired, icon: XCircle },
      ]}
    />
  );
}
