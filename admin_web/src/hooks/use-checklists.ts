import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { useQuery } from "@tanstack/react-query";

export interface ChecklistItem {
  id: number;
  userId: number;
  employeeId: string;
  userName: string;
  templateId: number;
  status: string;
  progressPercentage: number;
  completedTasks: number;
  totalTasks: number;
  startDate: string;
  dueDate: string | null;
  completedAt: string | null;
  mentorId: number | null;
  hrId: number | null;
  notes: string | null;
  isOverdue: boolean;
  daysRemaining: number | null;
  createdAt: string;
  certUid: string | null;
}

export interface ChecklistFormData {
  user_id: number;
  employee_id: string;
  template_id: number;
  start_date: string;
  due_date: string;
  mentor_id: number | null;
  hr_id: number | null;
  notes: string;
}

const defaultFormData: ChecklistFormData = {
  user_id: 0,
  employee_id: "",
  template_id: 0,
  start_date: new Date().toISOString().split("T")[0],
  due_date: "",
  mentor_id: null,
  hr_id: null,
  notes: "",
};

function mapToItem(
  c: {
    id: number;
    user_id: number;
    employee_id: string;
    template_id: number;
    status: string;
    progress_percentage: number;
    completed_tasks: number;
    total_tasks: number;
    start_date: string;
    due_date: string | null;
    completed_at: string | null;
    mentor_id: number | null;
    hr_id: number | null;
    notes: string | null;
    is_overdue: boolean;
    days_remaining: number | null;
    created_at: string;
    cert_uid: string | null;
  },
  usersMap: Map<number, string>,
): ChecklistItem {
  return {
    id: c.id,
    userId: c.user_id,
    employeeId: c.employee_id,
    userName: usersMap.get(c.user_id) || c.employee_id || `User ${c.user_id}`,
    templateId: c.template_id,
    status: c.status,
    progressPercentage: c.progress_percentage,
    completedTasks: c.completed_tasks,
    totalTasks: c.total_tasks,
    startDate: c.start_date,
    dueDate: c.due_date,
    completedAt: c.completed_at,
    mentorId: c.mentor_id,
    hrId: c.hr_id,
    notes: c.notes,
    isOverdue: c.is_overdue,
    daysRemaining: c.days_remaining,
    createdAt: c.created_at,
    certUid: c.cert_uid,
  };
}

function toCreatePayload(form: ChecklistFormData) {
  return {
    user_id: form.user_id,
    employee_id: form.employee_id,
    template_id: form.template_id,
    start_date: new Date(form.start_date).toISOString(),
    due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
    mentor_id: form.mentor_id,
    hr_id: form.hr_id,
    notes: form.notes || null,
  };
}

function toUpdatePayload(form: ChecklistFormData) {
  return {
    mentor_id: form.mentor_id,
    hr_id: form.hr_id,
    notes: form.notes || null,
  };
}

function toForm(checklist: ChecklistItem): ChecklistFormData {
  return {
    user_id: checklist.userId,
    employee_id: checklist.employeeId,
    template_id: checklist.templateId,
    start_date: checklist.startDate.split("T")[0],
    due_date: checklist.dueDate ? checklist.dueDate.split("T")[0] : "",
    mentor_id: checklist.mentorId,
    hr_id: checklist.hrId,
    notes: checklist.notes || "",
  };
}

export function useChecklists() {
  // Fetch users to map user_id to user_name
  const { data: usersData } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => api.users.list({ limit: 1000 }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const usersMap = new Map<number, string>();
  if (usersData?.success && usersData.data?.users) {
    for (const user of usersData.data.users) {
      usersMap.set(user.id, `${user.first_name}${user.last_name ? ` ${user.last_name}` : ""}`);
    }
  }

  const entity = useEntity<ChecklistItem, ChecklistFormData, ReturnType<typeof toCreatePayload>, ReturnType<typeof toUpdatePayload>>({
    entityName: "Чек-лист",
    translationNamespace: "checklists",
    queryKeyPrefix: "checklists",
    listFn: (params) => api.checklists.list(params),
    listDataKey: "checklists",
    createFn: (data) => api.checklists.create(data),
    updateFn: (id, data) => api.checklists.update(id, data),
    deleteFn: (id) => api.checklists.delete(id),
    defaultForm: defaultFormData,
    mapItem: (item: unknown) => mapToItem(item as Parameters<typeof mapToItem>[0], usersMap),
    toCreatePayload,
    toUpdatePayload,
    toForm,
    labels: {
      createdKey: "checklists.created",
      updatedKey: "checklists.updated",
      deletedKey: "checklists.deleted",
      createErrorKey: "checklists.createError",
      updateErrorKey: "checklists.updateError",
      deleteErrorKey: "checklists.deleteError",
    },
    searchable: true,
    searchParamName: "search",
    sortable: true,
    filters: [
      { name: "status", defaultValue: "ALL" },
      { name: "department", defaultValue: "ALL", paramName: "department_id", transform: (v) => parseInt(v) },
    ],
  });

  const handleCreate = () => {
    const payload = toCreatePayload(entity.formData);
    entity.createFn?.(payload).then((result) => {
      if (!result?.success) {
        // Error is already handled by entity hook's onError
        return;
      }
      entity.invalidate();
      entity.setIsCreateDialogOpen(false);
      entity.resetForm();
    });
  };

  const handleUpdate = () => {
    if (!entity.selectedItem) return;
    const payload = toUpdatePayload(entity.formData);
    entity.updateFn?.(entity.selectedItem.id, payload).then((result) => {
      if (!result?.success) {
        // Error is already handled by entity hook's onError
        return;
      }
      entity.invalidate();
      entity.setIsEditDialogOpen(false);
      entity.setSelectedItem(null);
      entity.resetForm();
    });
  };

  const handleComplete = (id: number) => {
    return api.checklists.complete(id);
  };

  return {
    // Data
    checklists: entity.items,
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
    statusFilter: entity.filterValues.status ?? "ALL",
    setStatusFilter: (value: string) => entity.setFilterValue("status", value),
    departmentFilter: entity.filterValues.department ?? "ALL",
    setDepartmentFilter: (value: string) => entity.setFilterValue("department", value),

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedChecklist: entity.selectedItem,
    setSelectedChecklist: entity.setSelectedItem,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Handlers
    handleCreate,
    handleUpdate,
    handleDelete: entity.handleDelete,
    handleComplete,
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
