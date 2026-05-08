"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { Checkbox } from "@/shared/ui/checkbox";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { StatusBadge } from "@/shared/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import { TableActions, buildEditAction, buildDeleteAction, buildPublishAction } from "@/shared/components";
import { BookOpen, Eye, Pin, Star } from "lucide-react";
import type { Category } from "@/shared/types";
import { getArticleStatusOptions } from "@/shared/lib/constants";
import type { ArticleRow } from "@/shared/hooks/use-articles";
import type { SortDirection } from "@/shared/hooks/use-sorting";

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

  function ArticleCard({
    article,
    onEdit,
    onPublish,
    onDelete,
    t,
  }: {
    article: ArticleRow;
    onEdit: (article: ArticleRow) => void;
    onPublish: (id: number) => void;
    onDelete: (id: number) => void;
    t: (key: string) => string;
  }) {
    return (
      <Card
        className="cursor-pointer transition-colors hover:bg-muted/50"
        onClick={() => onEdit(article)}
      >
        <CardContent className="p-4">
          {/* Header: Title + Status + Badges */}
          <div className="mb-3 flex items-start gap-3">
            <div className="bg-muted flex size-8 shrink-0 items-center justify-center rounded-lg">
              <BookOpen className="text-muted-foreground size-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-semibold truncate">{article.title}</h3>
                {article.isPinned && <Pin className="size-3 text-purple-500 shrink-0" />}
                {article.isFeatured && <Star className="size-3 text-yellow-500 shrink-0" />}
                <StatusBadge status={article.status} />
              </div>
              <p className="text-muted-foreground mt-1 line-clamp-2 text-xs">{article.excerpt}</p>
            </div>
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-1">
              <Badge
                variant="secondary"
                style={{
                  backgroundColor: article.category_color || undefined,
                  color: article.category_color ? '#fff' : undefined,
                }}
              >
                {article.category}
              </Badge>
            </div>
            <div>
              <span className="text-muted-foreground">{t("knowledge.author")}: </span>
              <span>{article.author}</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye className="text-muted-foreground size-3" />
              <span>{article.viewCount}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("common.createdAt")}: </span>
              <span>{new Date(article.createdAt).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="flex items-center gap-2 border-t pt-3 flex-col sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(article)}>
              {t("common.edit")}
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              onClick={() => onPublish(article.id)}
              disabled={article.status !== "DRAFT"}
            >
              {t("knowledge.publish")}
            </Button>
            <Button size="sm" variant="destructive" onClick={() => onDelete(article.id)}>
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mobileView = (
    <div className="space-y-3 p-4">
      {articles.map((article) => (
        <ArticleCard
          key={article.id}
          article={article}
          onEdit={onEdit}
          onPublish={onPublish}
          onDelete={onDelete}
          t={t}
        />
      ))}
    </div>
  );

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
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>{t("knowledge.articles")}</CardTitle>
            <div className="flex flex-col gap-2 w-full sm:flex-row sm:items-center sm:flex-wrap">
              <SearchInput placeholder={t("common.searchPlaceholder")} value={searchQuery} onChange={onSearchChange} className="w-full sm:w-auto" />
              <Select
                value={categoryFilter}
                onChange={onCategoryFilterChange}
                options={categoryOptions}
                className="w-full sm:w-auto"
              />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
                className="w-full sm:w-auto"
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
              <Button variant="outline" onClick={onReset} className="w-full sm:w-auto">
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
                <div className="flex items-start gap-3">
                  <div className="bg-muted flex size-8 shrink-0 items-center justify-center rounded-lg">
                    <BookOpen className="text-muted-foreground size-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{article.title}</p>
                      {article.isPinned && <Pin className="size-3 text-purple-500" />}
                      {article.isFeatured && <Star className="size-3 text-yellow-500" />}
                    </div>
                    <p className="text-muted-foreground text-sm">{article.excerpt}</p>
                  </div>
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