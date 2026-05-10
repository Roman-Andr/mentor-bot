"use client";

import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/shared/components";
import { cn } from "@/shared/lib/utils";
import { useTranslations } from "@/shared/hooks/use-translations";
import type { CategoryRow } from "@/shared/hooks/use-categories";
import type { SortDirection } from "@/shared/hooks/use-sorting";
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
  const tCommon = useTranslations();
  const tKnowledge = useTranslations("knowledge");

  const columns = useCategoriesColumns(tCommon, tKnowledge);

  function CategoryCard({
    category,
    onEdit,
    onDelete,
    tCommon,
  }: {
    category: CategoryRow;
    onEdit: (category: CategoryRow) => void;
    onDelete: (id: number) => void;
    tCommon: (key: string) => string;
  }) {
    return (
      <Card
        className={cn(
          "cursor-pointer transition-colors hover:bg-muted/50",
          category.parent_id && "bg-muted/50",
        )}
        onClick={() => onEdit(category)}
      >
        <CardContent className="p-4">
          {/* Header: Name */}
          <div className="mb-3">
            <div className="flex items-center gap-2">
              <h3 className="truncate font-semibold">{category.name}</h3>
              {category.parent_id && (
                <span className="text-xs text-muted-foreground">
                  ({tKnowledge("parent")}: {category.parent_name})
                </span>
              )}
            </div>
            {category.description && (
              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                {category.description}
              </p>
            )}
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">{tKnowledge("articles")}: </span>
              <span>{category.articles_count}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{tKnowledge("subcategories")}: </span>
              <span>{category.children_count}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(category)}>
              {tCommon("common.edit")}
            </Button>
            <Button size="sm" variant="destructive" onClick={() => onDelete(category.id)}>
              {tCommon("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mobileView = (
    <div className="space-y-3 p-4">
      {categories.map((category) => (
        <CategoryCard
          key={category.id}
          category={category}
          onEdit={onEdit}
          onDelete={onDelete}
          tCommon={tCommon}
        />
      ))}
    </div>
  );

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
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
              {totalCountLabel ?? tKnowledge("categories")}{" "}
              <span className="text-sm font-normal text-muted-foreground">
                ({totalCount ?? categories.length})
              </span>
            </CardTitle>
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <SearchInput
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
              <Button variant="outline" onClick={onResetFilters} className="w-full sm:w-auto">
                {tCommon("common.reset")}
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
              className={cn("cursor-pointer", category.parent_id && "bg-muted/50")}
              onClick={() => onEdit(category)}
            >
              {columns.map((col) => (
                <TableCell key={col.key}>
                  {col.key === "actions" ? (
                    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                      <TableActions
                        actions={[
                          buildEditAction(() => onEdit(category), tCommon("common.edit")),
                          buildDeleteAction(() => onDelete(category.id), tCommon("common.delete")),
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
