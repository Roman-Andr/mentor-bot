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
  return (
    <StatsGrid
      stats={[
        { label: "Всего приглашений", value: stats.total, icon: Mail },
        { label: "Ожидают", value: stats.pending, icon: Clock },
        { label: "Принято", value: stats.accepted, icon: CheckCircle },
        { label: "Истекло", value: stats.expired, icon: XCircle },
      ]}
    />
  );
}
