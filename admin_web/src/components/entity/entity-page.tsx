"use client";

import { ReactNode } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TabSwitcher } from "@/components/ui/tab-switcher";
import { EntityFormDialog } from "./entity-form-dialog";
import { Plus, Trash2, SquarePen } from "lucide-react";
import { cn } from "@/lib/utils";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import type { SortDirection } from "@/hooks/use-sorting";

// ============================================================================
// Types
// ============================================================================

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
  sortDirection?: SortDirection;
  /** Callback when a column header is clicked for sorting */
  onSort?: (field: string) => void;
}

// ============================================================================
// Component
// ============================================================================

/**
 * Generic, reusable CRUD page template for entity management.
 * Supports listing, searching, pagination, create/edit dialogs, and deletion.
 * 
 * @example
 * ```tsx
 * <EntityPage
 *   title="Departments"
 *   items={departments}
 *   totalItems={totalCount}
 *   currentPage={page}
 *   pageSize={10}
 *   isLoading={loading}
 *   isCreateOpen={isCreateOpen}
 *   isEditOpen={isEditOpen}
 *   selectedItem={selectedDepartment}
 *   onCreateOpen={() => setIsCreateOpen(true)}
 *   onEditOpen={(dept) => { setSelectedDepartment(dept); setIsEditOpen(true); }}
 *   onDelete={handleDelete}
 *   onCloseDialog={() => { setIsCreateOpen(false); setIsEditOpen(false); }}
 *   formData={formData}
 *   onFormChange={setFormData}
 *   onSubmit={handleSubmit}
 *   isSubmitting={isPending}
 *   submitError={error}
 *   searchQuery={search}
 *   onSearchChange={setSearch}
 *   onPageChange={setPage}
 *   getItemKey={(item) => item.id}
 *   columns={[
 *     { key: "name", header: "Name", cell: (d) => d.name },
 *     { key: "actions", header: "Actions", cell: (d) => <ActionButtons item={d} /> }
 *   ]}
 *   renderForm={({ formData, onChange }) => (
 *     <Input 
 *       value={formData.name} 
 *       onChange={(e) => onChange({ ...formData, name: e.target.value })} 
 *     />
 *   )}
 * />
 * ```
 */
