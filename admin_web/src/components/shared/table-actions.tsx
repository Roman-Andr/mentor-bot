import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  SquarePen,
  Trash2,
  Power,
  CheckCircle,
  RefreshCw,
  Ban,
  Copy,
  Check,
  Eye,
  MessageSquare,
  Users,
  UserPlus,
  UserCheck,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type ActionType =
  | "view"
  | "viewUsers"
  | "reply"
  | "edit"
  | "assign"
  | "assignMentor"
  | "publish"
  | "complete"
  | "toggle"
  | "resend"
  | "copy"
  | "revoke"
  | "delete";

const ACTION_ORDER: ActionType[] = [
  "view",
  "viewUsers",
  "reply",
  "edit",
  "assign",
  "assignMentor",
  "publish",
  "complete",
  "toggle",
  "resend",
  "copy",
  "revoke",
  "delete",
];

export interface ActionDefinition {
  type: ActionType;
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
  const sorted = [...actions]
    .filter(Boolean)
    .sort((a, b) => ACTION_ORDER.indexOf(a.type) - ACTION_ORDER.indexOf(b.type));

  return (
    <TooltipProvider>
      <div className="flex items-center justify-end gap-1">
        {sorted.map((action) => (
          <div key={action.type} className="flex size-9 items-center justify-center">
            {action.show !== false && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={action.variant || "ghost"}
                    size="icon"
                    onClick={action.onClick}
                    aria-label={action.label}
                    className={`${action.color ? action.color : "text-muted-foreground"} cursor-pointer`}
                  >
                    <action.icon className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{action.label}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
        ))}
      </div>
    </TooltipProvider>
  );
}

// Predefined action builders
export const buildEditAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "edit",
  icon: SquarePen,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildDeleteAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "delete",
  icon: Trash2,
  label,
  onClick,
  variant: "ghost",
  color: "text-red-500",
  show,
});

export const buildToggleAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "toggle",
  icon: Power,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildCompleteAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "complete",
  icon: CheckCircle,
  label,
  onClick,
  variant: "ghost",
  color: "text-green-500",
  show,
});

export const buildResendAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "resend",
  icon: RefreshCw,
  label,
  onClick,
  variant: "ghost",
  color: "text-blue-500",
  show,
});

export const buildRevokeAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "revoke",
  icon: Ban,
  label,
  onClick,
  variant: "ghost",
  color: "text-orange-500",
  show,
});

export const buildCopyAction = (onClick: () => void, label: string, show = true, isCopied = false): ActionDefinition => ({
  type: "copy",
  icon: isCopied ? Check : Copy,
  label,
  onClick,
  variant: "ghost",
  color: isCopied ? "text-green-600" : "text-muted-foreground",
  show,
});

export const buildViewAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "view",
  icon: Eye,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildReplyAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "reply",
  icon: MessageSquare,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildViewUsersAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "viewUsers",
  icon: Users,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildAssignAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "assign",
  icon: UserPlus,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildAssignMentorAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  type: "assignMentor",
  icon: UserCheck,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildPublishAction = (
  onClick: () => void,
  label: string,
  show = true,
  icon: LucideIcon = CheckCircle,
): ActionDefinition => ({
  type: "publish",
  icon,
  label,
  onClick,
  variant: "ghost",
  color: "text-green-500",
  show,
});
