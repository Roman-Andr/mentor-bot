"use client";

import { useTranslations } from "@/hooks/use-translations";
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
import { Trash2, SquarePen } from "lucide-react";
import type { CategoryRow } from "@/hooks/use-categories";

interface CategoriesTableProps {
  categories: CategoryRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
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
  pageSize,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
}: CategoriesTableProps) {
  const t = useTranslations();

  return (
    <DataTable
      loading={loading}
      empty={categories.length === 0}
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
            <CardTitle>{t("knowledge.categories")}</CardTitle>
            <SearchInput placeholder={t("common.searchPlaceholder")} value={searchQuery} onChange={onSearchChange} />
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("knowledge.name")}</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>{t("common.description")}</TableHead>
            <TableHead>{t("knowledge.articles")}</TableHead>
            <TableHead>{t("knowledge.order")}</TableHead>
            <TableHead>{t("common.createdAt")}</TableHead>
            <TableHead className="w-25">{t("common.actions")}</TableHead>
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
              <TableCell className="text-muted-foreground max-w-50 truncate text-sm">
                {category.description || "—"}
              </TableCell>
              <TableCell>
                <Badge variant="secondary">{category.articles_count}</Badge>
              </TableCell>
              <TableCell>{category.order}</TableCell>
              <TableCell>{new Date(category.createdAt).toLocaleDateString()}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex gap-1">
                   <Button variant="ghost" size="icon" onClick={() => onEdit(category)}>
                     <SquarePen className="size-4" />
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