"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { SearchInput } from "@/components/ui/search-input";
import { StatusBadge } from "@/components/ui/status-badge";
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
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/components/shared";
import { Calendar, CheckCircle } from "lucide-react";
import { getTemplateStatusOptions } from "@/lib/constants";
import type { TemplateItem } from "@/hooks/use-templates";
import type { SortDirection } from "@/hooks/use-sorting";

interface TemplatesTableProps {
  templates: TemplateItem[];
  loading: boolean;
  onEdit: (template: TemplateItem) => void;
  onPublish: (id: number) => void;
  onDelete: (id: number) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  onReset: () => void;
  currentPage?: number;
  totalPages?: number;
  totalCount?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

export function TemplatesTable({
  templates,
  loading,
  onEdit,
  onPublish,
  onDelete,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  onReset,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortField,
  sortDirection = "asc",
  onSort,
}: TemplatesTableProps) {
  const t = useTranslations();

  const statusOptions = getTemplateStatusOptions(t, true);

  return (
    <DataTable
      loading={loading}
      empty={templates.length === 0}
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
              {t("templates.title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? templates.length})
              </span>
            </CardTitle>
            <div className="flex gap-2">
              <SearchInput value={searchQuery} onChange={onSearchChange} />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
              />
              <Button variant="outline" onClick={onReset}>
                {t("common.reset")}
              </Button>
            </div>
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
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.name")}
            </SortableTableHead>
            <SortableTableHead
              field="department"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.department")}
            </SortableTableHead>
            <SortableTableHead
              field="position"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.position")}
            </SortableTableHead>
            <SortableTableHead
              field="durationDays"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.days")}
            </SortableTableHead>
            <SortableTableHead
              field="tasks"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.tasks")}
            </SortableTableHead>
            <SortableTableHead
              field="status"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.status")}
            </SortableTableHead>
            <TableHead className="w-25">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow
              key={template.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(template)}
            >
              <TableCell>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{template.name}</p>
                    {template.isDefault && (
                      <Badge variant="secondary" className="text-xs">
                        {t("templates.default")}
                      </Badge>
                    )}
                  </div>
                  <p className="text-muted-foreground text-sm">{template.description}</p>
                </div>
              </TableCell>
              <TableCell>{template.department}</TableCell>
              <TableCell>{template.position}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Calendar className="text-muted-foreground size-4" />
                  {template.durationDays}
                </div>
              </TableCell>
              <TableCell>{template.taskCount}</TableCell>
              <TableCell>
                <StatusBadge status={template.status} />
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(template), t("common.edit")),
                    ...(template.status === "DRAFT"
                      ? [{
                          icon: CheckCircle,
                          label: t("templates.publish"),
                          onClick: () => onPublish(template.id),
                          variant: "ghost" as const,
                          color: "text-green-500",
                        }]
                      : []
                    ),
                    buildDeleteAction(() => onDelete(template.id), t("common.delete")),
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