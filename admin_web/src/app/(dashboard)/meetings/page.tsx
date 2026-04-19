"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Dialog } from "@/components/ui/dialog";
import { PageContent } from "@/components/layout/page-content";
import { Calendar, Clock, UserPlus, Users } from "lucide-react";
import { MEETING_TYPES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { useMeetings } from "@/hooks/use-meetings";
import { useDepartments } from "@/hooks/use-departments";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { EntityPage } from "@/components/entity";
import { MeetingFormDialog } from "@/components/meetings/meeting-form-dialog";
import { AssignDialog, AssignmentsDialog } from "@/components/meetings";
import type { User, UserMeeting } from "@/types";
import type { MeetingItem, MeetingFormData } from "@/hooks/use-meetings";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

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

  const renderActionButtons = (item: MeetingItem) => {
    return (
      <div className="flex gap-1">
        <Button
          variant="ghost"
          size="icon"
          title={t("meetings.assignedUsers")}
          onClick={() => openAssignmentsDialog(item.id, item.title)}
        >
          <Users className="size-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          title={t("meetings.assignMeeting")}
          onClick={() => openAssignDialog(item.id, item.title)}
        >
          <UserPlus className="size-4" />
        </Button>
      </div>
    );
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

      <EntityPage<MeetingItem, MeetingFormData>
        title={t("meetings.meetings")}
        items={m.meetings}
        totalItems={m.totalCount}
        pageSize={m.pageSize}
        currentPage={m.currentPage}
        isLoading={m.loading}
        onPageSizeChange={m.setPageSize}
        isCreateOpen={m.isCreateDialogOpen}
        isEditOpen={m.isEditDialogOpen}
        selectedItem={m.selectedMeeting}
        onCreateOpen={() => {
          m.resetForm();
          m.setIsCreateDialogOpen(true);
        }}
        onEditOpen={m.openEditDialog}
        onDelete={m.handleDelete}
        onCloseDialog={() => {
          m.setIsCreateDialogOpen(false);
          m.setIsEditDialogOpen(false);
          m.resetForm();
        }}
        formData={m.formData}
        onFormChange={(data) => m.setFormData(data)}
        onSubmit={m.handleCreate}
        isSubmitting={m.isCreating}
        submitError={null}
        searchQuery={m.searchQuery}
        onSearchChange={m.setSearchQuery}
        onPageChange={m.setCurrentPage}
        createButtonLabel={t("meetings.scheduleMeeting")}
        emptyStateMessage={t("meetings.noMeetings")}
        searchPlaceholder={t("common.search")}
        getItemKey={(item) => item.id}
        sortField={m.sortField}
        sortDirection={m.sortDirection}
        onSort={m.toggleSort}
        filters={
          <Select
            value={m.typeFilter}
            onChange={m.setTypeFilter}
            options={MEETING_TYPES}
          />
        }
        columns={[
          {
            key: "title",
            header: t("meetings.name"),
            cell: (item) => (
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
            cell: (item) => MEETING_TYPES.find((t) => t.value === item.type)?.label || item.type,
            sortable: true,
          },
          {
            key: "department",
            header: t("meetings.department"),
            cell: (item) =>
              item.department || d.items.find((dept) => dept.id === item.departmentId)?.name || "—",
            sortable: true,
          },
          {
            key: "deadlineDays",
            header: t("meetings.deadlineDays"),
            cell: (item) => (
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
            cell: (item) => (
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
            cell: (item) =>
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
            cell: (item) => item.order,
            sortable: true,
            width: "w-24",
          },
          {
            key: "createdAt",
            header: t("common.created"),
            cell: (item) => formatDate(item.createdAt),
            sortable: true,
            width: "w-32",
          },
          {
            key: "assignments",
            header: "",
            cell: renderActionButtons,
            width: "w-24",
          },
        ]}
        renderForm={({ formData, onChange }) => (
          <MeetingFormDialog
            mode="create"
            formData={formData}
            departments={d.items}
            onFormDataChange={(value) => {
              if (typeof value === "function") {
                onChange(value(formData));
              } else {
                onChange(value);
              }
            }}
            onSubmit={() => {}}
            onCancel={() => {}}
          />
        )}
        isFormValid={!!m.formData.title}
      />
    </PageContent>
  );
}
