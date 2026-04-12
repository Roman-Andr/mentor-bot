"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SearchInput } from "@/components/ui/search-input";
import { Dialog } from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Trash2, SquarePen, Calendar, UserPlus, Users } from "lucide-react";
import { MEETING_TYPES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { useMeetings } from "@/hooks/use-meetings";
import { useDepartments } from "@/hooks/use-departments";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { MeetingFormDialog } from "@/components/meetings/meeting-form-dialog";
import { AssignDialog, AssignmentsDialog } from "@/components/meetings";
import type { User, UserMeeting } from "@/types";

export default function MeetingsPage() {
  const t = useTranslations();
  const m = useMeetings();
  const d = useDepartments();
  const { toast } = useToast();

  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);
  const [assignMeetingId, setAssignMeetingId] = useState<number | null>(null);
  const [assignMeetingTitle, setAssignMeetingTitle] = useState("");

  const [isAssignmentsDialogOpen, setIsAssignmentsDialogOpen] = useState(false);
  const [assignmentsMeetingTitle, setAssignmentsMeetingTitle] = useState("");
  const [assignments, setAssignments] = useState<UserMeeting[]>([]);
  const [assignmentsUsers, setAssignmentsUsers] = useState<Record<number, User>>({});
  const [assignmentsLoading, setAssignmentsLoading] = useState(false);

  const openAssignDialog = (meetingId: number, title: string) => {
    setAssignMeetingId(meetingId);
    setAssignMeetingTitle(title);
    setIsAssignDialogOpen(true);
  };

  const openAssignmentsDialog = async (meetingId: number, title: string) => {
    setAssignmentsMeetingTitle(title);
    setIsAssignmentsDialogOpen(true);
    setAssignmentsLoading(true);
    try {
      const resp = await api.userMeetings.listByMeeting(meetingId, { limit: 100 });
      if (resp.data) {
        setAssignments(resp.data.items);
        const userIds = [...new Set(resp.data.items.map((a) => a.user_id))];
        if (userIds.length > 0) {
          const usersResp = await api.users.list({ limit: 100 });
          if (usersResp.data) {
            const map: Record<number, User> = {};
            for (const u of usersResp.data.users) {
              if (userIds.includes(u.id)) map[u.id] = u;
            }
            setAssignmentsUsers(map);
          }
        }
      }
    } catch {
      toast(t("meetings.errorLoadingUsers"), "error");
    } finally {
      setAssignmentsLoading(false);
    }
  };

  const handleRemoveAssignment = async (assignmentId: number) => {
    try {
      await api.userMeetings.delete(assignmentId);
      setAssignments((prev) => prev.filter((a) => a.id !== assignmentId));
      toast(t("meetings.assignmentRemoved"), "success");
    } catch {
      toast(t("meetings.errorRemovingAssignment"), "error");
    }
  };

  const handleAssign = async (userId: number, meetingId: number) => {
    const resp = await api.userMeetings.assign({
      user_id: userId,
      meeting_id: meetingId,
    });
    if (resp.data) {
      toast(t("meetings.meetingAssigned"), "success");
      setIsAssignDialogOpen(false);
    } else {
      toast(resp.error || t("meetings.errorAssigning"), "error");
    }
  };

  return (
    <PageContent
      title={t("meetings.title")}
      subtitle={t("meetings.title")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            m.resetForm();
            m.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("meetings.scheduleMeeting")}
        </Button>
      }
    >
      <Dialog open={m.isCreateDialogOpen} onOpenChange={m.setIsCreateDialogOpen}>
        <MeetingFormDialog
          mode="create"
          formData={m.formData}
          departments={d.items}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleCreate}
          onCancel={() => {
            m.setIsCreateDialogOpen(false);
            m.resetForm();
          }}
        />
      </Dialog>

      <Dialog open={m.isEditDialogOpen} onOpenChange={m.setIsEditDialogOpen}>
        <MeetingFormDialog
          mode="edit"
          formData={m.formData}
          departments={d.items}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleUpdate}
          onCancel={() => {
            m.setIsEditDialogOpen(false);
            m.setSelectedMeeting(null);
            m.resetForm();
          }}
        />
      </Dialog>

      <AssignDialog
        isOpen={isAssignDialogOpen}
        onOpenChange={setIsAssignDialogOpen}
        meetingId={assignMeetingId}
        meetingTitle={assignMeetingTitle}
        onAssign={handleAssign}
      />

      <AssignmentsDialog
        isOpen={isAssignmentsDialogOpen}
        onOpenChange={setIsAssignmentsDialogOpen}
        meetingTitle={assignmentsMeetingTitle}
        assignments={assignments}
        assignmentsUsers={assignmentsUsers}
        assignmentsLoading={assignmentsLoading}
        onRemoveAssignment={handleRemoveAssignment}
      />

      <DataTable
        loading={m.loading}
        empty={m.meetings.length === 0}
        emptyMessage={t("meetings.noMeetings")}
        currentPage={m.currentPage}
        totalPages={m.totalPages}
        totalCount={m.totalCount}
        pageSize={m.pageSize}
        onPageChange={m.setCurrentPage}
        onPageSizeChange={m.setPageSize}
        showPageSizeSelector={true}
        header={
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                {t("meetings.meetings")}{" "}
                <span className="text-muted-foreground text-sm font-normal">({m.totalCount})</span>
              </CardTitle>
              <div className="flex gap-2">
                <SearchInput value={m.searchQuery} onChange={m.setSearchQuery} />
                <Select value={m.typeFilter} onChange={m.setTypeFilter} options={MEETING_TYPES} />
                <Button variant="outline" onClick={m.resetFilters}>
                  {t("common.reset")}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("meetings.name")}</TableHead>
              <TableHead>{t("meetings.type")}</TableHead>
              <TableHead>{t("meetings.department")}</TableHead>
              <TableHead>{t("meetings.deadlineDays")}</TableHead>
              <TableHead>{t("meetings.isMandatory")}</TableHead>
              <TableHead>{t("meetings.order")}</TableHead>
              <TableHead>{t("common.created")}</TableHead>
              <TableHead className="w-45">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {m.meetings.map((meeting) => (
              <TableRow
                key={meeting.id}
                className="hover:bg-muted cursor-pointer"
                onClick={() => m.openEditDialog(meeting)}
              >
                <TableCell>
                  <div>
                    <p className="font-medium">{meeting.title}</p>
                    {meeting.description && (
                      <p className="text-muted-foreground line-clamp-1 max-w-64 text-sm">
                        {meeting.description}
                      </p>
                    )}
                  </div>
                </TableCell>
                <TableCell>{MEETING_TYPES.find(t => t.value === meeting.type)?.label || meeting.type}</TableCell>
                <TableCell>{meeting.department || d.items.find(dept => dept.id === meeting.departmentId)?.name || "-"}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Calendar className="text-muted-foreground size-4" />
                    {meeting.deadlineDays} {t("common.days")}
                  </div>
                </TableCell>
                <TableCell>
                  {meeting.isMandatory ? (
                    <span className="text-green-600">{t("common.yes")}</span>
                  ) : (
                    <span className="text-muted-foreground">{t("common.no")}</span>
                  )}
                </TableCell>
                <TableCell>{meeting.order}</TableCell>
                <TableCell>{formatDate(meeting.createdAt)}</TableCell>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title={t("meetings.assignedUsers")}
                      onClick={() => openAssignmentsDialog(meeting.id, meeting.title)}
                    >
                      <Users className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title={t("meetings.assignMeeting")}
                      onClick={() => openAssignDialog(meeting.id, meeting.title)}
                    >
                      <UserPlus className="size-4" />
                    </Button>
                     <Button variant="ghost" size="icon" onClick={() => m.openEditDialog(meeting)}>
                       <SquarePen className="size-4" />
                     </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500"
                      onClick={() => m.handleDelete(meeting.id)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
