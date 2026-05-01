import { useEffect } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { TaskTemplate } from "@/types";
import { useQuery } from "@tanstack/react-query";
import { logger } from "@/lib/logger";

export interface TemplateItem {
  id: number;
  name: string;
  description: string;
  department_id: number | null;
  department: string;
  position: string;
  durationDays: number;
  taskCount: number;
  status: string;
  isDefault: boolean;
}

export interface TemplateFormData {
  name: string;
  description: string;
  department_id: number;
  position: string;
  duration_days: number;
  status: string;
  is_default: boolean;
}

interface ExtendedState {
  tasks: TaskTemplate[];
}

const defaultFormData: TemplateFormData = {
  name: "",
  description: "",
  department_id: 0,
  position: "",
  duration_days: 30,
  status: "DRAFT",
  is_default: false,
};

const defaultExtendedState: ExtendedState = {
  tasks: [],
};

function mapTemplateToItem(
  data: {
    id: number;
    name: string;
    description: string | null;
    department_id: number | null;
    department: { id: number; name: string } | null;
    position: string | null;
    duration_days: number;
    status: string;
    is_default: boolean;
    task_categories: string[];
    task_count?: number;
  },
  departments: { id: number; name: string }[] = [],
): TemplateItem {
  // Find department name from departments list if not provided in response
  let departmentName = data.department?.name || "";
  if (!departmentName && data.department_id && departments.length > 0) {
    const dept = departments.find((d) => d.id === data.department_id);
    if (dept) {
      departmentName = dept.name;
    }
  }

  return {
    id: data.id,
    name: data.name,
    description: data.description || "",
    department_id: data.department_id,
    department: departmentName,
    position: data.position || "",
    durationDays: data.duration_days,
    taskCount: data.task_count ?? 0,
    status: data.status,
    isDefault: data.is_default,
  };
}

function toCreatePayload(form: TemplateFormData) {
  return {
    name: form.name,
    description: form.description,
    department_id: form.department_id || null,
    position: form.position || null,
    level: null,
    duration_days: form.duration_days,
    task_categories: [],
    status: (form.status || "DRAFT") as "DRAFT" | "ACTIVE" | "ARCHIVED",
  };
}

function toUpdatePayload(form: TemplateFormData) {
  return {
    name: form.name,
    description: form.description,
    status: (form.status || "DRAFT") as "DRAFT" | "ACTIVE" | "ARCHIVED",
    is_default: form.is_default,
  };
}

function toForm(template: TemplateItem): TemplateFormData {
  return {
    name: template.name,
    description: template.description,
    department_id: template.department_id || 0,
    position: template.position,
    duration_days: template.durationDays,
    status: template.status,
    is_default: template.isDefault,
  };
}

export function useTemplates() {
  // Fetch departments first
  const { data: departmentsData } = useQuery({
    queryKey: queryKeys.departments.all,
    queryFn: () => api.departments.list({ limit: 1000 }),
    select: (result) => result.success ? result.data?.departments || [] : [],
  });

  const entity = useEntity<TemplateItem, TemplateFormData, ReturnType<typeof toCreatePayload>, ReturnType<typeof toUpdatePayload>, ExtendedState>({
    entityName: "Шаблон",
    translationNamespace: "templates",
    queryKeyPrefix: "templates",
    listFn: (params) => api.templates.list(params),
    listDataKey: "templates",
    createFn: (data) => api.templates.create(data),
    updateFn: (id, data) => api.templates.update(id, data),
    deleteFn: (id) => api.templates.delete(id),
    defaultForm: defaultFormData,
    mapItem: (item: unknown) => {
      const t = item as Parameters<typeof mapTemplateToItem>[0];
      return mapTemplateToItem(t, departmentsData || []);
    },
    toCreatePayload,
    toUpdatePayload,
    toForm,
    searchable: true,
    searchParamName: "search",
    sortable: true,
    filters: [{ name: "status", defaultValue: "ALL" }],
    labels: {
      createdKey: "templates.created",
      updatedKey: "templates.updated",
      deletedKey: "templates.deleted",
      createErrorKey: "templates.createError",
      updateErrorKey: "templates.updateError",
      deleteErrorKey: "templates.deleteError",
    },
  });

  // Initialize tasks state
  useEffect(() => {
    if (entity.extendedState.tasks === undefined) {
      entity.setExtendedState(() => ({ tasks: [] }));
    }
  }, [entity]);


  const handleDelete = async (id: number) => {
    await entity.handleDelete(id);
  };

  const handlePublish = async (id: number) => {
    const result = await api.templates.publish(id);
    if (result.success) {
      entity.invalidate();
    }
    return result;
  };

  const openEditDialog = async (template: TemplateItem) => {
    entity.setSelectedItem(template);
    entity.setFormData(toForm(template));
    entity.setExtendedState(() => defaultExtendedState);

    // Fetch tasks for the template
    try {
      const response = await api.templates.get(template.id);
      if (response.success && response.data?.tasks) {
        entity.setExtendedState((prev) => ({
          ...prev,
          tasks: response.data.tasks,
        }));
      }
    } catch (error) {
      logger.error("Failed to fetch template tasks", { error });
    }

    entity.setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    entity.resetForm();
    entity.setExtendedState(() => defaultExtendedState);
  };

  // Use entity.items directly - taskCount comes from API response in mapItem
  const templates = entity.items;

  return {
    // Data
    templates,
    departments: departmentsData || [],
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

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedTemplate: entity.selectedItem,
    setSelectedTemplate: entity.setSelectedItem,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Tasks - ensure we always return an array
    tasks: entity.extendedState.tasks ?? [],
    setTasks: (tasks: TaskTemplate[]) =>
      entity.setExtendedState((prev) => ({ ...prev, tasks })),

    // Handlers
    handleCreate: entity.handleSubmit,
    handleUpdate: entity.handleSubmit,
    handleDelete,
    handlePublish,
    openEditDialog,
    resetForm,
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
