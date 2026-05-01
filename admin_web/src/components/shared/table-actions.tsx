import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
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
  const visibleActions = actions.filter((a) => a && a.show !== false);

  // Grid with fixed positions: Edit | Middle | Delete
  const editAction = visibleActions.find(a => a.icon === SquarePen);
  const deleteAction = visibleActions.find(a => a.icon === Trash2);
  const middleActions = visibleActions.filter(a => a.icon !== SquarePen && a.icon !== Trash2);

  return (
    <TooltipProvider>
      <div className="grid grid-cols-3 gap-1 w-24">
        <div className="justify-self-start">
          {editAction && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={editAction.variant || "ghost"}
                  size="icon"
                  onClick={editAction.onClick}
                  className={`${editAction.color ? editAction.color : "text-muted-foreground"} cursor-pointer`}
                >
                  <editAction.icon className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{editAction.label}</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
        <div className="justify-self-center">
          {middleActions.map((action, index) => (
            <Tooltip key={index}>
              <TooltipTrigger asChild>
                <Button
                  variant={action.variant || "ghost"}
                  size="icon"
                  onClick={action.onClick}
                  className={`${action.color ? action.color : "text-muted-foreground"} cursor-pointer`}
                >
                  <action.icon className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{action.label}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
        <div className="justify-self-end">
          {deleteAction && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={deleteAction.variant || "ghost"}
                  size="icon"
                  onClick={deleteAction.onClick}
                  className={`${deleteAction.color ? deleteAction.color : "text-muted-foreground"} cursor-pointer`}
                >
                  <deleteAction.icon className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{deleteAction.label}</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
}

// Predefined action builders
export const buildEditAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: SquarePen,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildDeleteAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: Trash2,
  label,
  onClick,
  variant: "ghost",
  color: "text-red-500",
  show,
});

export const buildToggleAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: Power,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildCompleteAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: CheckCircle,
  label,
  onClick,
  variant: "ghost",
  color: "text-green-500",
  show,
});

export const buildResendAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: RefreshCw,
  label,
  onClick,
  variant: "ghost",
  color: "text-blue-500",
  show,
});

export const buildRevokeAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: XCircle,
  label,
  onClick,
  variant: "ghost",
  color: "text-orange-500",
  show,
});

export const buildCopyAction = (onClick: () => void, label: string, show = true, isCopied = false): ActionDefinition => ({
  icon: isCopied ? Check : Copy,
  label,
  onClick,
  variant: "ghost",
  color: isCopied ? "text-green-600" : "text-muted-foreground",
  show,
});

export const buildViewAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: Eye,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildReplyAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: MessageSquare,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildViewUsersAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: Users,
  label,
  onClick,
  variant: "ghost",
  show,
});

export const buildAssignAction = (onClick: () => void, label: string, show = true): ActionDefinition => ({
  icon: UserPlus,
  label,
  onClick,
  variant: "ghost",
  show,
});
