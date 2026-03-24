import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import type { CategoryRow } from "@/hooks/use-categories";

interface CategoriesTableProps {
  categories: CategoryRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  onPageChange: (page: number) => void;
  onEdit: (category: CategoryRow) => void;
  onDelete: (id: number) => void;
}

export function CategoriesTable({
  categories,
  loading,
  searchQuery,
  onSearchChange,
  currentPage,
  totalPages,
  totalCount,
  onPageChange,
  onEdit,
  onDelete,
}: CategoriesTableProps) {
  return (
    <DataTable
      loading={loading}
      empty={categories.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      onPageChange={onPageChange}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Категории</CardTitle>
            <SearchInput placeholder="Поиск..." value={searchQuery} onChange={onSearchChange} />
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Название</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Описание</TableHead>
            <TableHead>Статей</TableHead>
            <TableHead>Порядок</TableHead>
            <TableHead>Дата</TableHead>
            <TableHead className="w-[100px]">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {categories.map((category) => (
            <TableRow
              key={category.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(category)}
            >
              <TableCell>
                <div className="flex items-center gap-2">
                  {category.color && (
                    <span
                      className="inline-block size-3 rounded-full"
                      style={{ backgroundColor: category.color }}
                    />
                  )}
                  <span className="font-medium">{category.name}</span>
                  {category.parent_name && (
                    <Badge variant="outline" className="text-xs">
                      {category.parent_name}
                    </Badge>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <code className="text-muted-foreground text-xs">{category.slug}</code>
              </TableCell>
              <TableCell className="text-muted-foreground max-w-[200px] truncate text-sm">
                {category.description || "—"}
              </TableCell>
              <TableCell>
                <Badge variant="secondary">{category.articles_count}</Badge>
              </TableCell>
              <TableCell>{category.order}</TableCell>
              <TableCell>{new Date(category.createdAt).toLocaleDateString("ru-RU")}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onEdit(category)}>
                    <MoreHorizontal className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(category.id)}
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
