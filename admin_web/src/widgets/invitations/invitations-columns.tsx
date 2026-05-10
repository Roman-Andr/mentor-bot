import { StatusBadge } from "@/shared/ui/status-badge";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import { RefreshCw, XCircle, Copy, Check, AlertCircle } from "lucide-react";
import { ROLES } from "@/shared/lib/constants";
import type { InvitationItem } from "@/shared/hooks/use-invitations";
import { cn } from "@/shared/lib/utils";

interface InvitationsColumnsProps {
  copiedId: number | null;
  onCopy: (url: string, id: number) => void;
  onResend: (id: number) => void;
  onRevoke: (id: number) => void;
  t: (key: string) => string;
}

function ExpiryCell({ expiresAt, status }: { expiresAt: string; status: string }) {
  const expDate = new Date(expiresAt);
  const now = new Date();
  const daysLeft = Math.ceil((expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  const isExpired = daysLeft <= 0 || status === "EXPIRED";
  const isUrgent = daysLeft > 0 && daysLeft <= 7;

  return (
    <div className="flex items-center gap-1.5">
      {isExpired ? (
        <span className="text-sm text-muted-foreground">{expDate.toLocaleDateString()}</span>
      ) : isUrgent ? (
        <>
          <AlertCircle className="size-3.5 text-red-500" />
          <span className="text-sm font-medium text-red-600 dark:text-red-400">
            {expDate.toLocaleDateString()}
          </span>
          <span className="rounded-full bg-red-100 px-1.5 py-0.5 text-xs text-red-600 dark:bg-red-950 dark:text-red-400">
            {daysLeft}d
          </span>
        </>
      ) : (
        <span className="text-sm">{expDate.toLocaleDateString()}</span>
      )}
    </div>
  );
}

export function useInvitationsColumns({
  copiedId,
  onCopy,
  onResend,
  onRevoke,
  t,
}: InvitationsColumnsProps) {
  return [
    {
      key: "email",
      header: t("invitations.email"),
      cell: (item: InvitationItem) => <span className="font-medium">{item.email}</span>,
      sortable: true,
    },
    {
      key: "role",
      header: t("invitations.role"),
      cell: (item: InvitationItem) => {
        const role = ROLES.find((r) => r.value === item.role);
        return (
          <span className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
            {role?.label || item.role}
          </span>
        );
      },
      sortable: true,
    },
    {
      key: "department",
      header: t("common.department"),
      cell: (item: InvitationItem) => <span className="text-sm">{item.department || "—"}</span>,
      sortable: true,
    },
    {
      key: "status",
      header: t("common.status"),
      cell: (item: InvitationItem) => <StatusBadge status={item.status} />,
      sortable: true,
    },
    {
      key: "createdAt",
      header: t("invitations.createdAt"),
      cell: (item: InvitationItem) => (
        <span className="text-sm">{new Date(item.createdAt).toLocaleDateString()}</span>
      ),
      sortable: true,
    },
    {
      key: "expiresAt",
      header: t("invitations.expiresAt"),
      cell: (item: InvitationItem) => (
        <ExpiryCell expiresAt={item.expiresAt} status={item.status} />
      ),
      sortable: true,
    },
    {
      key: "actions",
      header: "",
      cell: (item: InvitationItem) => (
        <TooltipProvider>
          <div className="flex items-center gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    "size-8",
                    copiedId === item.id ? "text-green-600" : "text-muted-foreground",
                  )}
                  onClick={() => onCopy(item.invitationUrl, item.id)}
                >
                  {copiedId === item.id ? (
                    <Check className="size-4" />
                  ) : (
                    <Copy className="size-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{copiedId === item.id ? t("common.copied") : t("invitations.copyLink")}</p>
              </TooltipContent>
            </Tooltip>
            {item.status === "PENDING" && (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8 text-blue-500 hover:text-blue-600"
                      onClick={() => onResend(item.id)}
                    >
                      <RefreshCw className="size-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t("invitations.resend")}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8 text-orange-500 hover:text-orange-600"
                      onClick={() => onRevoke(item.id)}
                    >
                      <XCircle className="size-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t("invitations.revoke")}</p>
                  </TooltipContent>
                </Tooltip>
              </>
            )}
          </div>
        </TooltipProvider>
      ),
      width: "w-36",
    },
  ];
}
