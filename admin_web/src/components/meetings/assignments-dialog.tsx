"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDate } from "@/lib/utils";
import { X } from "lucide-react";
import type { User, UserMeeting } from "@/types";
import { StatusBadge } from "@/components/ui/status-badge";

export interface AssignmentsDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  meetingTitle: string;
  assignments: UserMeeting[];
  assignmentsUsers: Record<number, User>;
  assignmentsLoading: boolean;
  onRemoveAssignment: (assignmentId: number) => Promise<void>;
}

export function AssignmentsDialog({
  isOpen,
  onOpenChange,
  meetingTitle,
  assignments,
  assignmentsUsers,
  assignmentsLoading,
  onRemoveAssignment,
}: AssignmentsDialogProps) {
  const t = useTranslations();

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("meetings.assignedUsers")}</DialogTitle>
          <DialogDescription>
            {t("meetings.usersAssignedTo", { title: meetingTitle })}
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          {assignmentsLoading ? (
            <p className="text-muted-foreground text-sm">{t("common.loading")}</p>
          ) : assignments.length === 0 ? (
            <p className="text-muted-foreground text-sm">{t("meetings.noAssignedUsers")}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("common.user")}</TableHead>
                  <TableHead>{t("common.status")}</TableHead>
                  <TableHead>{t("meetings.scheduledAt")}</TableHead>
                  <TableHead>{t("meetings.completedAt")}</TableHead>
                  <TableHead className="w-16">{t("common.actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignments.map((a) => {
                  const user = assignmentsUsers[a.user_id];
                  return (
                    <TableRow key={a.id}>
                      <TableCell>
                        {user ? (
                          <div>
                            <p className="font-medium">
                              {user.first_name} {user.last_name || ""}
                            </p>
                            <p className="text-muted-foreground text-xs">{user.email}</p>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">{t("common.user")} #{a.user_id}</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={a.status} />
                      </TableCell>
                      <TableCell>{a.scheduled_at ? formatDate(a.scheduled_at) : "-"}</TableCell>
                      <TableCell>{a.completed_at ? formatDate(a.completed_at) : "-"}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500"
                          onClick={() => onRemoveAssignment(a.id)}
                        >
                          <X className="size-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("common.close")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
