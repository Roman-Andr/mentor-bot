import type { UseMutationResult } from "@tanstack/react-query";
import type { ListParams } from "../use-queries";

export interface EntityListResponse<T = unknown> {
  items?: T[];
  total?: number;
  pages?: number;
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

export interface UseEntityOptions<TItem, TForm, TCreatePayload, TUpdatePayload, TExtendedState = Record<string, unknown>> {
  // Entity identification
  entityName: string;

  // i18n namespace for translations
  translationNamespace?: string;

  // Query configuration
  queryKeyPrefix: keyof typeof import("@/lib/query-keys").queryKeys;
  listFn: (params: ListParams) => Promise<import("@/lib/api/client").ApiResult<unknown>>;
  listDataKey?: string;

  // CRUD operations
  createFn?: (data: TCreatePayload) => Promise<import("@/lib/api/client").ApiResult<unknown>>;
  updateFn?: (id: number, data: TUpdatePayload) => Promise<import("@/lib/api/client").ApiResult<unknown>>;
  deleteFn?: (id: number) => Promise<import("@/lib/api/client").ApiResult<unknown>>;

  // Form configuration
  defaultForm: TForm;
  defaultExtendedState?: TExtendedState;

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
  customMutations?: (context: UseEntityContext<TItem, TForm, TExtendedState>) => Record<string, UseMutationResult<unknown, Error, unknown, unknown>>;

  // Lifecycle hooks for side effects after mutations
  onAfterCreate?: (data: unknown, context: UseEntityContext<TItem, TForm, TExtendedState>) => void | Promise<void>;
  onAfterUpdate?: (data: unknown, context: UseEntityContext<TItem, TForm, TExtendedState>) => void | Promise<void>;

  // i18n: translation key for entity labels (e.g., "entities.users.singular")
  entityLabelKey?: string;
}

export interface UseEntityContext<TItem, TForm, TExtendedState = Record<string, unknown>> {
  selectedItem: TItem | null;
  formData: TForm;
  extendedState: TExtendedState;
  setExtendedState: (updater: (prev: TExtendedState) => TExtendedState) => void;
  queryClient: import("@tanstack/react-query").QueryClient;
  toast: (message: string, type: "success" | "error") => void;
  invalidate: () => void;
}

export interface UseEntityResult<TItem, TForm, TCreatePayload = unknown, TUpdatePayload = unknown, TExtendedState = Record<string, unknown>> {
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
  extendedState: TExtendedState;
  setExtendedState: (updater: (prev: TExtendedState) => TExtendedState) => void;

  // CRUD handlers
  handleSubmit: () => void;
  handleDelete: (id: number) => Promise<void>;
  openEditDialog: (item: TItem) => void;

  // Direct mutation functions (for custom handling)
  createFn?: (data: TCreatePayload) => Promise<import("@/lib/api/client").ApiResult<unknown>>;
  updateFn?: (id: number, data: TUpdatePayload) => Promise<import("@/lib/api/client").ApiResult<unknown>>;
  deleteFn?: (id: number) => Promise<import("@/lib/api/client").ApiResult<unknown>>;

  // Loading states
  isSubmitting: boolean;
  isDeleting: boolean;

  // Custom mutations
  customMutations: Record<string, UseMutationResult<unknown, Error, unknown, unknown>>;

  // Utilities
  invalidate: () => void;
}
