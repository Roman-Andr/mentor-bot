"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { DataTable } from "@/shared/ui/data-table";
import { StatusBadge } from "@/shared/ui/status-badge";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import {
  TableActions,
  buildEditAction,
  buildDeleteAction,
  buildCompleteAction,
} from "@/shared/components";
import { UserAvatar } from "@/shared/ui/user-avatar";
import { AlertTriangle, Clock, Filter } from "lucide-react";
import { getChecklistStatusOptions } from "@/shared/lib/constants";
import { formatDate } from "@/shared/lib/utils";
import type { ChecklistItem } from "@/shared/hooks/use-checklists";
import type { SortDirection } from "@/shared/hooks/use-sorting";
import { CertificateButton } from "@/widgets/certificates/certificate-button";
import { cn } from "@/shared/lib/utils";
import { useState } from "react";

interface ChecklistsTableProps {
  checklists: ChecklistItem[];
  loading: boolean;
  onEdit: (checklist: ChecklistItem) => void;
  onComplete: (id: number) => void;
  onDelete: (id: number) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  departmentFilter: string;
  onDepartmentFilterChange: (dept: string) => void;
  onReset: () => void;
  departments?: { id: number; name: string }[];
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

function ProgressBar({
  value,
  isOverdue,
  completed,
}: {
  value: number;
  isOverdue: boolean;
  completed: boolean;
}) {
  const color = completed
    ? "bg-emerald-500"
    : isOverdue
      ? "bg-red-500"
      : value > 50
        ? "bg-blue-500"
        : "bg-amber-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full transition-all", color)}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
      <span className="w-9 shrink-0 text-right text-xs text-muted-foreground">{value}%</span>
    </div>
  );
}

function ChecklistStatusBadge({ status, isOverdue }: { status: string; isOverdue: boolean }) {
  const t = useTranslations();
  if (isOverdue) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-red-200 bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700 dark:border-red-800 dark:bg-red-950/50 dark:text-red-400">
        <Clock className="size-3" />
        {t("checklists.overdue")}
      </span>
    );
  }
  return <StatusBadge status={status} />;
}

