"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Dialog } from "@/components/ui/dialog";
import { PageContent } from "@/components/layout/page-content";
import { useMeetings } from "@/hooks/use-meetings";
import { useDepartments } from "@/hooks/use-departments";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { MeetingFormDialog } from "@/components/meetings/meeting-form-dialog";
import { AssignDialog, AssignmentsDialog } from "@/components/meetings";
import type { User, UserMeeting } from "@/types";
import type { MeetingItem, MeetingFormData } from "@/hooks/use-meetings";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Plus } from "lucide-react";
import { getMeetingTypeOptions } from "@/lib/constants";
import { useMeetingsColumns } from "@/components/features/meetings/meetings-columns";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { SortableTableHead } from "@/components/ui/sortable-table-head";

export default function MeetingsPage() {
  const t = useTranslations();
  const m = useMeetings();
  const d = useDepartments();
  const { toast } = useToast();

  const typeOptions = getMeetingTypeOptions(t, true);

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
      if (resp.success && resp.data) {
        setAssignments(resp.data.items);
        const userIds = [...new Set(resp.data.items.map((a) => a.user_id))];
        const usersResp = await api.users.list({ limit: 100 });
        if (usersResp.success && usersResp.data) {
          const map: Record<number, User> = {};
          for (const u of usersResp.data.users) {
            if (userIds.includes(u.id)) map[u.id] = u;
          }
          setAssignmentsUsers(map);
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
    if (resp.success && resp.data) {
      toast(t("meetings.meetingAssigned"), "success");
      setIsAssignDialogOpen(false);
    } else {
      toast(!resp.success && resp.error ? resp.error.message : t("meetings.errorAssigning"), "error");
    }
  };

  const columns = useMeetingsColumns({
    departments: d.items,
    onOpenAssignDialog: openAssignDialog,
    onOpenAssignmentsDialog: openAssignmentsDialog,
    t,
  });

  const handleCreateMeeting = () => {
    m.resetForm();
    m.setIsCreateDialogOpen(true);
  };

  return (
    <PageContent title={t("meetings.title")} subtitle={t("meetings.title")}>
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
        currentPage={m.currentPage}
        totalPages={Math.ceil(m.totalCount / m.pageSize)}
        totalCount={m.totalCount}
        pageSize={m.pageSize}
        onPageChange={m.setCurrentPage}
        onPageSizeChange={m.setPageSize}
        showPageSizeSelector={true}
        skeleton={<DataTableSkeleton columns={9} rows={5} showHeader={false} />}
        header={
          <CardHeader>
            <div className="flex items-center justify-between gap-4">
              <CardTitle>{t("meetings.meetings")}</CardTitle>
              <div className="flex items-center gap-2">
                <SearchInput
                  placeholder={t("common.searchPlaceholder")}
                  value={m.searchQuery}
                  onChange={m.setSearchQuery}
                />
                <Select
                  value={m.typeFilter}
                  onChange={m.setTypeFilter}
                  options={typeOptions}
                  className="w-[180px]"
                />
                <Button onClick={handleCreateMeeting} className="gap-2">
                  <Plus className="size-4" />
                  {t("meetings.scheduleMeeting")}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
        emptyMessage={t("meetings.noMeetings")}
      >
        <Table>
          <TableHeader>
            <TableRow>
              <SortableTableHead
                field="title"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.name")}
              </SortableTableHead>
              <SortableTableHead
                field="type"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.type")}
              </SortableTableHead>
              <SortableTableHead
                field="department"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.department")}
              </SortableTableHead>
              <SortableTableHead
                field="deadlineDays"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.deadlineDays")}
              </SortableTableHead>
              <SortableTableHead
                field="durationMinutes"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.durationMinutes")}
              </SortableTableHead>
              <SortableTableHead
                field="isMandatory"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.isMandatory")}
              </SortableTableHead>
              <SortableTableHead
                field="order"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("meetings.order")}
              </SortableTableHead>
              <SortableTableHead
                field="createdAt"
                sortable={true}
                sortField={m.sortField ?? null}
                sortDirection={m.sortDirection}
                onSort={m.toggleSort}
              >
                {t("common.created")}
              </SortableTableHead>
              <TableHead className="w-24">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {m.meetings.map((meeting) => (
              <TableRow key={meeting.id}>
                {columns.map((column, idx) => (
                  <TableCell key={idx}>{column.cell(meeting)}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
