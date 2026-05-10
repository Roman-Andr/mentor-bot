"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { Select } from "@/shared/ui/select";
import { SearchInput } from "@/shared/ui/search-input";
import { StatusBadge } from "@/shared/ui/status-badge";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import {
  TableActions,
  buildEditAction,
  buildDeleteAction,
  buildPublishAction,
} from "@/shared/components";
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

  function TemplateCard({
    template,
    onEdit,
    onPublish,
    onDelete,
    onClone,
    t,
  }: {
    template: TemplateItem;
    onEdit: (template: TemplateItem) => void;
    onPublish: (id: number) => void;
    onDelete: (id: number) => void;
    onClone?: (id: number) => void;
    t: (key: string) => string;
  }) {
    return (
      <Card
        className="cursor-pointer transition-colors hover:bg-muted/50"
        onClick={() => onEdit(template)}
      >
        <CardContent className="p-4">
          {/* Header: Name + Default Badge + Status */}
          <div className="mb-3">
            <div className="flex items-center gap-2">
              <h3 className="truncate font-semibold">{template.name}</h3>
              {template.isDefault && (
                <Badge variant="secondary" className="shrink-0 text-xs">
                  {t("templates.default")}
                </Badge>
              )}
              <StatusBadge status={template.status} />
            </div>
            {template.description && (
              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                {template.description}
              </p>
            )}
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-1.5">
              <Building2 className="size-3.5 shrink-0 text-muted-foreground" />
              <span className="text-muted-foreground">{t("common.department")}: </span>
              <span className="truncate">{template.department || "—"}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("common.position")}: </span>
              <span>{template.position || "—"}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="size-3.5 shrink-0 text-muted-foreground" />
              <span className="text-muted-foreground">{t("common.days")}: </span>
              <span>{template.durationDays}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <ListTodo className="size-3.5 shrink-0 text-muted-foreground" />
              <span className="text-muted-foreground">{t("common.tasks")}: </span>
              <span className={cn(template.taskCount === 0 && "text-muted-foreground")}>
                {template.taskCount}
              </span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(template)}>
              {t("common.edit")}
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              onClick={() => onPublish(template.id)}
            >
              {template.status === "DRAFT" ? t("templates.publish") : t("templates.unpublish")}
            </Button>
            {onClone && (
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={() => onClone(template.id)}
              >
                <Copy className="size-3.5" />
              </Button>
            )}
            <Button size="sm" variant="destructive" onClick={() => onDelete(template.id)}>
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mobileView = (
    <div className="space-y-3 p-4">
      {templates.map((template) => (
        <TemplateCard
          key={template.id}
          template={template}
          onEdit={onEdit}
          onPublish={onPublish}
          onDelete={onDelete}
          onClone={onClone}
          t={t}
        />
      ))}
    </div>
  );

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
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
              {t("templates.checklistTemplates")}{" "}
              <span className="text-sm font-normal text-muted-foreground">
                ({totalCount ?? templates.length})
              </span>
            </CardTitle>
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <SearchInput
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
                className="w-full sm:w-auto"
              />
              <Button variant="outline" onClick={onReset} className="w-full sm:w-auto">
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
            <TableHead className="w-32">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow
              key={template.id}
              className="cursor-pointer transition-colors hover:bg-muted"
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
                    <p className="line-clamp-1 text-xs text-muted-foreground">
                      {template.description}
                    </p>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <Building2 className="size-3.5 text-muted-foreground" />
                  <span className="text-sm">{template.department || "—"}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{template.position || "—"}</span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <Calendar className="size-3.5 text-muted-foreground" />
                  {template.durationDays}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <ListTodo className="size-3.5 text-muted-foreground" />
                  <span className={cn(template.taskCount === 0 && "text-muted-foreground")}>
                    {template.taskCount}
                  </span>
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
                      template.status === "DRAFT"
                        ? t("templates.publish")
                        : t("templates.unpublish"),
                      true,
                    ),
                    ...(onClone
                      ? [
                          {
                            type: "toggle" as const,
                            icon: Copy,
                            label: t("templates.clone") || "Clone",
                            onClick: () => onClone(template.id),
                            variant: "ghost" as const,
                            color: "text-blue-500",
                            show: true,
                          } as ActionDefinition,
                        ]
                      : []),
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
