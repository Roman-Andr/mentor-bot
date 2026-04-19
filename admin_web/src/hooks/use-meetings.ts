import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import type { Meeting } from "@/types";

export interface MeetingItem {
  id: number;
  title: string;
  description: string;
  type: string;
  departmentId: number | null;
  department: string;
  position: string;
  level: string;
  deadlineDays: number;
  durationMinutes: number;
  isMandatory: boolean;
  order: number;
  createdAt: string;
}

export interface MeetingFormData {
  title: string;
  description: string;
  type: string;
  department_id: number;
  position: string;
  level: string;
  deadline_days: number;
  duration_minutes: number;
  is_mandatory: boolean;
  order: number;
}

function mapMeeting(m: Meeting): MeetingItem {
  return {
    id: m.id,
    title: m.title,
    description: m.description || "",
    type: m.type,
    departmentId: m.department_id,
    department: m.department?.name || "",
    position: m.position || "",
    level: m.level || "",
    deadlineDays: m.deadline_days,
    durationMinutes: m.duration_minutes,
    isMandatory: m.is_mandatory,
    order: m.order,
    createdAt: m.created_at,
  };
}

const defaultFormData: MeetingFormData = {
  title: "",
  description: "",
  type: "HR",
  department_id: 0,
  position: "",
  level: "",
  deadline_days: 7,
  duration_minutes: 60,
  is_mandatory: true,
  order: 0,
};

function toPayload(form: MeetingFormData) {
  return {
    title: form.title,
    description: form.description || null,
    type: form.type,
    department_id: form.department_id || null,
    position: form.position || null,
    level: form.level || null,
    deadline_days: form.deadline_days,
    duration_minutes: form.duration_minutes,
    is_mandatory: form.is_mandatory,
    order: form.order,
  };
}

function toForm(meeting: MeetingItem): MeetingFormData {
  return {
    title: meeting.title,
    description: meeting.description,
    type: meeting.type,
    department_id: meeting.departmentId || 0,
    position: meeting.position,
    level: meeting.level,
    deadline_days: meeting.deadlineDays,
    duration_minutes: meeting.durationMinutes,
    is_mandatory: meeting.isMandatory,
    order: meeting.order,
  };
}

export function useMeetings() {
  const entity = useEntity<MeetingItem, MeetingFormData, ReturnType<typeof toPayload>, ReturnType<typeof toPayload>>({
    entityName: "Встреча",
    translationNamespace: "meetings",
    queryKeyPrefix: "meetings",
    listFn: (params) => api.meetings.list(params),
    listDataKey: "meetings",
    createFn: (data) => api.meetings.create(data),
    updateFn: (id, data) => api.meetings.update(id, data),
    deleteFn: (id) => api.meetings.delete(id),
    defaultForm: defaultFormData,
    mapItem: (item: unknown) => mapMeeting(item as Meeting),
    toCreatePayload: toPayload,
    toUpdatePayload: toPayload,
    toForm,
    searchable: true,
    searchParamName: "search",
    filters: [{ name: "type", defaultValue: "ALL", paramName: "meeting_type" }],
    sortable: true,
    labels: {
      createdKey: "meetings.created",
      updatedKey: "meetings.updated",
      deletedKey: "meetings.deleted",
      createErrorKey: "meetings.createError",
      updateErrorKey: "meetings.updateError",
      deleteErrorKey: "meetings.deleteError",
    },
  });

  return {
    // Data
    meetings: entity.items,
    loading: entity.loading,
    totalCount: entity.totalCount,
    totalPages: entity.totalPages,

    // Pagination
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,

    // Search & Filters
    searchQuery: entity.searchQuery,
    setSearchQuery: entity.setSearchQuery,
    typeFilter: entity.filterValues.type ?? "ALL",
    setTypeFilter: (value: string) => entity.setFilterValue("type", value),

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedMeeting: entity.selectedItem,
    setSelectedMeeting: entity.setSelectedItem,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Handlers
    handleCreate: entity.handleSubmit,
    handleUpdate: entity.handleSubmit,
    handleDelete: entity.handleDelete,
    openEditDialog: entity.openEditDialog,
    resetForm: entity.resetForm,
    resetFilters: entity.resetFilters,

    // Loading states
    isCreating: entity.isSubmitting,
    isUpdating: entity.isSubmitting,
    isDeleting: entity.isDeleting,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,
  };
}
