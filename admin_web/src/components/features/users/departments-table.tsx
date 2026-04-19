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
import { Trash2, SquarePen } from "lucide-react";
import type { DepartmentRow } from "@/hooks/use-departments";

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
}

export function DepartmentsTable({
  departments,
  loading,
  searchQuery,
  onSearchChange,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
}: DepartmentsTableProps) {
  const t = useTranslations();

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
            <TableHead>{t("departments.name")}</TableHead>
            <TableHead>{t("common.description")}</TableHead>
            <TableHead>{t("common.created")}</TableHead>
            <TableHead className="w-25">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {departments.map((department) => (
            <TableRow
              key={department.id}
              className="hover:bg-muted cursor-pointer"
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
                <div className="flex gap-1">
                   <Button variant="ghost" size="icon" onClick={() => onEdit(department)} aria-label={t("common.edit")}>
                     <SquarePen className="size-4" />
                   </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(department.id)}
                    aria-label={t("common.delete")}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}