import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { Building, MoreHorizontal, Trash2 } from "lucide-react";
import { ROLES } from "@/lib/constants";
import type { UserItem } from "@/hooks/use-users";

interface UsersTableProps {
  users: UserItem[];
  loading: boolean;
  onEdit: (user: UserItem) => void;
  onDelete: (id: number) => void;
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
  currentPage,
  totalPages,
  totalCount,
  onPageChange,
}: UsersTableProps) {
  return (
    <DataTable
      loading={loading}
      empty={users.length === 0}
      emptyMessage="Пользователи не найдены"
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      onPageChange={onPageChange}
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Пользователь</TableHead>
            <TableHead>Отдел</TableHead>
            <TableHead>Должность</TableHead>
            <TableHead>Роль</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead>Дата приёма</TableHead>
            <TableHead className="w-[100px]">Действия</TableHead>
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
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString("ru-RU") : "-"}
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