export function EntityPage<TItem, TForm>({
  // Page config
  title,
  description,

  // Entity data
  items,
  totalItems,
  currentPage,
  pageSize,
  isLoading,

  // Dialog state
  isCreateOpen,
  isEditOpen,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  selectedItem,

  // Actions
  onCreateOpen,
  onEditOpen,
  onDelete,
  onCloseDialog,

  // Form handling
  formData,
  onFormChange,
  onSubmit,
  isSubmitting,
  submitError,

  // Search & pagination
  searchQuery,
  onSearchChange,
  onPageChange,
  onPageSizeChange,

  // Renderers
  columns,
  renderForm,

  // Optional
  createButtonLabel,
  emptyStateMessage,
  tabs,
  activeTab,
  onTabChange,
  filters,
  additionalActions,
  className,
  getItemKey,
  onRowClick,
  showSearch = true,
  searchPlaceholder,
  isFormValid = true,
  dialogMaxWidth = "max-w-lg",
  sortField,
  sortDirection = "asc",
  onSort,
}: EntityPageProps<TItem, TForm>) {
  const t = useTranslations();

  const totalPages = Math.ceil(totalItems / pageSize) || 1;

  // Render action buttons for a row
  const renderActionButtons = (item: TItem) => {
    const id = (item as Record<string, unknown>).id as number;
    return (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onEditOpen(item)}
          title={t("common.edit")}
        >
          <SquarePen className="size-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="text-destructive hover:text-destructive"
          onClick={() => onDelete(id)}
          title={t("common.delete")}
        >
          <Trash2 className="size-4" />
        </Button>
      </div>
    );
  };

  // Render the table content
  const renderTable = () => (
    <DataTable
      loading={isLoading}
      empty={items.length === 0}
      emptyMessage={emptyStateMessage}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalItems}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      showPageSizeSelector={!!onPageSizeChange}
      header={
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <div>
              <CardTitle>{title}</CardTitle>
              {description && (
                <CardDescription className="mt-1">{description}</CardDescription>
              )}
            </div>
            <div className="flex items-center gap-2">
              {showSearch && (
                <SearchInput
                  placeholder={searchPlaceholder}
                  value={searchQuery}
                  onChange={onSearchChange}
                />
              )}
              {filters}
              {additionalActions}
              <Button onClick={onCreateOpen} className="gap-2">
                <Plus className="size-4" />
                {createButtonLabel || t("common.create")}
              </Button>
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <SortableTableHead
                key={column.key}
                field={column.key}
                sortable={column.sortable && !!onSort}
                sortField={sortField ?? null}
                sortDirection={sortDirection}
                onSort={onSort ?? (() => {})}
                className={column.headerClassName}
                width={column.width}
              >
                {column.header}
              </SortableTableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => (
            <TableRow
              key={getItemKey(item)}
              className={cn(
                "transition-colors",
                onRowClick && "cursor-pointer hover:bg-muted"
              )}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((column) => (
                <TableCell
                  key={`${getItemKey(item)}-${column.key}`}
                  className={column.cellClassName}
                >
                  {column.key === "actions"
                    ? renderActionButtons(item)
                    : column.cell(item)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );

  // Render tabs if provided
  const renderTabs = () => {
    if (!tabs || tabs.length === 0) return null;

    const tabItems = tabs.map((tab) => ({
      id: tab.id,
      label: tab.label,
      icon: tab.icon,
    }));

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <TabSwitcher
            tabs={tabItems}
            activeTab={activeTab || tabs[0].id}
            onTabChange={onTabChange || (() => {})}
          />
          <Button onClick={onCreateOpen} className="gap-2">
            <Plus className="size-4" />
            {createButtonLabel || t("common.create")}
          </Button>
        </div>
        {tabs.find((t) => t.id === (activeTab || tabs[0].id))?.content}
      </div>
    );
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Create Dialog */}
      <EntityFormDialog
        isOpen={isCreateOpen}
        onClose={onCloseDialog}
        onSubmit={onSubmit}
        title={`${t("common.create")} ${title}`}
        submitLabel={t("common.create")}
        cancelLabel={t("common.cancel")}
        isSubmitting={isSubmitting}
        error={submitError}
        isValid={isFormValid}
        formData={formData}
        maxWidth={dialogMaxWidth}
      >
        {renderForm({
          formData,
          onChange: onFormChange,
          mode: "create",
        })}
      </EntityFormDialog>

      {/* Edit Dialog */}
      <EntityFormDialog
        isOpen={isEditOpen}
        onClose={onCloseDialog}
        onSubmit={onSubmit}
        title={`${t("common.edit")} ${title}`}
        submitLabel={t("common.save")}
        cancelLabel={t("common.cancel")}
        isSubmitting={isSubmitting}
        error={submitError}
        isValid={isFormValid}
        formData={formData}
        maxWidth={dialogMaxWidth}
      >
        {renderForm({
          formData,
          onChange: onFormChange,
          mode: "edit",
        })}
      </EntityFormDialog>

      {/* Main Content */}
      {tabs ? renderTabs() : renderTable()}
    </div>
  );
}

/**
 * Loading skeleton for EntityPage
 */
export function EntityPageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="bg-muted h-8 w-48 animate-pulse rounded" />
          <div className="bg-muted h-4 w-72 animate-pulse rounded" />
        </div>
        <div className="bg-muted h-10 w-32 animate-pulse rounded" />
      </div>
      <div className="rounded-xl border">
        <div className="p-6">
          <div className="bg-muted h-6 w-full animate-pulse rounded" />
        </div>
        <div className="space-y-2 p-6 pt-0">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-muted h-12 w-full animate-pulse rounded" />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Empty state for EntityPage
 */
export function EntityPageEmpty({
  message,
  action,
}: {
  message: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <p className="text-muted-foreground mb-4">{message}</p>
      {action}
    </div>
  );
}
