/* eslint-disable @typescript-eslint/no-explicit-any */
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
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
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground"
            onClick={() => onCopy(item.invitationUrl, item.id)}
            title={t("invitations.copyLink")}
          >
            {copiedId === item.id ? (
              <Check className="size-4 text-green-600" />
            ) : (
              <Copy className="size-4" />
            )}
          </Button>
          {item.status === "PENDING" && (
            <Button
              variant="ghost"
              size="icon"
              className="text-blue-500"
              title={t("invitations.resend")}
              onClick={() => onResend(item.id)}
            >
              <RefreshCw className="size-4" />
            </Button>
          )}
          {item.status === "PENDING" && (
            <Button
              variant="ghost"
              size="icon"
              className="text-orange-500"
              title={t("invitations.revoke")}
              onClick={() => onRevoke(item.id)}
            >
              <XCircle className="size-4" />
            </Button>
          )}
        </div>
      ),
      width: "w-40",
    },
  ];
}
