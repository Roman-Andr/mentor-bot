import { useState, useCallback, useMemo } from "react";
import { useQuery, useMutation, useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useDebounce } from "./use-debounce";
import { useToast } from "./use-toast";
import { useConfirm } from "./use-confirm";
import { useTranslations } from "./use-translations";
import { usePaginationSettings } from "@/components/providers/pagination-provider";
import { queryKeys, getEntityListKey } from "@/lib/query-keys";
import type { ListParams } from "./use-queries";

// ============================================================================
// Types
// ============================================================================

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
}

export interface EntityListResponse {
  items?: unknown[];
  total?: number;
  pages?: number;
  // Allow any additional properties from specific entity responses
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

export interface FilterConfig {
  name: string;
  defaultValue: string;
  paramName?: string;
  transform?: (value: string) => unknown;
}

export interface EntityLabels {
  // Translation keys (preferred)
  createdKey?: string;
  updatedKey?: string;
  deletedKey?: string;
  createErrorKey?: string;
  updateErrorKey?: string;
  deleteErrorKey?: string;
  deleteConfirmTitleKey?: string;
  deleteConfirmDescriptionKey?: string;
  // Hardcoded strings (fallback)
  created?: string;
  updated?: string;
  deleted?: string;
  createError?: string;
  updateError?: string;
  deleteError?: string;
  deleteConfirmTitle?: string;
  deleteConfirmDescription?: string;
}

export interface UseEntityOptions<TItem, TForm, TCreatePayload, TUpdatePayload> {
  // Entity identification
  entityName: string;

  // i18n namespace for translations
  translationNamespace?: string;

  // Query configuration
  queryKeyPrefix: keyof typeof queryKeys;
  listFn: (params: ListParams) => Promise<{ data?: unknown; error?: string }>;
  listDataKey?: string;

  // CRUD operations
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createFn?: (data: any) => Promise<ApiResponse<unknown>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  updateFn?: (id: number, data: any) => Promise<ApiResponse<unknown>>;
  deleteFn?: (id: number) => Promise<ApiResponse<unknown>>;

  // Form configuration
  defaultForm: TForm;

  // Mapping functions
  mapItem: (apiItem: unknown) => TItem;
  toCreatePayload: (form: TForm) => TCreatePayload;
  toUpdatePayload: (form: TForm) => TUpdatePayload;
  toForm: (item: TItem) => TForm;

  // UI configuration
  labels?: EntityLabels;

  // Pagination
  pageSize?: number;

  // Filters
  filters?: FilterConfig[];

  // Search
  searchable?: boolean;
  searchParamName?: string;

  // Sorting
  sortable?: boolean;
  sortFieldParam?: string;
  sortDirectionParam?: string;

  // Custom mutations factory
  customMutations?: (context: UseEntityContext<TItem, TForm>) => Record<string, UseMutationResult<unknown, Error, unknown, unknown>>;
}

export interface UseEntityContext<TItem, TForm> {
  selectedItem: TItem | null;
  formData: TForm;
  extendedState: Record<string, unknown>;
  setExtendedState: (updater: (prev: Record<string, unknown>) => Record<string, unknown>) => void;
  queryClient: ReturnType<typeof useQueryClient>;
  toast: (message: string, type: "success" | "error") => void;
  invalidate: () => void;
}

export interface UseEntityResult<TItem, TForm> {
  // Data
  items: TItem[];
  loading: boolean;
  totalCount: number;
  totalPages: number;

  // Pagination
  currentPage: number;
  setCurrentPage: (page: number | ((prev: number) => number)) => void;
  pageSize: number;
  setPageSize: (size: number) => void;

  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  debouncedSearch: string;

  // Filters
  filterValues: Record<string, string>;
  setFilterValue: (name: string, value: string) => void;
  resetFilters: () => void;

  // Sorting
  sortField: string | null;
  sortDirection: "asc" | "desc";
  toggleSort: (field: string) => void;
  setSort: (field: string, direction: "asc" | "desc") => void;
  clearSort: () => void;

  // Dialogs
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;

  // Selection
  selectedItem: TItem | null;
  setSelectedItem: (item: TItem | null) => void;

  // Form
  formData: TForm;
  setFormData: React.Dispatch<React.SetStateAction<TForm>>;
  updateFormField: <K extends keyof TForm>(field: K, value: TForm[K]) => void;
  resetForm: () => void;

  // Extended state (attachments, tasks, etc.)
  extendedState: Record<string, unknown>;
  setExtendedState: (updater: (prev: Record<string, unknown>) => Record<string, unknown>) => void;

  // CRUD handlers
  handleSubmit: () => void;
  handleDelete: (id: number) => Promise<void>;
  openEditDialog: (item: TItem) => void;

  // Direct mutation functions (for custom handling)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createFn?: (data: any) => Promise<ApiResponse<unknown>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  updateFn?: (id: number, data: any) => Promise<ApiResponse<unknown>>;
  deleteFn?: (id: number) => Promise<ApiResponse<unknown>>;

