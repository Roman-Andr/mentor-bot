import { cn } from "@/shared/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import type { ColumnDef, EntityPageProps } from "./entity-page-types";
import { EntityPageActions } from "./entity-page-actions";

interface EntityPageTableProps<TItem, TForm> extends Pick<
  EntityPageProps<TItem, TForm>,
  | "items"
  | "totalItems"
  | "currentPage"
  | "pageSize"
  | "isLoading"
  | "searchQuery"
  | "onSearchChange"
  | "onPageChange"
  | "onPageSizeChange"
  | "columns"
  | "getItemKey"
  | "onRowClick"
  | "onEditOpen"
  | "onDelete"
  | "title"
  | "description"
  | "showSearch"
  | "searchPlaceholder"
  | "filters"
  | "additionalActions"
  | "createButtonLabel"
  | "onCreateOpen"
  | "sortField"
  | "sortDirection"
  | "onSort"
  | "emptyStateMessage"
  | "t"
> {
  renderMobileCard?: (item: TItem) => React.ReactNode;
  mobileBreakpoint?: "sm" | "md" | "lg" | "xl";
}

export function EntityPageTable<TItem, TForm>({
  items,
  totalItems,
  currentPage,
  pageSize,
  isLoading,
  searchQuery,
  onSearchChange,
  onPageChange,
  onPageSizeChange,
  columns,
  getItemKey,
  onRowClick,
  onEditOpen,
  onDelete,
  title,
  description,
  showSearch,
  searchPlaceholder,
  filters,
  additionalActions,
  createButtonLabel,
  onCreateOpen,
  sortField,
  sortDirection,
  onSort,
  emptyStateMessage,
  t,
  renderMobileCard,
  mobileBreakpoint = "md",
}: EntityPageTableProps<TItem, TForm>) {
  const totalPages = Math.ceil(totalItems / pageSize) || 1;

  const mobileView = renderMobileCard ? (
    <div className="space-y-3 p-4">
      {items.map((item) => (
        <div key={getItemKey(item)}>{renderMobileCard(item)}</div>
      ))}
    </div>
  ) : undefined;

  return (
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
      skeleton={<DataTableSkeleton columns={columns.length} rows={Math.min(pageSize, 8)} showHeader={false} />}
      header={
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold">{title}</h2>
            {description && (
              <p className="text-muted-foreground mt-1">{description}</p>
            )}
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-2">
            {showSearch && (
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => onSearchChange?.(e.target.value)}
                className="rounded border px-3 py-2 w-full sm:w-auto"
              />
            )}
            {filters}
            {additionalActions}
            <button
              onClick={onCreateOpen}
              className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center justify-center gap-2 rounded px-4 py-2 w-full sm:w-auto"
            >
              <span className="size-4">+</span>
              {createButtonLabel}
            </button>
          </div>
        </div>
      }
      mobileView={mobileView}
      mobileBreakpoint={mobileBreakpoint}
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
                sortDirection={sortDirection ?? "asc"}
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
          {items.map((item, idx) => (
            <TableRow
              key={getItemKey ? getItemKey(item) : idx}
              className={cn(
                "transition-colors",
                onRowClick && "cursor-pointer hover:bg-muted"
              )}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((column) => (
                <TableCell
                  key={`${getItemKey ? getItemKey(item) : idx}-${column.key}`}
                  className={column.cellClassName}
                >
                  {column.key === "actions"
                    ? <EntityPageActions item={item} onEdit={onEditOpen} onDelete={onDelete} t={t} />
                    : column.cell(item)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}
