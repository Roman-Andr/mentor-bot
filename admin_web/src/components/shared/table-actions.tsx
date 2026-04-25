import { Button } from "@/components/ui/button";
import { SquarePen, Trash2, Power, CheckCircle, RefreshCw, XCircle, Copy, Check, Eye, MessageSquare, Users, UserPlus } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface ActionDefinition {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
  variant?: "ghost" | "outline" | "default";
  color?: string;
  show?: boolean;
}

interface TableActionsProps {
  actions: ActionDefinition[];
}

export function TableActions({ actions }: TableActionsProps) {
  return (
    <div className="flex gap-1">
      {actions.filter((a) => a.show !== false).map((action, index) => (
        <Button
          key={index}
          variant={action.variant || "ghost"}
          size="icon"
          onClick={action.onClick}
          title={action.label}
          className={action.color ? action.color : "text-muted-foreground"}
        >
          <action.icon className="size-4" />
        </Button>
      ))}
    </div>
  );
}

// Predefined action builders
export const buildEditAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: SquarePen,
  label: "Edit",
  onClick,
  variant: "ghost",
  show,
});

export const buildDeleteAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: Trash2,
  label: "Delete",
  onClick,
  variant: "ghost",
  color: "text-red-500",
  show,
});

export const buildToggleAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: Power,
  label: "Toggle",
  onClick,
  variant: "ghost",
  show,
});

export const buildCompleteAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: CheckCircle,
  label: "Complete",
  onClick,
  variant: "ghost",
  color: "text-green-500",
  show,
});

export const buildResendAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: RefreshCw,
  label: "Resend",
  onClick,
  variant: "ghost",
  color: "text-blue-500",
  show,
});

export const buildRevokeAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: XCircle,
  label: "Revoke",
  onClick,
  variant: "ghost",
  color: "text-orange-500",
  show,
});

export const buildCopyAction = (onClick: () => void, show = true, isCopied = false): ActionDefinition => ({
  icon: isCopied ? Check : Copy,
  label: "Copy",
  onClick,
  variant: "ghost",
  color: isCopied ? "text-green-600" : "text-muted-foreground",
  show,
});

export const buildViewAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: Eye,
  label: "View",
  onClick,
  variant: "ghost",
  show,
});

export const buildReplyAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: MessageSquare,
  label: "Reply",
  onClick,
  variant: "ghost",
  show,
});

export const buildViewUsersAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: Users,
  label: "View Users",
  onClick,
  variant: "ghost",
  show,
});

export const buildAssignAction = (onClick: () => void, show = true): ActionDefinition => ({
  icon: UserPlus,
  label: "Assign",
  onClick,
  variant: "ghost",
  show,
});