  // Loading states
  isSubmitting: boolean;
  isDeleting: boolean;

  // Custom mutations
  customMutations: Record<string, UseMutationResult<unknown, Error, unknown, unknown>>;

  // Utilities
  invalidate: () => void;
}

// ============================================================================
// Helper to safely get list query key
// ============================================================================

function getListQueryKey(prefix: keyof typeof queryKeys, params: ListParams) {
  const keyConfig = queryKeys[prefix];
  if ("list" in keyConfig && typeof keyConfig.list === "function") {
    return keyConfig.list(params);
  }
  return [prefix, "list", params];
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useEntity<TItem, TForm, TCreatePayload = unknown, TUpdatePayload = unknown>(
  options: UseEntityOptions<TItem, TForm, TCreatePayload, TUpdatePayload>,
): UseEntityResult<TItem, TForm> {
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
    mapItem,
    toCreatePayload,
    toUpdatePayload,
    toForm,
    labels = {},
    pageSize = 20,
    filters = [],
    searchable = true,
    searchParamName = "search",
    sortable = false,
    sortFieldParam = "sort_by",
    sortDirectionParam = "sort_order",
    customMutations: customMutationsConfig,
  } = options;

  // Initialize translations - always call hooks unconditionally
  const tNamespace = useTranslations((translationNamespace as import("./use-translations").Namespace) ?? "common");
  const tCommon = useTranslations("common");
  // Use the namespace translations if available, otherwise use common
  const t = translationNamespace ? tNamespace : tCommon;

  // Resolve label with i18n support (translation keys take precedence)
  const resolveLabel = useCallback((key: keyof EntityLabels, fallback: string): string => {
    // First try translation key - extract just the key part after the namespace
    const translationKey = labels[`${key}Key` as keyof EntityLabels] as string | undefined;
    if (translationKey && t) {
      // If key includes namespace prefix (e.g., "departments.created"), extract just "created"
      const keyParts = translationKey.split(".");
      const finalKey = keyParts.length > 1 ? keyParts[keyParts.length - 1] : translationKey;
      return t(finalKey) as string;
    }
    // Fall back to hardcoded string
    return labels[key] ?? fallback;
  }, [labels, t]);

  const created = resolveLabel("created", `${entityName}`);
  const updated = resolveLabel("updated", `${entityName}`);
  const deleted = resolveLabel("deleted", `${entityName}`);
  const createError = resolveLabel("createError", `${entityName}`);
  const updateError = resolveLabel("updateError", `${entityName}`);
  const deleteError = resolveLabel("deleteError", `${entityName}`);
  const deleteConfirmTitle = resolveLabel("deleteConfirmTitle", tCommon("deleteTitle") ?? "");
  const deleteConfirmDescription = resolveLabel("deleteConfirmDescription", tCommon("confirmDelete") ?? "");

  const { toast } = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();
  const { pageSize: globalPageSize, setPageSize: setGlobalPageSize } = usePaginationSettings();

  // Extended state for custom fields (attachments, tasks, etc.)
  // Initialize empty, will be populated by entity-specific hooks via setExtendedState
  const [extendedState, setExtendedStateState] = useState<Record<string, unknown>>({});

  const setExtendedState = useCallback(
    (updater: (prev: Record<string, unknown>) => Record<string, unknown>) => {
      setExtendedStateState((prev) => updater(prev));
    },
    [],
  );

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery);