function ChecklistCard({
  checklist,
  onEdit,
  onComplete,
  onDelete,
  t,
}: {
  checklist: ChecklistItem;
  onEdit: (checklist: ChecklistItem) => void;
  onComplete: (id: number) => void;
  onDelete: (id: number) => void;
  t: (key: string) => string;
}) {
  return (
    <Card
      className={cn(
        "cursor-pointer transition-colors hover:bg-muted/50",
        checklist.isOverdue && "border-l-4 border-l-red-500",
      )}
      onClick={() => onEdit(checklist)}
    >
      <CardContent className="p-4">
        {/* Header: User + Status */}
        <div className="mb-3 flex items-start gap-3">
          <UserAvatar name={checklist.userName} id={checklist.id} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3 className="truncate font-semibold">{checklist.userName}</h3>
              <ChecklistStatusBadge status={checklist.status} isOverdue={checklist.isOverdue} />
            </div>
            <p className="text-xs text-muted-foreground">{checklist.employeeId}</p>
            {checklist.notes && (
              <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{checklist.notes}</p>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-3">
          <ProgressBar
            value={checklist.progressPercentage}
            isOverdue={checklist.isOverdue}
            completed={checklist.status === "COMPLETED"}
          />
        </div>

        {/* Metadata */}
        <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-muted-foreground">{t("checklists.tasks")}: </span>
            <span>
              {checklist.completedTasks}/{checklist.totalTasks}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("checklists.startDate")}: </span>
            <span>{formatDate(checklist.startDate)}</span>
          </div>
          <div className="col-span-2">
            <span className="text-muted-foreground">{t("checklists.dueDate")}: </span>
            <div className="flex items-center gap-1">
              {checklist.isOverdue && <AlertTriangle className="size-3 text-red-500" />}
              <span className={cn(checklist.isOverdue && "text-red-600 dark:text-red-400")}>
                {formatDate(checklist.dueDate)}
              </span>
              {checklist.daysRemaining !== null && checklist.status !== "COMPLETED" && (
                <span
                  className={cn(
                    checklist.daysRemaining < 0 ? "text-red-500" : "text-muted-foreground",
                  )}
                >
                  (
                  {checklist.daysRemaining > 0
                    ? `${checklist.daysRemaining} ${t("checklists.daysLeft")}`
                    : `${Math.abs(checklist.daysRemaining)} ${t("checklists.daysOverdue")}`}
                  )
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Footer: Actions */}
        <div
          className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
          onClick={(e) => e.stopPropagation()}
        >
          <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(checklist)}>
            {t("common.edit")}
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onComplete(checklist.id)}
            disabled={checklist.status === "COMPLETED"}
          >
            {t("checklists.markComplete")}
          </Button>
          {checklist.status === "COMPLETED" && checklist.certUid && (
            <CertificateButton certUid={checklist.certUid} />
          )}
          <Button size="sm" variant="destructive" onClick={() => onDelete(checklist.id)}>
            {t("common.delete")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function ChecklistsTable({
  checklists,
  loading,
  onEdit,
  onComplete,
  onDelete,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  departmentFilter,
  onDepartmentFilterChange,
  onReset,
  departments = [],
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortField,
  sortDirection = "asc",
  onSort,
}: ChecklistsTableProps) {
  const t = useTranslations();
  const [overdueOnly, setOverdueOnly] = useState(false);

  const statusOptions = getChecklistStatusOptions(t, true);
  const departmentOptions = [
    { value: "ALL", label: t("checklists.allDepartments") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  const displayed = overdueOnly ? checklists.filter((c) => c.isOverdue) : checklists;

  const mobileView = (
    <div className="space-y-3 p-4">
      {displayed.map((checklist) => (
        <ChecklistCard
          key={checklist.id}
          checklist={checklist}
          onEdit={onEdit}
          onComplete={onComplete}
          onDelete={onDelete}
          t={t}
        />
      ))}
    </div>
  );

  return (
    <DataTable
      loading={loading}
      empty={displayed.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={overdueOnly ? displayed.length : totalCount}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      showPageSizeSelector={!!onPageSizeChange}
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
                {t("checklists.title")}{" "}
                <span className="text-sm font-normal text-muted-foreground">({totalCount})</span>
              </CardTitle>
              {checklists.filter((c) => c.isOverdue).length > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-950/50 dark:text-red-400">
                  <AlertTriangle className="size-3" />
                  {checklists.filter((c) => c.isOverdue).length} {t("checklists.overdue")}
                </span>
              )}
            </div>
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
              <Select
                value={departmentFilter}
                onChange={onDepartmentFilterChange}
                options={departmentOptions}
                className="w-full sm:w-auto"
              />
              <Button
                variant={overdueOnly ? "destructive" : "outline"}
                size="sm"
                onClick={() => setOverdueOnly(!overdueOnly)}
                className="w-full gap-1.5 sm:w-auto"
              >
                <Filter className="size-3.5" />
                {t("checklists.overdueFilter") || t("checklists.overdue")}
              </Button>
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
              field="employee"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("checklists.employee")}
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
            <SortableTableHead
              field="progress"
              sortable={false}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("checklists.progress")}
            </SortableTableHead>
            <SortableTableHead
              field="tasks"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("checklists.tasks")}
            </SortableTableHead>
            <SortableTableHead
              field="start_date"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("checklists.startDate")}
            </SortableTableHead>
            <SortableTableHead
              field="due_date"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("checklists.dueDate")}
            </SortableTableHead>
            <TableHead className="w-28">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {displayed.map((checklist) => (
            <TableRow
              key={checklist.id}
              className={cn(
                "cursor-pointer transition-colors hover:bg-muted",
                checklist.isOverdue && "border-l-2 border-l-red-500",
              )}
              onClick={() => onEdit(checklist)}
            >
              <TableCell>
                <div className="flex items-center gap-2">
                  <UserAvatar name={checklist.userName} id={checklist.id} />
                  <div>
                    <p className="leading-none font-medium">{checklist.userName}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{checklist.employeeId}</p>
                    {checklist.notes && (
                      <p className="mt-0.5 line-clamp-1 max-w-44 text-xs text-muted-foreground">
                        {checklist.notes}
                      </p>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <ChecklistStatusBadge status={checklist.status} isOverdue={checklist.isOverdue} />
              </TableCell>
              <TableCell>
                <ProgressBar
                  value={checklist.progressPercentage}
                  isOverdue={checklist.isOverdue}
                  completed={checklist.status === "COMPLETED"}
                />
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {checklist.completedTasks}/{checklist.totalTasks}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-sm">{formatDate(checklist.startDate)}</span>
              </TableCell>
              <TableCell>
                <div>
                  <div className="flex items-center gap-1">
                    {checklist.isOverdue && <AlertTriangle className="size-3.5 text-red-500" />}
                    <span
                      className={cn(
                        "text-sm",
                        checklist.isOverdue && "text-red-600 dark:text-red-400",
                      )}
                    >
                      {formatDate(checklist.dueDate)}
                    </span>
                  </div>
                  {checklist.daysRemaining !== null && checklist.status !== "COMPLETED" && (
                    <p
                      className={cn(
                        "text-xs",
                        checklist.daysRemaining < 0 ? "text-red-500" : "text-muted-foreground",
                      )}
                    >
                      {checklist.daysRemaining > 0
                        ? `${checklist.daysRemaining} ${t("checklists.daysLeft")}`
                        : `${Math.abs(checklist.daysRemaining)} ${t("checklists.daysOverdue")}`}
                    </p>
                  )}
                </div>
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center gap-1">
                  <TableActions
                    actions={[
                      buildEditAction(() => onEdit(checklist), t("common.edit")),
                      buildCompleteAction(
                        () => onComplete(checklist.id),
                        t("checklists.markComplete"),
                        checklist.status !== "COMPLETED",
                      ),
                      buildDeleteAction(() => onDelete(checklist.id), t("common.delete")),
                    ]}
                  />
                  {checklist.status === "COMPLETED" && checklist.certUid && (
                    <CertificateButton certUid={checklist.certUid} />
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}
