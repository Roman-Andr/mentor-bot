"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui/status-badge";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction, buildAssignMentorAction } from "@/components/shared";
import { Building } from "lucide-react";
import { getRoleOptions } from "@/lib/constants";
import type { UserItem } from "@/hooks/use-users";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import type { SortDirection } from "@/hooks/use-sorting";

interface UsersTableProps {
  users: UserItem[];
  loading: boolean;
  onEdit: (user: UserItem) => void;
  onDelete: (id: number) => void;
  onAssignMentor?: (user: UserItem) => void;
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

const ROLE_VARIANTS: Record<string, "default" | "secondary" | "outline"> = {
  ADMIN: "default",
  HR: "secondary",
  MENTOR: "default",
};

export function UsersTable({
  users,
  loading,
  onEdit,
  onDelete,
  onAssignMentor,
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
          <div className="flex items-center justify-between">
            <CardTitle>
              {t("users.title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? users.length})
              </span>
            </CardTitle>
            <div className="flex gap-2">
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
            <TableHead className="w-25">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow
              key={user.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(user)}
            >
              <TableCell>
                <div>
                  <p className="font-medium">{user.name}</p>
                  <p className="text-muted-foreground text-sm">{user.email}</p>
                </div>
              </TableCell>
              <TableCell className="font-mono text-sm">{user.employee_id}</TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Building className="text-muted-foreground size-4" />
                  {user.department}
                </div>
              </TableCell>
              <TableCell>{user.position}</TableCell>
              <TableCell>
                <Badge variant={ROLE_VARIANTS[user.role] ?? "outline"}>
                  {t(`statuses.${user.role}`)}
                </Badge>
              </TableCell>
              <TableCell>
                <StatusBadge status={user.isActive ? "ACTIVE" : "INACTIVE"} />
              </TableCell>
              <TableCell>
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : "-"}
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