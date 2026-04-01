"use client";

import { useTranslations } from "next-intl";
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
import { Building, MoreHorizontal, Trash2 } from "lucide-react";
import { ROLES, ROLES_WITH_ALL } from "@/lib/constants";
import type { UserItem } from "@/hooks/use-users";

interface UsersTableProps {
  users: UserItem[];
  loading: boolean;
  onEdit: (user: UserItem) => void;
  onDelete: (id: number) => void;
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
  onPageChange?: (page: number) => void;
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
  onPageChange,
}: UsersTableProps) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");

  const departmentOptions = [
    { value: "ALL", label: t("allDepartments") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];
  return (
    <DataTable
      loading={loading}
      empty={users.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      onPageChange={onPageChange}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {t("title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? users.length})
              </span>
            </CardTitle>
            <div className="flex gap-2">
              <SearchInput
                placeholder={t("searchByNameOrEmail")}
                value={searchQuery}
                onChange={onSearchChange}
              />
              <Select value={roleFilter} onChange={onRoleFilterChange} options={ROLES_WITH_ALL} />
              <Select
                value={departmentFilter}
                onChange={onDepartmentFilterChange}
                options={departmentOptions}
              />
              <Button variant="outline" onClick={onReset}>
                {t("reset")}
              </Button>
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("user")}</TableHead>
            <TableHead>{t("employeeId")}</TableHead>
            <TableHead>{tCommon("department")}</TableHead>
            <TableHead>{t("position")}</TableHead>
            <TableHead>{tCommon("role")}</TableHead>
            <TableHead>{t("status")}</TableHead>
            <TableHead>{t("addedAt")}</TableHead>
            <TableHead className="w-[100px]">{tCommon("actions")}</TableHead>
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
                  {ROLES.find((r) => r.value === user.role)?.label || user.role}
                </Badge>
              </TableCell>
              <TableCell>
                <StatusBadge status={user.isActive ? "ACTIVE" : "INACTIVE"} />
              </TableCell>
              <TableCell>
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : "-"}
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onEdit(user)}>
                    <MoreHorizontal className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(user.id)}
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