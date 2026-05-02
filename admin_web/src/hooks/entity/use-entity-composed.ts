import { useState, useCallback, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "../use-debounce";
import { useToast } from "../use-toast";
import { useConfirm } from "../use-confirm";
import { useTranslations } from "../use-translations";
import { usePaginationSettings } from "@/components/providers/pagination-provider";
import type { ListParams } from "../use-queries";
import type {
  UseEntityOptions,
  UseEntityContext,
  UseEntityResult,
  FilterConfig,
  EntityLabels,
} from "./types";
import { useEntityQuery } from "./use-entity-query";
import { useEntityMutations } from "./use-entity-mutations";
import { useEntityFilters } from "./use-entity-filters";
import { useEntityPagination } from "./use-entity-pagination";

export function useEntity<TItem, TForm, TCreatePayload = unknown, TUpdatePayload = unknown, TExtendedState = Record<string, unknown>>(
  options: UseEntityOptions<TItem, TForm, TCreatePayload, TUpdatePayload, TExtendedState>,
): UseEntityResult<TItem, TForm, TCreatePayload, TUpdatePayload, TExtendedState> {
  const {
    entityName,
    translationNamespace,
    queryKeyPrefix,
    listFn,
    listDataKey = "items",
    createFn,
    updateFn,
    deleteFn,
    defaultForm,
    defaultExtendedState,
    mapItem,
    toCreatePayload,
    toUpdatePayload,
    toForm,
    labels = {},
    filters = [],
    searchable = true,
    searchParamName = "search",
    sortable = false,
    sortFieldParam = "sort_by",
    sortDirectionParam = "sort_order",
    customMutations: customMutationsConfig,
    pageSize: initialPageSize,
    entityLabelKey,
  } = options;

  // Initialize translations - always call hooks unconditionally
  const tNamespace = useTranslations((translationNamespace as import("../use-translations").Namespace) ?? "common");
  const tCommon = useTranslations("common");
  const t = translationNamespace ? tNamespace : tCommon;

  // Resolve entity name from entityLabelKey if provided
  const resolvedEntityName = entityLabelKey ? t(entityLabelKey as any) as string : entityName;

  // Resolve label with i18n support (translation keys take precedence)
  const resolveLabel = useCallback((key: keyof EntityLabels, fallback: string): string => {
    const translationKey = labels[`${key}Key` as keyof EntityLabels] as string | undefined;
    if (translationKey && t) {
      const keyParts = translationKey.split(".");
      const finalKey = keyParts.length > 1 ? keyParts[keyParts.length - 1] : translationKey;
      return t(finalKey) as string;
    }
    return labels[key] ?? fallback;
  }, [labels, t]);

  const created = resolveLabel("created", `${resolvedEntityName}`);
  const updated = resolveLabel("updated", `${resolvedEntityName}`);
  const deleted = resolveLabel("deleted", `${resolvedEntityName}`);
  const createError = resolveLabel("createError", `${resolvedEntityName}`);
  const updateError = resolveLabel("updateError", `${resolvedEntityName}`);
  const deleteError = resolveLabel("deleteError", `${resolvedEntityName}`);
  const deleteConfirmTitle = resolveLabel("deleteConfirmTitle", tCommon("deleteTitle") ?? "");
  const deleteConfirmDescription = resolveLabel("deleteConfirmDescription", tCommon("confirmDelete") ?? "");

  const { toast } = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();
  const { pageSize: globalPageSize, setPageSize: setGlobalPageSize } = usePaginationSettings();

  // Extended state for custom fields (attachments, tasks, etc.)
  const [extendedState, setExtendedStateState] = useState<TExtendedState>(
    defaultExtendedState ?? ({} as TExtendedState),
  );

  const setExtendedState = useCallback(
    (updater: (prev: TExtendedState) => TExtendedState) => {
      setExtendedStateState((prev) => updater(prev));
    },
    [],
  );

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery);

  // Pagination state
  const { currentPage, setCurrentPage, pageSize, setPageSize } = useEntityPagination(initialPageSize);

  // Filters and sorting state
  const {
    filterValues,
    setFilterValue,
    resetFilters,
    sortField,
    sortDirection,
    toggleSort,
    setSort,
    clearSort,
  } = useEntityFilters(filters, setCurrentPage);

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  // Selection state
  const [selectedItem, setSelectedItem] = useState<TItem | null>(null);

  // Form state
  const [formData, setFormData] = useState<TForm>({ ...defaultForm });

  // Build query params
  const queryParams = useMemo(() => {
    const params: ListParams = {
      skip: (currentPage - 1) * pageSize,
      limit: pageSize,
    };

    // Add search
    if (searchable && debouncedSearch) {
      params[searchParamName] = debouncedSearch;
    }

    // Add filters
    for (const filter of filters) {
      const value = filterValues[filter.name];
      if (value !== "ALL" && value !== "" && value !== undefined) {
        const paramName = filter.paramName ?? filter.name;
        params[paramName] = filter.transform ? filter.transform(value) : value;
      }
    }

    // Add sorting
    if (sortable && sortField) {
      params[sortFieldParam] = sortField;
      params[sortDirectionParam] = sortDirection;
    }

    return params;
  }, [currentPage, pageSize, searchable, debouncedSearch, searchParamName, filters, filterValues, sortable, sortField, sortDirection, sortFieldParam, sortDirectionParam]);

  // Query
  const { items, loading, totalCount, totalPages } = useEntityQuery(
    { queryKeyPrefix, listFn, listDataKey, mapItem },
    queryParams,
  );

  // Invalidate helper
  const invalidate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: [queryKeyPrefix] });
  }, [queryClient, queryKeyPrefix]);

  // Internal reset form
  const resetFormInternal = useCallback(() => {
    setFormData({ ...defaultForm });
    setSelectedItem(null);
    setExtendedStateState(defaultExtendedState ?? ({} as TExtendedState));
  }, [defaultForm, defaultExtendedState]);

  // Mutations
  const mutationContext = {
    toast,
    invalidate,
    extendedState,
    setExtendedState,
    selectedItem,
    formData,
  };

  const { createMutation, updateMutation, deleteMutation, handleSubmit, isSubmitting, isDeleting } = useEntityMutations(
    { createFn, updateFn, deleteFn, queryKeyPrefix, onAfterCreate: options.onAfterCreate, onAfterUpdate: options.onAfterUpdate, toCreatePayload },
    mutationContext,
    { created, updated, deleted, createError, updateError, deleteError },
    resetFormInternal,
    setIsCreateDialogOpen,
    setIsEditDialogOpen,
    setSelectedItem,
    toUpdatePayload,
  );

  // Custom mutations
  const customMutationsContext: UseEntityContext<TItem, TForm, TExtendedState> = {
    selectedItem,
    formData,
    extendedState,
    setExtendedState,
    queryClient,
    toast,
    invalidate,
  };

  const customMutations = useMemo(() => {
    if (!customMutationsConfig) return {};
    return customMutationsConfig(customMutationsContext);
  }, [customMutationsConfig, customMutationsContext]);

  // Handlers
  const updateFormField = useCallback(<K extends keyof TForm>(field: K, value: TForm[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData({ ...defaultForm });
    setSelectedItem(null);
    setExtendedStateState(defaultExtendedState ?? ({} as TExtendedState));
  }, [defaultForm, defaultExtendedState]);

  const handleDelete = useCallback(
    async (id: number) => {
      const confirmed = await confirm({
        title: deleteConfirmTitle,
        description: deleteConfirmDescription,
        variant: "destructive",
        confirmText: tCommon("delete") ?? "Delete",
      });
      if (confirmed) {
        deleteMutation.mutate(id);
      }
    },
    [confirm, deleteConfirmTitle, deleteConfirmDescription, deleteMutation, tCommon],
  );

  const openEditDialog = useCallback(
    (item: TItem) => {
      setSelectedItem(item);
      setFormData(toForm(item));
      setIsEditDialogOpen(true);
    },
    [toForm],
  );

  return {
    // Data
    items,
    loading,
    totalCount,
    totalPages,

    // Pagination
    currentPage,
    setCurrentPage,
    pageSize,
    setPageSize,

    // Search
    searchQuery,
    setSearchQuery,
    debouncedSearch,

    // Filters
    filterValues,
    setFilterValue,
    resetFilters,

    // Sorting
    sortField,
    sortDirection,
    toggleSort,
    setSort,
    clearSort,

    // Dialogs
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,

    // Selection
    selectedItem,
    setSelectedItem,

    // Form
    formData,
    setFormData,
    updateFormField,
    resetForm,

    // Extended state
    extendedState,
    setExtendedState,

    // Handlers
    handleSubmit,
    handleDelete,
    openEditDialog,

    // Direct mutation functions
    createFn,
    updateFn,
    deleteFn,

    // Loading states
    isSubmitting,
    isDeleting,

    // Custom mutations
    customMutations,

    // Utilities
    invalidate,
  };
}
