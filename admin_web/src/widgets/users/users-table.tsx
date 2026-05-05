"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
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
import { TableActions, buildEditAction, buildDeleteAction, buildAssignMentorAction } from "@/shared/components";
import { Building, Shield, ShieldOff, UserCog } from "lucide-react";
import { getRoleOptions } from "@/shared/lib/constants";
import type { UserItem } from "@/shared/hooks/use-users";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import type { SortDirection } from "@/shared/hooks/use-sorting";
import { cn } from "@/shared/lib/utils";

interface UsersTableProps {
  users: UserItem[];
  loading: boolean;
  onEdit: (user: UserItem) => void;
  onDelete: (id: number) => void;
  onAssignMentor?: (user: UserItem) => void;
  onDeactivate?: (user: UserItem) => void;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  roleFilter: string;
  onRoleFilterChange: (value: string) => void;
  departmentFilter: string;
  onDepartmentFilterChange: (value: string) => void;
  onReset: () => void;
  departments?: { id: number; name: string }[];
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

const ROLE_STYLES: Record<string, string> = {
  ADMIN: "bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-950/50 dark:text-violet-300 dark:border-violet-800",
  HR: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800",
  MENTOR: "bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-950/50 dark:text-teal-300 dark:border-teal-800",
  NEWBIE: "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800",
};

const AVATAR_COLORS = [
  "bg-blue-500", "bg-teal-500", "bg-violet-500", "bg-amber-500",
  "bg-rose-500", "bg-cyan-500", "bg-emerald-500", "bg-indigo-500",
];

function UserAvatar({ name, id }: { name: string; id: number }) {
  const initials = name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
  const color = AVATAR_COLORS[id % AVATAR_COLORS.length];
  return (
    <div className={cn("flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white", color)}>
      {initials || "?"}
    </div>
  );
}

export function UsersTable({
  users,
  loading,
  onEdit,
  onDelete,
  onAssignMentor,
  onDeactivate,
  searchQuery,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
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
}: UsersTableProps) {
  const t = useTranslations();

  const roleOptions = getRoleOptions(t, true);
  const departmentOptions = [
    { value: "ALL", label: t("users.allDepartments") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  return (
    <DataTable
      loading={loading}
      empty={users.length === 0}
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
              {t("users.title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? users.length})
              </span>
            </CardTitle>
            <div className="flex flex-wrap gap-2">
              <SearchInput
                placeholder={t("users.searchByNameOrEmail")}
                value={searchQuery}
                onChange={onSearchChange}
              />
              <Select value={roleFilter} onChange={onRoleFilterChange} options={roleOptions} />
              <Select
                value={departmentFilter}
                onChange={onDepartmentFilterChange}
                options={departmentOptions}
              />
              <Button variant="outline" onClick={onReset}>
                {t("users.reset")}
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
              {t("common.user")}
            </SortableTableHead>
            <SortableTableHead field="employee_id" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("users.employeeId")}
            </SortableTableHead>
            <SortableTableHead field="department" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.department")}
            </SortableTableHead>
            <SortableTableHead field="position" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.position")}
            </SortableTableHead>
            <SortableTableHead field="role" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.role")}
            </SortableTableHead>
            <SortableTableHead field="isActive" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.status")}
            </SortableTableHead>
            <SortableTableHead field="createdAt" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.createdAt")}
            </SortableTableHead>
            <TableHead className="w-28">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow
              key={user.id}
              className={cn("hover:bg-muted cursor-pointer transition-colors", !user.isActive && "opacity-60")}
              onClick={() => onEdit(user)}
            >
              <TableCell>
                <div className="flex items-center gap-3">
                  <UserAvatar name={user.name} id={user.id} />
                  <div>
                    <p className="font-medium leading-none">{user.name}</p>
                    <p className="text-muted-foreground mt-0.5 text-xs">{user.email}</p>
                    {user.telegram_id && (
                      <p className="mt-0.5 text-xs text-blue-500">@tg:{user.telegram_id}</p>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell className="font-mono text-sm">{user.employee_id || "—"}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <Building className="text-muted-foreground size-3.5" />
                  <span className="text-sm">{user.department || "—"}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{user.position || "—"}</span>
              </TableCell>
              <TableCell>
                <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold", ROLE_STYLES[user.role] ?? "bg-muted text-muted-foreground")}>
                  {t(`statuses.${user.role}`) || user.role}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  {user.isActive ? (
                    <>
                      <div className="size-2 rounded-full bg-emerald-500" />
                      <span className="text-xs text-emerald-600 dark:text-emerald-400">{t("common.active")}</span>
                    </>
                  ) : (
                    <>
                      <div className="size-2 rounded-full bg-gray-400" />
                      <span className="text-muted-foreground text-xs">{t("common.inactive")}</span>
                    </>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : "—"}
                </span>
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(user), t("common.edit")),
                    ...(onAssignMentor
                      ? [buildAssignMentorAction(() => onAssignMentor(user), t("users.assignMentor"), user.role === "NEWBIE")]
                      : []),
                    ...(onDeactivate
                      ? [{
                          type: "toggle" as const,
                          icon: user.isActive ? ShieldOff : Shield,
                          label: user.isActive ? t("users.deactivate") : t("users.activate"),
                          onClick: () => onDeactivate(user),
                          variant: "ghost" as const,
                          color: user.isActive ? "text-amber-500" : "text-emerald-500",
                          show: true,
                        }]
                      : []),
                    {
                      type: "edit" as const,
                      icon: UserCog,
                      label: t("users.changeRole"),
                      onClick: () => onEdit(user),
                      variant: "ghost" as const,
                      show: false,
                    },
                    buildDeleteAction(() => onDelete(user.id), t("common.delete")),
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
