"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/components/shared";
import type { DepartmentRow } from "@/hooks/use-departments";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import type { SortDirection } from "@/hooks/use-sorting";

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

  return (
    <DataTable
      loading={false}
      empty={departments.length === 0}
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
            <CardTitle>{t("departments.title")}</CardTitle>
            <SearchInput placeholder={t("common.searchPlaceholder")} value={searchQuery} onChange={onSearchChange} />
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
              className="hover:bg-muted cursor-pointer transition-none"
              onClick={() => onEdit(department)}
            >
              <TableCell>
                <span className="font-medium">{department.name}</span>
              </TableCell>
              <TableCell className="text-muted-foreground max-w-75 truncate text-sm">
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