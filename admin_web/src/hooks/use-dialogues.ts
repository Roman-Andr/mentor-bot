import { useEffect } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { DialogueScenario, DialogueCategory, DialogueAnswerType } from "@/types";
import { useQuery } from "@tanstack/react-query";

export interface DialogueRow {
  id: number;
  title: string;
  description: string;
  keywords: string[];
  category: DialogueCategory;
  isActive: boolean;
  displayOrder: number;
  stepsCount: number;
  createdAt: string;
}

export interface DialogueStepRow {
  id: number;
  scenario_id: number;
  step_number: number;
  question: string;
  answer_type: DialogueAnswerType;
  options: { label: string; next_step: number }[] | null;
  answer_content: string | null;
  is_final: boolean;
}

export interface DialogueFormData {
  title: string;
  description: string;
  keywords: string;
  category: DialogueCategory;
  is_active: boolean;
  display_order: number;
}

interface ExtendedState {
  selectedSteps: DialogueStepRow[];
}

const EMPTY_FORM: DialogueFormData = {
  title: "",
  description: "",
  keywords: "",
  category: "VACATION",
  is_active: true,
  display_order: 0,
};

const defaultExtendedState: ExtendedState = {
  selectedSteps: [],
};

function mapDialogue(d: DialogueScenario): DialogueRow {
  return {
    id: d.id,
    title: d.title,
    description: d.description || "",
    keywords: d.keywords,
    category: d.category as DialogueCategory,
    isActive: d.is_active,
    displayOrder: d.display_order,
    stepsCount: d.steps?.length || 0,
    createdAt: d.created_at ? d.created_at.split("T")[0] : "",
  };
}

function toPayload(form: DialogueFormData) {
  const keywordsArray = form.keywords
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);

  return {
    title: form.title,
    description: form.description || undefined,
    keywords: keywordsArray,
    category: form.category,
    is_active: form.is_active,
    display_order: form.display_order,
  };
}

function toForm(dialogue: DialogueRow): DialogueFormData {
  return {
    title: dialogue.title,
    description: dialogue.description,
    keywords: dialogue.keywords.join(", "),
    category: dialogue.category,
    is_active: dialogue.isActive,
    display_order: dialogue.displayOrder,
  };
}

export function useDialogues() {
  const entity = useEntity<DialogueRow, DialogueFormData, ReturnType<typeof toPayload>, ReturnType<typeof toPayload>, Record<string, unknown>>({
    entityName: "Диалог",
    translationNamespace: "dialogues",
    queryKeyPrefix: "dialogues",
    listFn: (params) => api.dialogues.list(params),
    listDataKey: "scenarios",
    createFn: (data) => api.dialogues.create(data),
    updateFn: (id, data) => api.dialogues.update(id, data),
    deleteFn: (id) => api.dialogues.delete(id),
    defaultForm: EMPTY_FORM,
    mapItem: (item: unknown) => mapDialogue(item as DialogueScenario),
    toCreatePayload: toPayload,
    toUpdatePayload: toPayload,
    toForm,
    searchable: true,
    searchParamName: "search",
    sortable: true,
    filters: [{ name: "category", defaultValue: "ALL" }],
    labels: {
      createdKey: "dialogues.created",
      updatedKey: "dialogues.updated",
      deletedKey: "dialogues.deleted",
      createErrorKey: "dialogues.createError",
      updateErrorKey: "dialogues.updateError",
      deleteErrorKey: "dialogues.deleteError",
    },
  });

  // Initialize selectedSteps state
  useEffect(() => {
    if (entity.extendedState.selectedSteps === undefined) {
      entity.setExtendedState(() => ({ selectedSteps: [] }));
    }
  }, [entity.extendedState.selectedSteps, entity.setExtendedState]);

  // Fetch steps for selected dialogue
  const { data: stepsData } = useQuery({
    queryKey: entity.selectedItem ? queryKeys.dialogues.steps(entity.selectedItem.id) : ["dialogue-steps", "none"],
    queryFn: () => api.dialogues.get(entity.selectedItem!.id),
    enabled: !!entity.selectedItem,
    select: (result) => {
      if (!result.success) return [];
      return (
        result.data.steps?.map((s) => ({
          id: s.id,
          scenario_id: s.scenario_id,
          step_number: s.step_number,
          question: s.question,
          answer_type: s.answer_type as DialogueAnswerType,
          options: s.options,
          answer_content: s.answer_content,
          is_final: s.is_final,
        })) || []
      );
    },
  });

  const handleToggleActive = (id: number, isActive: boolean) => {
    return api.dialogues.update(id, { is_active: isActive });
  };

  const openEdit = (dialogue: DialogueRow) => {
    entity.setSelectedItem(dialogue);
    entity.setFormData(toForm(dialogue));
    entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
    entity.setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    entity.resetForm();
    entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
  };

  return {
    // Data
    dialogues: entity.items,
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
    categoryFilter: entity.filterValues.category ?? "ALL",
    setCategoryFilter: (value: string) => entity.setFilterValue("category", value),

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedDialogue: entity.selectedItem,
    setSelectedDialogue: entity.setSelectedItem,
    selectedSteps: stepsData || entity.extendedState.selectedSteps || [],

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Handlers
    handleSubmit: entity.handleSubmit,
    handleDelete: entity.handleDelete,
    handleToggleActive,
    openEdit,
    resetForm,
    resetFilters: entity.resetFilters,

    // Loading states
    isSubmitting: entity.isSubmitting,
    isDeleting: entity.isDeleting,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,
  };
}

