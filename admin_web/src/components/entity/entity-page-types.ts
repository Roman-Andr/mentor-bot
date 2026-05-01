import { ReactNode } from "react";

/** Column definition for the entity table */
export interface ColumnDef<TItem> {
  /** Unique key for the column */
  key: string;
  /** Header text or ReactNode */
  header: ReactNode;
  /** Cell renderer function */
  cell: (item: TItem) => ReactNode;
  /** Column width class (e.g., "w-24", "w-1/4") */
  width?: string;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Custom className for the header cell */
  headerClassName?: string;
  /** Custom className for body cells */
  cellClassName?: string;
}

/** Tab definition for tabbed pages */
export interface EntityPageTab {
  /** Tab ID */
  id: string;
  /** Tab label */
  label: string;
  /** Optional icon component */
  icon?: React.ComponentType<{ className?: string }>;
  /** Tab content - table or custom content */
  content: ReactNode;
}

export interface EntityPageProps<TItem, TForm> {
  // Page config
  /** Page title */
  title: string;
  /** Optional page description */
  description?: string;

  // Entity data from useEntity hook
  /** Array of items to display */
  items: TItem[];
  /** Total number of items (for pagination) */
  totalItems: number;
  /** Current page number (1-based) */
  currentPage: number;
  /** Number of items per page */
  pageSize: number;
  /** Whether data is loading */
  isLoading: boolean;

  // Dialog state
  /** Whether create dialog is open */
  isCreateOpen: boolean;
  /** Whether edit dialog is open */
  isEditOpen: boolean;
  /** Currently selected item for editing (available to parent for reference) */
  selectedItem: TItem | null;

  // Actions
  /** Callback to open create dialog */
  onCreateOpen: () => void;
  /** Callback to open edit dialog with item */
  onEditOpen: (item: TItem) => void;
  /** Callback to delete an item by ID (confirmation handled externally) */
  onDelete: (id: number) => void;
  /** Callback to close any dialog */
  onCloseDialog: () => void;

  // Form handling
  /** Current form data */
  formData: TForm;
  /** Callback when form data changes */
  onFormChange: (data: TForm) => void;
  /** Callback when form is submitted */
  onSubmit: () => void;
  /** Whether form is submitting */
  isSubmitting: boolean;
  /** Form submission error message */
  submitError: string | null;

  // Search & pagination
  /** Current search query */
  searchQuery: string;
  /** Callback when search query changes */
  onSearchChange: (value: string) => void;
  /** Callback when page changes */
  onPageChange: (page: number) => void;
  /** Optional callback when page size changes */
  onPageSizeChange?: (size: number) => void;

  // Renderers
  /** Table column definitions */
  columns: ColumnDef<TItem>[];
  /** Form renderer function */
  renderForm: (props: {
    formData: TForm;
    onChange: (data: TForm) => void;
    mode: "create" | "edit";
  }) => ReactNode;

  // Optional
  /** Label for create button (default: uses translation) */
  createButtonLabel?: string;
  /** Label for edit button (default: uses translation) */
  editButtonLabel?: string;
  /** Message shown when no items (default: uses translation) */
  emptyStateMessage?: string;
  /** Tabs for tabbed interface */
  tabs?: EntityPageTab[];
  /** Active tab ID (when tabs are provided) */
  activeTab?: string;
  /** Callback when tab changes */
  onTabChange?: (tabId: string) => void;
  /** Additional filter UI */
  filters?: ReactNode;
  /** Additional actions in the header */
  additionalActions?: ReactNode;
  /** Custom className for the table container */
  className?: string;
  /** Unique key accessor for table rows */
  getItemKey: (item: TItem) => string | number;
  /** Callback when a row is clicked */
  onRowClick?: (item: TItem) => void;
  /** Whether to show the search input */
  showSearch?: boolean;
  /** Placeholder text for search input */
  searchPlaceholder?: string;
  /** Whether the form is valid (controls submit button) */
  isFormValid?: boolean;
  /** Maximum width for dialogs */
  dialogMaxWidth?: string;
  /** Current sort field */
  sortField?: string | null;
  /** Current sort direction */
  sortDirection?: import("@/hooks/use-sorting").SortDirection;
  /** Callback when a column header is clicked for sorting */
  onSort?: (field: string) => void;
  /** Translation function for i18n */
  t: (key: string) => string;
}
