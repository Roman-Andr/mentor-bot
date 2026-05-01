"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { DataTable } from "@/components/ui/data-table";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
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
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction, buildCompleteAction } from "@/components/shared";
import { AlertTriangle, Clock, Download } from "lucide-react";
import { CHECKLIST_STATUSES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import type { ChecklistItem } from "@/hooks/use-checklists";
import type { SortDirection } from "@/hooks/use-sorting";
import { CertificateButton } from "@/components/features/certificates/certificate-button";

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

  const columns = [
    { key: "employee", label: t("checklists.employee"), sortable: true },
    { key: "status", label: t("common.status"), sortable: true },
    { key: "progress", label: t("checklists.progress"), sortable: false },
    { key: "tasks", label: t("checklists.tasks"), sortable: true },
    { key: "start_date", label: t("checklists.startDate"), sortable: true },
    { key: "due_date", label: t("checklists.dueDate"), sortable: true },
  ];

  const departmentOptions = [
    { value: "ALL", label: t("common.all") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  return (
    <DataTable
      loading={loading}
      empty={checklists.length === 0}
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
              {t("checklists.title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">({totalCount})</span>
            </CardTitle>
            <div className="flex gap-2">
              <SearchInput value={searchQuery} onChange={onSearchChange} />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={CHECKLIST_STATUSES}
              />
              <Select
                value={departmentFilter}
                onChange={onDepartmentFilterChange}
                options={departmentOptions}
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
            {columns.map((col) => (
              <SortableTableHead
                key={col.key}
                field={col.key}
                sortable={col.sortable && !!onSort}
                sortField={sortField ?? null}
                sortDirection={sortDirection}
                onSort={onSort ?? (() => {})}
              >
                {col.label}
              </SortableTableHead>
            ))}
            <TableHead className="w-25">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {checklists.map((checklist) => (
            <TableRow
              key={checklist.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(checklist)}
            >
              <TableCell>
                <div>
                  <p className="font-medium">{checklist.userName}</p>
                  <p className="text-muted-foreground text-xs">{checklist.employeeId}</p>
                  {checklist.notes && (
                    <p className="text-muted-foreground max-w-50 truncate text-sm">
                      {checklist.notes}
                    </p>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <ChecklistStatusBadge status={checklist.status} isOverdue={checklist.isOverdue} />
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="bg-muted h-2 min-w-15 flex-1 overflow-hidden rounded-full">
                    <div
                      className={`h-full rounded-full transition-all ${
                        checklist.progressPercentage === 100
                          ? "bg-green-500 dark:bg-green-600"
                          : checklist.isOverdue
                            ? "bg-red-500 dark:bg-red-600"
                            : "bg-blue-500 dark:bg-blue-600"
                      }`}
                      style={{ width: `${checklist.progressPercentage}%` }}
                    />
                  </div>
                  <span className="text-muted-foreground text-sm whitespace-nowrap">
                    {checklist.progressPercentage}%
                  </span>
                </div>
              </TableCell>
              <TableCell>
                {checklist.completedTasks}/{checklist.totalTasks}
              </TableCell>
              <TableCell>{formatDate(checklist.startDate)}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  {checklist.isOverdue && <AlertTriangle className="size-4 text-red-500" />}
                  <span className={checklist.isOverdue ? "text-red-600" : ""}>
                    {formatDate(checklist.dueDate)}
                  </span>
                </div>
                {checklist.daysRemaining !== null && checklist.status !== "COMPLETED" && (
                  <span className="text-muted-foreground text-xs">
                    {checklist.daysRemaining > 0
                      ? `${checklist.daysRemaining} ${t("checklists.daysLeft")}`
                      : `${Math.abs(checklist.daysRemaining)} ${t("checklists.daysOverdue")}`}
                  </span>
                )}
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center gap-2">
                  <TableActions
                    actions={[
                      buildEditAction(() => onEdit(checklist)),
                      ...(checklist.status !== "COMPLETED"
                        ? [buildCompleteAction(() => onComplete(checklist.id))]
                        : []
                      ),
                      buildDeleteAction(() => onDelete(checklist.id)),
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

function ChecklistStatusBadge({ status, isOverdue }: { status: string; isOverdue: boolean }) {
  const t = useTranslations();
  
  if (isOverdue) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-800">
        <Clock className="size-3" />
        {t("checklists.overdue")}
      </span>
    );
  }
  return <StatusBadge status={status} />;
}