import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent } from "@/shared/ui/card";
import { Mail, Check, Clock, XCircle, Ban } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface InvitationStatsProps {
  stats: {
    total: number;
    pending: number;
    accepted: number;
    expired: number;
    revoked?: number;
  };
}

interface StatCardProps {
  label: string;
  value: number;
  icon: React.ElementType;
  colorClass: string;
}

function StatItem({ label, value, icon: Icon, colorClass }: StatCardProps) {
  return (
    <Card className={cn("border transition-shadow hover:shadow-sm", colorClass)}>
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white/20">
          <Icon className="size-5" />
        </div>
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-sm opacity-80">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function InvitationStats({ stats }: InvitationStatsProps) {
  const t = useTranslations();

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatItem
        label={t("invitations.total") || "Total"}
        value={stats.total}
        icon={Mail}
        colorClass="bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200 text-blue-700 dark:from-blue-950/50 dark:to-blue-900/30 dark:border-blue-800 dark:text-blue-300"
      />
      <StatItem
        label={t("invitations.pending") || "Pending"}
        value={stats.pending}
        icon={Clock}
        colorClass="bg-gradient-to-br from-amber-50 to-amber-100/50 border-amber-200 text-amber-700 dark:from-amber-950/50 dark:to-amber-900/30 dark:border-amber-800 dark:text-amber-300"
      />
      <StatItem
        label={t("invitations.accepted") || "Accepted"}
        value={stats.accepted}
        icon={Check}
        colorClass="bg-gradient-to-br from-emerald-50 to-emerald-100/50 border-emerald-200 text-emerald-700 dark:from-emerald-950/50 dark:to-emerald-900/30 dark:border-emerald-800 dark:text-emerald-300"
      />
      <StatItem
        label={t("invitations.expired") || "Expired"}
        value={stats.expired + (stats.revoked ?? 0)}
        icon={stats.revoked ? Ban : XCircle}
        colorClass="bg-gradient-to-br from-red-50 to-red-100/50 border-red-200 text-red-700 dark:from-red-950/50 dark:to-red-900/30 dark:border-red-800 dark:text-red-300"
      />
    </div>
  );
}
