import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Mail, UserPlus, RefreshCw } from "lucide-react";
import Link from "next/link";

interface DashboardHeaderProps {
  t: (key: string) => string;
  onRefresh?: () => void;
}

export function DashboardHeader({ t, onRefresh }: DashboardHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-2">
        <div>
          <h1 className="text-foreground text-2xl font-bold tracking-tight">{t("dashboard.title")}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">{t("dashboard.welcome")}</p>
        </div>
        {onRefresh && (
          <Button variant="ghost" size="icon" onClick={onRefresh} title={t("common.refresh")}>
            <RefreshCw className="size-4" />
          </Button>
        )}
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <Link href="/invitations">
          <Button variant="outline" size="sm" className="gap-2 w-full sm:w-auto">
            <Mail className="size-4" />
            {t("invitations.sendInvitation")}
          </Button>
        </Link>
        <Link href="/users">
          <Button size="sm" className="gap-2 w-full sm:w-auto">
            <UserPlus className="size-4" />
            {t("users.addUser")}
          </Button>
        </Link>
      </div>
    </div>
  );
}
