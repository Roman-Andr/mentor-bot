/* eslint-disable @typescript-eslint/no-explicit-any */
import { MEETING_TYPES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { Calendar, Clock, Users, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { MeetingItem } from "@/hooks/use-meetings";

interface MeetingsColumnsProps {
  departments: any[];
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
        <div>
          <p className="font-medium">{item.title}</p>
          {item.description && (
            <p className="text-muted-foreground line-clamp-1 max-w-64 text-sm">
              {item.description}
            </p>
          )}
        </div>
      ),
      sortable: true,
    },
    {
      key: "type",
      header: t("meetings.type"),
      cell: (item: MeetingItem) => MEETING_TYPES.find((type) => type.value === item.type)?.label || item.type,
      sortable: true,
    },
    {
      key: "department",
      header: t("meetings.department"),
      cell: (item: MeetingItem) =>
        item.department || departments.find((dept) => dept.id === item.departmentId)?.name || "—",
      sortable: true,
    },
    {
      key: "deadlineDays",
      header: t("meetings.deadlineDays"),
      cell: (item: MeetingItem) => (
        <div className="flex items-center gap-1">
          <Calendar className="text-muted-foreground size-4" />
          {item.deadlineDays} {t("common.days")}
        </div>
      ),
      sortable: true,
    },
    {
      key: "durationMinutes",
      header: t("meetings.durationMinutes"),
      cell: (item: MeetingItem) => (
        <div className="flex items-center gap-1">
          <Clock className="text-muted-foreground size-4" />
          {item.durationMinutes} {t("common.minutes")}
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
          <span className="text-green-600">{t("common.yes")}</span>
        ) : (
          <span className="text-muted-foreground">{t("common.no")}</span>
        ),
      sortable: true,
    },
    {
      key: "order",
      header: t("meetings.order"),
      cell: (item: MeetingItem) => item.order,
      sortable: true,
      width: "w-24",
    },
    {
      key: "createdAt",
      header: t("common.created"),
      cell: (item: MeetingItem) => formatDate(item.createdAt),
      sortable: true,
      width: "w-32",
    },
    {
      key: "assignments",
      header: "",
      cell: (item: MeetingItem) => (
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            title={t("meetings.assignedUsers")}
            onClick={() => onOpenAssignmentsDialog(item.id, item.title)}
          >
            <Users className="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title={t("meetings.assignMeeting")}
            onClick={() => onOpenAssignDialog(item.id, item.title)}
          >
            <UserPlus className="size-4" />
          </Button>
        </div>
      ),
      width: "w-24",
    },
  ];
}
