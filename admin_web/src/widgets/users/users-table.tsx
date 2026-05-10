"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import {
  TableActions,
  buildEditAction,
  buildDeleteAction,
  buildAssignMentorAction,
} from "@/shared/components";
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
  ADMIN:
    "bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-950/50 dark:text-violet-300 dark:border-violet-800",
  HR: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800",
  MENTOR:
    "bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-950/50 dark:text-teal-300 dark:border-teal-800",
  NEWBIE:
    "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800",
};

const AVATAR_COLORS = [
  "bg-blue-500",
  "bg-teal-500",
  "bg-violet-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-cyan-500",
  "bg-emerald-500",
  "bg-indigo-500",
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
    <div
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
        color,
      )}
    >
      {initials || "?"}
    </div>
  );
}

function UserCard({
  user,
  onEdit,
  onDelete,
  onAssignMentor,
  onDeactivate,
  t,
}: {
  user: UserItem;
  onEdit: (user: UserItem) => void;
  onDelete: (id: number) => void;
  onAssignMentor?: (user: UserItem) => void;
  onDeactivate?: (user: UserItem) => void;
  t: (key: string) => string;
}) {
  const handleCardClick = () => onEdit(user);

  return (
    <Card
      className={cn(
        "cursor-pointer transition-colors hover:bg-muted/50",
        !user.isActive && "opacity-60",
      )}
      onClick={handleCardClick}
    >
      <CardContent className="p-4">
        {/* Header: Avatar + Name + Status */}
        <div className="mb-3 flex items-start gap-3">
          <UserAvatar name={user.name} id={user.id} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3 className="truncate font-semibold">{user.name}</h3>
              <div className="flex size-2 shrink-0 rounded-full bg-emerald-500" />
            </div>
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            {user.telegram_id && (
              <p className="mt-0.5 text-xs text-blue-500">@tg:{user.telegram_id}</p>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-muted-foreground">{t("common.role")}: </span>
            <span
              className={cn(
                "inline-flex items-center rounded-full border px-2 py-0.5 font-semibold",
                ROLE_STYLES[user.role] ?? "bg-muted text-muted-foreground",
              )}
            >
              {t(`statuses.${user.role}`) || user.role}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("common.department")}: </span>
            <span>{user.department || "—"}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("common.position")}: </span>
            <span>{user.position || "—"}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("users.employeeId")}: </span>
            <span className="font-mono">{user.employee_id || "—"}</span>
          </div>
        </div>

        {/* Footer: Actions */}
        <div
          className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
          onClick={(e) => e.stopPropagation()}
        >
          <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(user)}>
            {t("common.edit")}
          </Button>
          {onAssignMentor && user.role === "NEWBIE" && (
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              onClick={() => onAssignMentor(user)}
            >
              {t("users.assignMentor")}
            </Button>
          )}
          {onDeactivate && (
            <Button
              size="sm"
              variant={user.isActive ? "outline" : "default"}
              className={user.isActive ? "flex-1 text-amber-500 hover:text-amber-600" : "flex-1"}
              onClick={() => onDeactivate(user)}
            >
              {user.isActive ? t("users.deactivate") : t("users.activate")}
            </Button>
          )}
          <Button size="sm" variant="destructive" onClick={() => onDelete(user.id)}>
            {t("common.delete")}
          </Button>
        </div>
      </CardContent>
    </Card>
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

  const mobileView = (
    <div className="space-y-3 p-4">
      {users.map((user) => (
        <UserCard
          key={user.id}
          user={user}
          onEdit={onEdit}
          onDelete={onDelete}
          onAssignMentor={onAssignMentor}
          onDeactivate={onDeactivate}
          t={t}
        />
      ))}
    </div>
  );

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
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
              {t("users.title")}{" "}
              <span className="text-sm font-normal text-muted-foreground">
                ({totalCount ?? users.length})
              </span>
            </CardTitle>
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <SearchInput
                placeholder={t("users.searchByNameOrEmail")}
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
              <Select
                value={roleFilter}
                onChange={onRoleFilterChange}
                options={roleOptions}
                className="w-full sm:w-auto"
              />
              <Select
                value={departmentFilter}
                onChange={onDepartmentFilterChange}
                options={departmentOptions}
                className="w-full sm:w-auto"
              />
              <Button variant="outline" onClick={onReset} className="w-full sm:w-auto">
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
            <SortableTableHead
              field="name"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.user")}
            </SortableTableHead>
            <SortableTableHead
              field="employee_id"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("users.employeeId")}
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
              field="role"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.role")}
            </SortableTableHead>
            <SortableTableHead
              field="isActive"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.status")}
            </SortableTableHead>
            <SortableTableHead
              field="createdAt"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.createdAt")}
            </SortableTableHead>
            <TableHead className="w-28">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow
              key={user.id}
              className={cn(
                "cursor-pointer transition-colors hover:bg-muted",
                !user.isActive && "opacity-60",
              )}
              onClick={() => onEdit(user)}
            >
              <TableCell>
                <div className="flex items-center gap-3">
                  <UserAvatar name={user.name} id={user.id} />
                  <div>
                    <p className="leading-none font-medium">{user.name}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{user.email}</p>
                    {user.telegram_id && (
                      <p className="mt-0.5 text-xs text-blue-500">@tg:{user.telegram_id}</p>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell className="font-mono text-sm">{user.employee_id || "—"}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <Building className="size-3.5 text-muted-foreground" />
                  <span className="text-sm">{user.department || "—"}</span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{user.position || "—"}</span>
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                    ROLE_STYLES[user.role] ?? "bg-muted text-muted-foreground",
                  )}
                >
                  {t(`statuses.${user.role}`) || user.role}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  {user.isActive ? (
                    <>
                      <div className="size-2 rounded-full bg-emerald-500" />
                      <span className="text-xs text-emerald-600 dark:text-emerald-400">
                        {t("common.active")}
                      </span>
                    </>
                  ) : (
                    <>
                      <div className="size-2 rounded-full bg-gray-400" />
                      <span className="text-xs text-muted-foreground">{t("common.inactive")}</span>
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
                      ? [
                          buildAssignMentorAction(
                            () => onAssignMentor(user),
                            t("users.assignMentor"),
                            user.role === "NEWBIE",
                          ),
                        ]
                      : []),
                    ...(onDeactivate
                      ? [
                          {
                            type: "toggle" as const,
                            icon: user.isActive ? ShieldOff : Shield,
                            label: user.isActive ? t("users.deactivate") : t("users.activate"),
                            onClick: () => onDeactivate(user),
                            variant: "ghost" as const,
                            color: user.isActive ? "text-amber-500" : "text-emerald-500",
                            show: true,
                          },
                        ]
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
