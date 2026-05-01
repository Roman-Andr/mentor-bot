
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { RefreshCw, XCircle, Copy, Check } from "lucide-react";
import { ROLES, INVITATION_STATUSES } from "@/lib/constants";
import type { InvitationItem } from "@/hooks/use-invitations";

interface InvitationsColumnsProps {
  copiedId: number | null;
  onCopy: (url: string, id: number) => void;
  onResend: (id: number) => void;
  onRevoke: (id: number) => void;
  t: (key: string) => string;
}

export function useInvitationsColumns({ copiedId, onCopy, onResend, onRevoke, t }: InvitationsColumnsProps) {
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
      cell: (item: InvitationItem) => ROLES.find((r) => r.value === item.role)?.label || item.role,
      sortable: true,
    },
    {
      key: "department",
      header: t("common.department"),
      cell: (item: InvitationItem) => item.department || "—",
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
      cell: (item: InvitationItem) => new Date(item.createdAt).toLocaleDateString(),
      sortable: true,
    },
    {
      key: "expiresAt",
      header: t("invitations.expiresAt"),
      cell: (item: InvitationItem) => new Date(item.expiresAt).toLocaleDateString(),
      sortable: true,
    },
    {
      key: "actions",
      header: "",
      cell: (item: InvitationItem) => (
        <TooltipProvider>
          <div className="flex gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground"
                  onClick={() => onCopy(item.invitationUrl, item.id)}
                >
                  {copiedId === item.id ? (
                    <Check className="size-4 text-green-600" />
                  ) : (
                    <Copy className="size-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{t("invitations.copyLink")}</p>
              </TooltipContent>
            </Tooltip>
            {item.status === "PENDING" && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-blue-500"
                    onClick={() => onResend(item.id)}
                  >
                    <RefreshCw className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t("invitations.resend")}</p>
                </TooltipContent>
              </Tooltip>
            )}
            {item.status === "PENDING" && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-orange-500"
                    onClick={() => onRevoke(item.id)}
                  >
                    <XCircle className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t("invitations.revoke")}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
        </TooltipProvider>
      ),
      width: "w-40",
    },
  ];
}
