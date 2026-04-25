import { useTranslations } from "@/hooks/use-translations";
import { StatsGrid } from "@/components/ui/stat-card";
import { Mail, Check, Clock, XCircle } from "lucide-react";

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
        { label: t("invitations.total") || "Total", value: stats.total, icon: Mail },
        { label: t("invitations.pending") || "Pending", value: stats.pending, icon: Clock },
        { label: t("invitations.accepted") || "Accepted", value: stats.accepted, icon: Check },
        { label: t("invitations.expired") || "Expired", value: stats.expired, icon: XCircle },
      ]}
    />
  );
}
