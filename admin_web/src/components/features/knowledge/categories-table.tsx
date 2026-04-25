"use client";

import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/components/shared";
import { cn } from "@/lib/utils";
import type { CategoryRow } from "@/hooks/use-categories";
import type { SortDirection } from "@/hooks/use-sorting";
import { useCategoriesColumns } from "./categories-table-columns";

interface CategoriesTableProps {
  categories: CategoryRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onResetFilters: () => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  onEdit: (category: CategoryRow) => void;
  onDelete: (id: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
  totalCountLabel?: string;
}

export function CategoriesTable({
  categories,
  loading,
  searchQuery,
  onSearchChange,
  onResetFilters,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
  sortField,
  sortDirection,
  onSort,
  totalCountLabel,
}: CategoriesTableProps) {
  const tCommon = (key: string) => key; // Simplified, should use useTranslations
  const tKnowledge = (key: string) => key; // Simplified, should use useTranslations

  const columns = useCategoriesColumns(tCommon, tKnowledge);

  return (
    <DataTable
      loading={loading}
      empty={categories.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      showPageSizeSelector={!!onPageSizeChange}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {totalCountLabel ?? "Categories"}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? categories.length})
              </span>
            </CardTitle>
            <div className="flex gap-2">
              <SearchInput value={searchQuery} onChange={onSearchChange} />
              <Button variant="outline" onClick={onResetFilters}>
                Reset
              </Button>
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <SortableTableHead
                key={col.key}
                field={col.key}
                sortable={col.sortable}
                sortField={sortField ?? null}
                sortDirection={sortDirection ?? "asc"}
                onSort={onSort ?? (() => {})}
                width={col.width}
              >
                {col.title}
              </SortableTableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {categories.map((category) => (
            <TableRow
              key={category.id}
              className={cn(
                "cursor-pointer",
                category.parent_id && "bg-muted/50"
              )}
              onClick={() => onEdit(category)}
            >
              {columns.map((col) => (
                <TableCell key={col.key}>
                  {col.key === "actions" ? (
                    <div
                      className="flex gap-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <TableActions
                        actions={[
                          buildEditAction(() => onEdit(category)),
                          buildDeleteAction(() => onDelete(category.id)),
                        ]}
                      />
                    </div>
                  ) : (
                    col.render(category)
                  )}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}