"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/shared/components";
import type { DepartmentRow } from "@/shared/hooks/use-departments";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import type { SortDirection } from "@/shared/hooks/use-sorting";

interface DepartmentsTableProps {
  departments: DepartmentRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  onEdit: (department: DepartmentRow) => void;
  onDelete: (id: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

function DepartmentCard({
  department,
  onEdit,
  onDelete,
  t,
}: {
  department: DepartmentRow;
  onEdit: (department: DepartmentRow) => void;
  onDelete: (id: number) => void;
  t: (key: string) => string;
}) {
  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-muted/50"
      onClick={() => onEdit(department)}
    >
      <CardContent className="p-4">
        <div className="mb-3 min-w-0">
          <h3 className="truncate font-semibold">{department.name}</h3>
          <p className="mt-1 line-clamp-3 text-sm text-muted-foreground">
            {department.description || "—"}
          </p>
        </div>

        <div className="mb-3 text-xs text-muted-foreground">
          {t("common.created")}: {new Date(department.createdAt).toLocaleDateString()}
        </div>

        <div
          className="flex flex-col gap-2 border-t pt-3 sm:flex-row"
          onClick={(event) => event.stopPropagation()}
        >
          <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(department)}>
            {t("common.edit")}
          </Button>
          <Button size="sm" variant="destructive" onClick={() => onDelete(department.id)}>
            {t("common.delete")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function DepartmentsTable({
  departments,
  loading,
  searchQuery,
  onSearchChange,
  currentPage,
  totalPages,
  totalCount,
  sortField,
  sortDirection = "asc",
  onSort,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
}: DepartmentsTableProps) {
  const t = useTranslations();

  const mobileView = (
    <div className="space-y-3 p-4">
      {departments.map((department) => (
        <DepartmentCard
          key={department.id}
          department={department}
          onEdit={onEdit}
          onDelete={onDelete}
          t={t}
        />
      ))}
    </div>
  );

  return (
    <DataTable
      loading={loading}
      empty={departments.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      showPageSizeSelector={!!onPageSizeChange}
      skeleton={<DataTableSkeleton columns={4} rows={5} showHeader={false} />}
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{t("departments.title")}</CardTitle>
            <SearchInput
              placeholder={t("common.searchPlaceholder")}
              value={searchQuery}
              onChange={onSearchChange}
            />
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead
              field="name"
              sortable={!!onSort}
              sortField={sortField}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("departments.name")}
            </SortableTableHead>
            <TableHead>{t("common.description")}</TableHead>
            <SortableTableHead
              field="createdAt"
              sortable={!!onSort}
              sortField={sortField}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.created")}
            </SortableTableHead>
            <TableHead className="w-25">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {departments.map((department) => (
            <TableRow
              key={department.id}
              className="cursor-pointer transition-none hover:bg-muted"
              onClick={() => onEdit(department)}
            >
              <TableCell>
                <span className="font-medium">{department.name}</span>
              </TableCell>
              <TableCell className="max-w-75 truncate text-sm text-muted-foreground">
                {department.description || "—"}
              </TableCell>
              <TableCell>{new Date(department.createdAt).toLocaleDateString()}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(department), t("common.edit")),
                    buildDeleteAction(() => onDelete(department.id), t("common.delete")),
                  ]}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}
