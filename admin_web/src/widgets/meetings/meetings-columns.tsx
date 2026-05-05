import type { ColumnDef } from "@/shared/entity/entity-page-types";
import { formatDate } from "@/shared/lib/utils";
import {
  Calendar,
  Clock,
  Users,
  UserPlus,
  ShieldCheck,
  Shield,
  Briefcase,
  HelpCircle,
  User2,
} from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import type { MeetingItem } from "@/shared/hooks/use-meetings";
import { cn } from "@/shared/lib/utils";

const MEETING_TYPE_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  HR: {
    label: "HR",
    icon: <Users className="size-3.5" />,
    color: "bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300",
  },
  SECURITY: {
    label: "Security",
    icon: <ShieldCheck className="size-3.5" />,
    color: "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300",
  },
  TEAM: {
    label: "Team",
    icon: <Users className="size-3.5" />,
    color: "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
  },
  MANAGER: {
    label: "Manager",
    icon: <Briefcase className="size-3.5" />,
    color: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
  },
  OTHER: {
    label: "Other",
    icon: <HelpCircle className="size-3.5" />,
    color: "bg-muted text-muted-foreground",
  },
};

interface MeetingsColumnsProps {
  departments: { id: number; name: string }[];
  onOpenAssignDialog: (meetingId: number, title: string) => void;
  onOpenAssignmentsDialog: (meetingId: number, title: string) => void;
  t: (key: string) => string;
}

export function useMeetingsColumns({ departments, onOpenAssignDialog, onOpenAssignmentsDialog, t }: MeetingsColumnsProps) {
  return [
    {
      key: "title",
      header: t("meetings.name"),
      cell: (item: MeetingItem) => (
        <div className="flex items-start gap-3">
          <div className="bg-muted flex size-8 shrink-0 items-center justify-center rounded-lg">
            <User2 className="text-muted-foreground size-4" />
          </div>
          <div className="min-w-0">
            <p className="font-medium leading-none">{item.title}</p>
            {item.description && (
              <p className="text-muted-foreground mt-0.5 line-clamp-1 max-w-56 text-xs">{item.description}</p>
            )}
          </div>
        </div>
      ),
      sortable: true,
    },
    {
      key: "type",
      header: t("meetings.type"),
      cell: (item: MeetingItem) => {
        const cfg = MEETING_TYPE_CONFIG[item.type] ?? MEETING_TYPE_CONFIG.OTHER;
        return (
          <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", cfg.color)}>
            {cfg.icon}
            {cfg.label}
          </span>
        );
      },
      sortable: true,
    },
    {
      key: "department",
      header: t("meetings.department"),
      cell: (item: MeetingItem) => {
        const name = item.department || departments.find((dept) => dept.id === item.departmentId)?.name;
        return name ? (
          <span className="text-sm">{name}</span>
        ) : (
          <span className="text-muted-foreground text-sm">—</span>
        );
      },
      sortable: true,
    },
    {
      key: "deadlineDays",
      header: t("meetings.deadlineDays"),
      cell: (item: MeetingItem) => (
        <div className="flex items-center gap-1.5 text-sm">
          <Calendar className="text-muted-foreground size-3.5" />
          <span>{item.deadlineDays} {t("common.days")}</span>
        </div>
      ),
      sortable: true,
    },
    {
      key: "durationMinutes",
      header: t("meetings.durationMinutes"),
      cell: (item: MeetingItem) => (
        <div className="flex items-center gap-1.5 text-sm">
          <Clock className="text-muted-foreground size-3.5" />
          <span>{item.durationMinutes} {t("common.minutes")}</span>
        </div>
      ),
      sortable: true,
      width: "w-32",
    },
    {
      key: "isMandatory",
      header: t("meetings.isMandatory"),
      cell: (item: MeetingItem) =>
        item.isMandatory ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
            <Shield className="size-3" />
            {t("common.yes")}
          </span>
        ) : (
          <span className="text-muted-foreground text-xs">{t("common.no")}</span>
        ),
      sortable: true,
    },
    {
      key: "order",
      header: t("meetings.order"),
      cell: (item: MeetingItem) => (
        <span className="text-muted-foreground rounded bg-muted px-1.5 py-0.5 text-xs font-mono">
          #{item.order}
        </span>
      ),
      sortable: true,
      width: "w-20",
    },
    {
      key: "createdAt",
      header: t("common.created"),
      cell: (item: MeetingItem) => (
        <span className="text-muted-foreground text-sm">{formatDate(item.createdAt)}</span>
      ),
      sortable: true,
      width: "w-32",
    },
    {
      key: "assignments",
      header: "",
      cell: (item: MeetingItem) => (
        <TooltipProvider>
          <div className="flex gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-8"
                  onClick={() => onOpenAssignmentsDialog(item.id, item.title)}
                >
                  <Users className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{t("meetings.assignedUsers")}</p>
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-8"
                  onClick={() => onOpenAssignDialog(item.id, item.title)}
                >
                  <UserPlus className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{t("meetings.assignMeeting")}</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </TooltipProvider>
      ),
      width: "w-24",
    },
  ];
}
