import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
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
> {}

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
}: EntityPageTableProps<TItem, TForm>) {
  const totalPages = Math.ceil(totalItems / pageSize) || 1;

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
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">{title}</h2>
            {description && (
              <p className="text-muted-foreground mt-1">{description}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {showSearch && (
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="border rounded px-3 py-2"
              />
            )}
            {filters}
            {additionalActions}
            <button
              onClick={onCreateOpen}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              <span className="size-4">+</span>
              {createButtonLabel}
            </button>
          </div>
        </div>
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
                    ? <EntityPageActions item={item} onEdit={onEditOpen} onDelete={onDelete} />
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
