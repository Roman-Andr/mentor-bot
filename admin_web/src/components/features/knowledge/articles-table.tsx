"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
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
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { TableActions, buildEditAction, buildDeleteAction, buildPublishAction } from "@/components/shared";
import { BookOpen, Eye, Pin, Star } from "lucide-react";
import type { Category } from "@/types";
import { getArticleStatusOptions } from "@/lib/constants";
import type { ArticleRow } from "@/hooks/use-articles";
import type { SortDirection } from "@/hooks/use-sorting";

export type { ArticleRow };

interface ArticlesTableProps {
  articles: ArticleRow[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  pinnedFilter: string;
  onPinnedFilterChange: (value: string) => void;
  onReset: () => void;
  categories: Category[];
  onEdit: (article: ArticleRow) => void;
  onPublish: (id: number) => void;
  onDelete: (id: number) => void;
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

export function ArticlesTable({
  articles,
  loading,
  searchQuery,
  onSearchChange,
  categoryFilter,
  onCategoryFilterChange,
  statusFilter,
  onStatusFilterChange,
  pinnedFilter,
  onPinnedFilterChange,
  onReset,
  categories,
  onEdit,
  onPublish,
  onDelete,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortField,
  sortDirection = "asc",
  onSort,
}: ArticlesTableProps) {
  const t = useTranslations();

  const columns = [
    { key: "title", label: t("knowledge.article"), sortable: true },
    { key: "category", label: t("knowledge.category"), sortable: true },
    { key: "author", label: t("knowledge.author"), sortable: true },
    { key: "viewCount", label: t("knowledge.viewCount"), sortable: true },
    { key: "status", label: t("common.status"), sortable: true },
    { key: "createdAt", label: t("common.createdAt"), sortable: true },
  ];

  const categoryOptions = [
    { value: "ALL", label: t("knowledge.allCategories") },
    ...categories.map((cat) => ({ value: String(cat.id), label: cat.name })),
  ];

  const statusOptions = getArticleStatusOptions(t, true);

  return (
    <DataTable
      loading={loading}
      empty={articles.length === 0}
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
            <CardTitle>{t("knowledge.articles")}</CardTitle>
            <div className="flex gap-2">
              <SearchInput placeholder={t("common.searchPlaceholder")} value={searchQuery} onChange={onSearchChange} />
              <Select
                value={categoryFilter}
                onChange={onCategoryFilterChange}
                options={categoryOptions}
              />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
              />
              <div className="flex items-center gap-2 px-3">
                <Checkbox
                  id="pinned-filter"
                  checked={pinnedFilter === "true"}
                  onCheckedChange={(checked) => onPinnedFilterChange(checked ? "true" : "ALL")}
                />
                <label htmlFor="pinned-filter" className="text-sm cursor-pointer">
                  {t("knowledge.pinnedOnly")}
                </label>
              </div>
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
          {articles.map((article) => (
            <TableRow
              key={article.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(article)}
            >
              <TableCell>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{article.title}</p>
                    {article.isPinned && <Pin className="size-3 text-purple-500" />}
                    {article.isFeatured && <Star className="size-3 text-yellow-500" />}
                  </div>
                  <p className="text-muted-foreground text-sm">{article.excerpt}</p>
                </div>
              </TableCell>
              <TableCell>
                <Badge
                  variant="secondary"
                  style={{
                    backgroundColor: article.category_color || undefined,
                    color: article.category_color ? '#fff' : undefined,
                  }}
                >
                  {article.category}
                </Badge>
              </TableCell>
              <TableCell>{article.author}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Eye className="text-muted-foreground size-4" />
                  {article.viewCount}
                </div>
              </TableCell>
              <TableCell>
                <StatusBadge status={article.status} />
              </TableCell>
              <TableCell>{new Date(article.createdAt).toLocaleDateString()}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(article), t("common.edit")),
                    buildPublishAction(
                      () => onPublish(article.id),
                      t("knowledge.publish"),
                      article.status === "DRAFT",
                      BookOpen,
                    ),
                    buildDeleteAction(() => onDelete(article.id), t("common.delete")),
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