  // Filter states
  const [filterValues, setFilterValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      initial[filter.name] = filter.defaultValue;
    }
    return initial;
  });

  // Sorting state
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  // Pagination state - use global settings
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSizeState, setPageSizeLocal] = useState(globalPageSize);

  // Sync with global page size changes
  const setPageSize = useCallback((size: number) => {
    setPageSizeLocal(size);
    setGlobalPageSize(size);
    setCurrentPage(1); // Reset to first page on page size change
  }, [setGlobalPageSize]);

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
      skip: (currentPage - 1) * pageSizeState,
      limit: pageSizeState,
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
  }, [currentPage, pageSizeState, searchable, debouncedSearch, searchParamName, filters, filterValues, sortable, sortField, sortDirection, sortFieldParam, sortDirectionParam]);

  // Query key
  const listQueryKey = useMemo(
    () => getListQueryKey(queryKeyPrefix, queryParams),
    [queryKeyPrefix, queryParams],
  );

  // List query
  const { data: listData, isLoading: loading } = useQuery({
    queryKey: listQueryKey,
    queryFn: () => listFn(queryParams),
    select: (result) => {
      if (!result.data) return undefined;

      // Handle case when API returns an array directly
      if (Array.isArray(result.data)) {
        return {
          items: result.data.map(mapItem),
          total: result.data.length,
          pages: 1,
        };
      }

      // Extract items using the specified key or default
      const data = result.data as Record<string, unknown>;
      const rawItems = (data[listDataKey] ?? data.items ?? []) as unknown[];

      return {
        items: rawItems.map(mapItem),
        total: (data.total as number | undefined) ?? 0,
        pages: (data.pages as number | undefined) ?? 1,
      };
    },
  });

  // Invalidate helper
  const invalidate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: getEntityListKey(queryKeyPrefix) });
  }, [queryClient, queryKeyPrefix]);

  // Internal reset form that doesn't depend on itself
  const resetFormInternal = useCallback(() => {
    setFormData({ ...defaultForm });
    setSelectedItem(null);
    setExtendedStateState({});
  }, [defaultForm]);

  // Create mutation
  const createMutation = useMutation<unknown, Error, TCreatePayload>({
    mutationFn: async (data) => {
      if (!createFn) throw new Error("createFn not provided");
      const result = await createFn(data);
      if (result.error) throw new Error(result.error);
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      setIsCreateDialogOpen(false);
      resetFormInternal();
      toast(created, "success");
    },
    onError: () => toast(createError, "error"),
  });

  // Update mutation
  const updateMutation = useMutation<unknown, Error, { id: number; data: TUpdatePayload }>({
    mutationFn: async ({ id, data }) => {
      if (!updateFn) throw new Error("updateFn not provided");
      const result = await updateFn(id, data);
      if (result.error) throw new Error(result.error);
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      setIsEditDialogOpen(false);
      setSelectedItem(null);
      toast(updated, "success");
    },
    onError: () => toast(updateError, "error"),
  });

  // Delete mutation
  const deleteMutation = useMutation<unknown, Error, number>({
    mutationFn: async (id) => {
      if (!deleteFn) throw new Error("deleteFn not provided");
      const result = await deleteFn(id);
      if (result.error) throw new Error(result.error);
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      toast(deleted, "success");
    },
    onError: () => toast(deleteError, "error"),
  });

  // Custom mutations - Note: These must be created by the caller using useMutation
  // and passed in options to avoid hook rule violations. We just pass them through.
  const customMutations = useMemo(() => {
    if (!customMutationsConfig) return {};
    // The factory should return mutation results, not create them
    // Caller must create mutations at top level, then pass config that returns them
    const context: UseEntityContext<TItem, TForm> = {
      selectedItem,
      formData,
      extendedState,
      setExtendedState,
      queryClient,
      toast,
      invalidate,
    };
    return customMutationsConfig(context);
  }, [customMutationsConfig, selectedItem, formData, extendedState, setExtendedState, queryClient, toast, invalidate]);

  // Handlers
  const updateFormField = useCallback(<K extends keyof TForm>(field: K, value: TForm[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData({ ...defaultForm });
    setSelectedItem(null);
    setExtendedStateState({});
  }, [defaultForm]);

  const resetFilters = useCallback(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      initial[filter.name] = filter.defaultValue;
    }
    setFilterValues(initial);
    setSearchQuery("");
    setCurrentPage(1);
  }, [filters]);

  const setFilterValue = useCallback((name: string, value: string) => {
    setFilterValues((prev) => ({ ...prev, [name]: value }));
    setCurrentPage(1); // Reset to first page on filter change
  }, []);

  // Sorting handlers
  const toggleSort = useCallback((field: string) => {
    if (sortField === field) {
      // Same column: toggle direction
      setSortDirection((currentDir) => (currentDir === "asc" ? "desc" : "asc"));
    } else {
      // Different column: reset to asc
      setSortField(field);
      setSortDirection("asc");
    }
  }, [sortField]);

  const setSort = useCallback((field: string, direction: "asc" | "desc") => {
    setSortField(field);
    setSortDirection(direction);
  }, []);

  const clearSort = useCallback(() => {
    setSortField(null);
    setSortDirection("asc");
  }, []);

  const handleSubmit = useCallback(() => {
    if (selectedItem) {
      const payload = toUpdatePayload(formData);
      updateMutation.mutate({ id: (selectedItem as Record<string, unknown>).id as number, data: payload });
    } else {
      const payload = toCreatePayload(formData);
      createMutation.mutate(payload);
    }
  }, [selectedItem, formData, toCreatePayload, toUpdatePayload, createMutation, updateMutation]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  // Derived values
  const items = listData?.items ?? [];
  const totalCount = listData?.total ?? 0;
  const totalPages = listData?.pages ?? 1;

  return {
    // Data
    items,
    loading,
    totalCount,
    totalPages,

    // Pagination
    currentPage,
    setCurrentPage,
    pageSize: pageSizeState,
    setPageSize,

    // Search
    searchQuery,
    setSearchQuery,
    debouncedSearch,

    // Filters
    filterValues,
    setFilterValue,
    resetFilters,

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
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    isDeleting: deleteMutation.isPending,

    // Custom mutations
    customMutations,

    // Sorting
    sortField,
    sortDirection,
    toggleSort,
    setSort,
    clearSort,

    // Utilities
    invalidate,
  };
}
