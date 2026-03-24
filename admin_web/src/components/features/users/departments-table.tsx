import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
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
import { Trash2, MoreHorizontal } from "lucide-react";
import type { DepartmentRow } from "@/hooks/use-departments";

interface DepartmentsTableProps {
  departments: DepartmentRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  onPageChange: (page: number) => void;
  onEdit: (department: DepartmentRow) => void;
  onDelete: (id: number) => void;
}

export function DepartmentsTable({
  departments,
  loading,
  searchQuery,
  onSearchChange,
  currentPage,
  totalPages,
  totalCount,
  onPageChange,
  onEdit,
  onDelete,
}: DepartmentsTableProps) {
  return (
    <DataTable
      loading={loading}
      empty={departments.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      onPageChange={onPageChange}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Отделы</CardTitle>
            <SearchInput placeholder="Поиск..." value={searchQuery} onChange={onSearchChange} />
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Название</TableHead>
            <TableHead>Описание</TableHead>
            <TableHead>Дата создания</TableHead>
            <TableHead className="w-[100px]">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {departments.map((department) => (
            <TableRow
              key={department.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(department)}
            >
              <TableCell>
                <span className="font-medium">{department.name}</span>
              </TableCell>
              <TableCell className="text-muted-foreground max-w-[300px] truncate text-sm">
                {department.description || "—"}
              </TableCell>
              <TableCell>{new Date(department.createdAt).toLocaleDateString("ru-RU")}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onEdit(department)}>
                    <MoreHorizontal className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(department.id)}
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
