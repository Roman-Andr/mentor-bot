"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { SquarePen, Trash2, CheckCircle, AlertTriangle, Clock } from "lucide-react";
import { CHECKLIST_STATUSES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import type { ChecklistItem } from "@/hooks/use-checklists";

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
}: ChecklistsTableProps) {
  const t = useTranslations();

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
            <TableHead>{t("checklists.employee")}</TableHead>
            <TableHead>{t("common.status")}</TableHead>
            <TableHead>{t("checklists.progress")}</TableHead>
            <TableHead>{t("checklists.tasks")}</TableHead>
            <TableHead>{t("checklists.startDate")}</TableHead>
            <TableHead>{t("checklists.dueDate")}</TableHead>
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
                          ? "bg-green-500"
                          : checklist.isOverdue
                            ? "bg-red-500"
                            : "bg-blue-500"
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
                <div className="flex gap-1">
                   <Button variant="ghost" size="icon" onClick={() => onEdit(checklist)}>
                     <SquarePen className="size-4" />
                   </Button>
                  {checklist.status !== "COMPLETED" && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-green-500"
                      onClick={() => onComplete(checklist.id)}
                      title={t("checklists.markComplete")}
                    >
                      <CheckCircle className="size-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(checklist.id)}
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