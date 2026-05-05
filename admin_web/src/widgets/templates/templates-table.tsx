"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { Select } from "@/shared/ui/select";
import { SearchInput } from "@/shared/ui/search-input";
import { StatusBadge } from "@/shared/ui/status-badge";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle } from "@/shared/ui/card";
import { TableActions, buildEditAction, buildDeleteAction, buildPublishAction } from "@/shared/components";
import type { ActionDefinition } from "@/shared/components/table-actions";
import { Calendar, Copy, ListTodo, Building2 } from "lucide-react";
import { getTemplateStatusOptions } from "@/shared/lib/constants";
import type { TemplateItem } from "@/shared/hooks/use-templates";
import type { SortDirection } from "@/shared/hooks/use-sorting";
import { cn } from "@/shared/lib/utils";

interface TemplatesTableProps {
  templates: TemplateItem[];
  loading: boolean;
  onEdit: (template: TemplateItem) => void;
  onPublish: (id: number) => void;
  onDelete: (id: number) => void;
  onClone?: (id: number) => void;
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
  onClone,
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
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>
              {t("templates.checklistTemplates")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? templates.length})
              </span>
            </CardTitle>
            <div className="flex flex-wrap gap-2">
              <SearchInput value={searchQuery} onChange={onSearchChange} />
              <Select value={statusFilter} onChange={onStatusFilterChange} options={statusOptions} />
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
            <SortableTableHead field="name" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.name")}
            </SortableTableHead>
            <SortableTableHead field="department" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.department")}
            </SortableTableHead>
            <SortableTableHead field="position" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.position")}
            </SortableTableHead>
            <SortableTableHead field="durationDays" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.days")}
            </SortableTableHead>
            <SortableTableHead field="tasks" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.tasks")}
            </SortableTableHead>
            <SortableTableHead field="status" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.status")}
            </SortableTableHead>
            <TableHead className="w-32">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow
              key={template.id}
              className="hover:bg-muted cursor-pointer transition-colors"
              onClick={() => onEdit(template)}
            >
              <TableCell>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{template.name}</p>
                    {template.isDefault && (
                      <Badge variant="secondary" className="text-xs">
                        {t("templates.default")}
                      </Badge>
                    )}
                  </div>
                  {template.description && (
                    <p className="text-muted-foreground line-clamp-1 text-xs">{template.description}</p>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <Building2 className="text-muted-foreground size-3.5" />
                  <span className="text-sm">{template.department || "—"}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{template.position || "—"}</span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <Calendar className="text-muted-foreground size-3.5" />
                  {template.durationDays}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <ListTodo className="text-muted-foreground size-3.5" />
                  <span className={cn(template.taskCount === 0 && "text-muted-foreground")}>{template.taskCount}</span>
                </div>
              </TableCell>
              <TableCell>
                <StatusBadge status={template.status} />
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(template), t("common.edit")),
                    buildPublishAction(
                      () => onPublish(template.id),
                      template.status === "DRAFT" ? t("templates.publish") : t("templates.unpublish"),
                      true,
                    ),
                    ...(onClone ? [{
                      type: "toggle" as const,
                      icon: Copy,
                      label: t("templates.clone") || "Clone",
                      onClick: () => onClone(template.id),
                      variant: "ghost" as const,
                      color: "text-blue-500",
                      show: true,
                    } as ActionDefinition] : []),
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
