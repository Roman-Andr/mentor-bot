"use client";

import { Fragment, useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Dialog } from "@/shared/ui/dialog";
import { PageContent } from "@/shared/layout/page-content";
import { useMeetings } from "@/shared/hooks/use-meetings";
import { useDepartments } from "@/shared/hooks/use-departments";
import { useToast } from "@/shared/hooks/use-toast";
import { useConfirm } from "@/shared/hooks/use-confirm";
import { api } from "@/shared/lib/api";
import { MeetingFormDialog } from "@/widgets/meetings/meeting-form-dialog";
import { AssignDialog, AssignmentsDialog } from "@/widgets/meetings";
import { MaterialsPanel } from "@/widgets/meetings/materials-panel";
import type { User, UserMeeting } from "@/shared/types";
import type { MeetingItem } from "@/shared/hooks/use-meetings";
import { Select } from "@/shared/ui/select";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { CardHeader, CardTitle } from "@/shared/ui/card";
import { Plus, Pencil, Trash2, ChevronDown, ChevronRight, Shield } from "lucide-react";
import { getMeetingTypeOptions } from "@/shared/lib/constants";
import { useMeetingsColumns } from "@/widgets/meetings/meetings-columns";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { cn } from "@/shared/lib/utils";

export function MeetingsWidget() {
  const t = useTranslations();
  const m = useMeetings();
  const d = useDepartments();
  const { toast } = useToast();
  const confirm = useConfirm();

  const typeOptions = getMeetingTypeOptions(t, true);
  const mandatoryCount = m.meetings.filter((meet) => meet.isMandatory).length;

  const getMandatoryForm = (n: number) => {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod100 >= 11 && mod100 <= 14) return t("meetings.mandatoryMany");
    if (mod10 === 1) return t("meetings.mandatoryOne");
    if (mod10 >= 2 && mod10 <= 4) return t("meetings.mandatoryFew");
    return t("meetings.mandatoryMany");
  };

  const [expandedId, setExpandedId] = useState<number | null>(null);
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
    const resp = await api.userMeetings.assign({ user_id: userId, meeting_id: meetingId });
    if (resp.success && resp.data) {
      toast(t("meetings.meetingAssigned"), "success");
      setIsAssignDialogOpen(false);
    } else {
      toast(!resp.success && resp.error ? resp.error.message : t("meetings.errorAssigning"), "error");
    }
  };

  const handleDelete = async (meeting: MeetingItem) => {
    if (!(await confirm({
      title: t("meetings.deleteMeeting") || "Delete meeting",
      description: t("common.confirmDelete").replace("item", `"${meeting.title}"`),
      variant: "destructive",
      confirmText: t("common.delete"),
    }))) return;
    m.handleDelete(meeting.id);
  };

  const columns = useMeetingsColumns({ departments: d.items, onOpenAssignDialog: openAssignDialog, onOpenAssignmentsDialog: openAssignmentsDialog, t });

  const toggleExpand = (id: number) => setExpandedId((prev) => (prev === id ? null : id));

  return (
    <PageContent title={t("meetings.title")} subtitle={t("meetings.title")}>
      <Dialog open={m.isCreateDialogOpen} onOpenChange={m.setIsCreateDialogOpen}>
        <MeetingFormDialog
          mode="create"
          formData={m.formData}
          departments={d.items}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleCreate}
          onCancel={() => { m.setIsCreateDialogOpen(false); m.resetForm(); }}
        />
      </Dialog>

      <Dialog open={m.isEditDialogOpen} onOpenChange={m.setIsEditDialogOpen}>
        <MeetingFormDialog
          mode="edit"
          formData={m.formData}
          departments={d.items}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleUpdate}
          onCancel={() => { m.setIsEditDialogOpen(false); m.setSelectedMeeting(null); m.resetForm(); }}
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
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <CardTitle>
                  {t("meetings.meetings")}{" "}
                  <span className="text-muted-foreground text-sm font-normal">({m.totalCount})</span>
                </CardTitle>
                {mandatoryCount > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                    <Shield className="size-3" />
                    {mandatoryCount} {getMandatoryForm(mandatoryCount)}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <SearchInput placeholder={t("common.searchPlaceholder")} value={m.searchQuery} onChange={m.setSearchQuery} />
                <Select value={m.typeFilter} onChange={m.setTypeFilter} options={typeOptions} className="w-[180px]" />
                <Button onClick={() => { m.resetForm(); m.setIsCreateDialogOpen(true); }} className="gap-2">
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
              <TableHead className="w-8" />
              <SortableTableHead field="title" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.name")}</SortableTableHead>
              <SortableTableHead field="type" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.type")}</SortableTableHead>
              <SortableTableHead field="department" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.department")}</SortableTableHead>
              <SortableTableHead field="deadlineDays" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.deadlineDays")}</SortableTableHead>
              <SortableTableHead field="durationMinutes" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.durationMinutes")}</SortableTableHead>
              <SortableTableHead field="isMandatory" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.isMandatory")}</SortableTableHead>
              <SortableTableHead field="order" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("meetings.order")}</SortableTableHead>
              <SortableTableHead field="createdAt" sortable={true} sortField={m.sortField ?? null} sortDirection={m.sortDirection} onSort={m.toggleSort}>{t("common.created")}</SortableTableHead>
              <TableHead className="w-36">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {m.meetings.map((meeting) => (
              <Fragment key={meeting.id}>
                <TableRow
                  className={cn("hover:bg-muted cursor-pointer transition-colors", expandedId === meeting.id && "bg-muted/50")}
                  onClick={() => toggleExpand(meeting.id)}
                >
                  <TableCell className="w-8 pr-0">
                    {expandedId === meeting.id ? <ChevronDown className="text-muted-foreground size-4" /> : <ChevronRight className="text-muted-foreground size-4" />}
                  </TableCell>
                  {columns.slice(0, -1).map((column, idx) => (
                    <TableCell key={idx}>{column.cell(meeting)}</TableCell>
                  ))}
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      {columns[columns.length - 1].cell(meeting)}
                      <Button variant="ghost" size="icon" className="size-8" onClick={() => m.openEditDialog(meeting)}>
                        <Pencil className="size-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="size-8 text-red-500 hover:text-red-600" onClick={() => handleDelete(meeting)}>
                        <Trash2 className="size-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
                {expandedId === meeting.id && (
                  <TableRow key={`${meeting.id}-materials`} className="bg-muted/30">
                    <TableCell colSpan={11} className="py-3 pl-10 pr-6">
                      <MaterialsPanel meetingId={meeting.id} />
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
