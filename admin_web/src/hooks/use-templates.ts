import { useEffect } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { TaskTemplate } from "@/types";
import { useQuery } from "@tanstack/react-query";

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
  },
  taskCount: number,
): TemplateItem {
  return {
    id: data.id,
    name: data.name,
    description: data.description || "",
    department_id: data.department_id,
    department: data.department?.name || "",
    position: data.position || "",
    durationDays: data.duration_days,
    taskCount,
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
  const entity = useEntity<TemplateItem, TemplateFormData, ReturnType<typeof toCreatePayload>, ReturnType<typeof toUpdatePayload>>({
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
      return mapTemplateToItem(t, (t as { tasks?: unknown[] }).tasks?.length ?? 0);
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
  }, []);

  // Fetch departments
  const { data: departmentsData } = useQuery({
    queryKey: queryKeys.departments.all,
    queryFn: () => api.departments.list({ limit: 1000 }),
    select: (result) => result.data?.departments || [],
  });

  const addTasksToTemplate = async (templateId: number, tasks: TaskTemplate[]) => {
    for (const task of tasks) {
      await api.templates.addTask(templateId, {
        template_id: templateId,
        title: task.title,
        description: task.description,
        instructions: task.instructions,
        category: task.category,
        order: task.order,
        due_days: task.due_days,
        estimated_minutes: task.estimated_minutes,
      });
    }
  };

  const handleCreate = async () => {
    const { tasks } = entity.extendedState as unknown as ExtendedState;
    const result = await api.templates.create(toCreatePayload(entity.formData));
    if (result.data) {
      await addTasksToTemplate(result.data.id, tasks);
      entity.invalidate();
      entity.setIsCreateDialogOpen(false);
      entity.resetForm();
      entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
    }
  };

  const handleUpdate = async () => {
    if (!entity.selectedItem) return;
    const { tasks } = entity.extendedState as unknown as ExtendedState;
    const result = await api.templates.update(entity.selectedItem.id, toUpdatePayload(entity.formData));
    if (result.data) {
      const newTasks = tasks.filter((t) => !t.id || t.id === 0);
      await addTasksToTemplate(entity.selectedItem.id, newTasks);
      entity.invalidate();
      entity.setIsEditDialogOpen(false);
      entity.setSelectedItem(null);
      entity.resetForm();
      entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
    }
  };

  const handleDelete = async (id: number) => {
    await entity.handleDelete(id);
  };

  const handlePublish = (id: number) => {
    return api.templates.publish(id);
  };

  const openEditDialog = (template: TemplateItem) => {
    entity.setSelectedItem(template);
    entity.setFormData(toForm(template));
    entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
    entity.setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    entity.resetForm();
    entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
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
    tasks: (entity.extendedState as unknown as ExtendedState).tasks ?? [],
    setTasks: (tasks: TaskTemplate[]) =>
      entity.setExtendedState((prev) => ({ ...(prev as unknown as ExtendedState), tasks })),

    // Handlers
    handleCreate,
    handleUpdate,
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
