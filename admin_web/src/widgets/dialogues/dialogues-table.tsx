"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
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
import { useConfirm } from "@/shared/hooks/use-confirm";
import { cn } from "@/shared/lib/utils";
import { TableActions, buildEditAction, buildDeleteAction, buildToggleAction } from "@/shared/components";
import { useRouter } from "next/navigation";
import type { DialogueRow } from "@/shared/hooks/use-dialogues";
import type { SortDirection } from "@/shared/hooks/use-sorting";
import { MessageSquare, ListOrdered, Activity, CheckCircle2, XCircle } from "lucide-react";

const CATEGORY_COLORS: Record<string, string> = {
  VACATION: "bg-sky-100 text-sky-700 dark:bg-sky-950/50 dark:text-sky-300",
  ACCESS: "bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300",
  BENEFITS: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300",
  CONTACTS: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
  WORKTIME: "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
};

const CATEGORIES_LABELS: Record<string, string> = {
  VACATION: "Vacation & Time Off",
  ACCESS: "Passes & Access",
  BENEFITS: "Benefits",
  CONTACTS: "Contacts",
  WORKTIME: "Work Time",
};

function getCategoryLabel(cat: string): string {
  return CATEGORIES_LABELS[cat] || cat;
}

function getCategoryOptions(t: (key: string) => string): { value: string; label: string }[] {
  return [
    { value: "ALL", label: t("dialogues.allCategories") },
    { value: "VACATION", label: t("dialogues.vacation") },
    { value: "ACCESS", label: t("dialogues.access") },
    { value: "BENEFITS", label: t("dialogues.benefits") },
    { value: "CONTACTS", label: t("dialogues.contacts") },
    { value: "WORKTIME", label: t("dialogues.worktime") },
  ];
}

interface DialoguesTableProps {
  dialogues: DialogueRow[];
  loading: boolean;
  onEdit?: (d: DialogueRow) => void;
  onDelete: (id: number) => void;
  onToggleActive: (id: number, isActive: boolean) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (category: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

export function DialoguesTable({
  dialogues,
  loading,
  onDelete,
  onToggleActive,
  searchQuery,
  onSearchChange,
  categoryFilter,
  onCategoryFilterChange,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortField,
  sortDirection = "asc",
  onSort,
}: DialoguesTableProps) {
  const t = useTranslations();
  const confirm = useConfirm();
  const router = useRouter();

  const handleEdit = (d: DialogueRow) => {
    router.push(`/dialogues/${d.id}`);
  };

  const categoryOptions = getCategoryOptions(t);

  const handleDelete = async (id: number, title: string) => {
    if (
      !(await confirm({
        title: t("dialogues.deleteDialogue"),
        description: t("common.confirmDelete").replace("item", `"${title}"`),
        variant: "destructive",
        confirmText: t("common.delete"),
      }))
    )
      return;
    onDelete(id);
  };

  const activeCount = dialogues.filter((d) => d.isActive).length;

  return (
    <DataTable
      loading={loading}
      empty={dialogues.length === 0}
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
            <div className="flex items-center gap-3">
              <CardTitle>
                {t("dialogues.title")}{" "}
                <span className="text-muted-foreground text-sm font-normal">
                  ({totalCount ?? dialogues.length})
                </span>
              </CardTitle>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                  <Activity className="size-3" />
                  {activeCount} {t("dialogues.activeStatus")}
                </span>
              </div>
            </div>
            <div className="flex gap-2">
              <SearchInput
                placeholder={t("dialogues.searchDialogues")}
                value={searchQuery}
                onChange={onSearchChange}
              />
              <Select
                value={categoryFilter}
                onChange={onCategoryFilterChange}
                options={categoryOptions}
              />
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead field="title" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("dialogues.name")}
            </SortableTableHead>
            <SortableTableHead field="category" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("dialogues.category")}
            </SortableTableHead>
            <SortableTableHead field="stepsCount" sortable={false} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("dialogues.stepsCount")}
            </SortableTableHead>
            <SortableTableHead field="isActive" sortable={!!onSort} sortField={sortField ?? null} sortDirection={sortDirection} onSort={onSort ?? (() => {})}>
              {t("common.status")}
            </SortableTableHead>
            <TableHead className="w-28">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dialogues.map((d) => (
            <TableRow
              key={d.id}
              className="hover:bg-muted cursor-pointer transition-colors"
              onClick={() => handleEdit(d)}
            >
              <TableCell>
                <div className="flex items-start gap-3">
                  <div className="bg-muted flex size-8 shrink-0 items-center justify-center rounded-lg">
                    <MessageSquare className="text-muted-foreground size-4" />
                  </div>
                  <div>
                    <p className="font-medium leading-none">{d.title}</p>
                    {d.description && (
                      <p className="text-muted-foreground mt-0.5 line-clamp-1 text-xs">{d.description}</p>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <span className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                  CATEGORY_COLORS[d.category] ?? "bg-muted text-muted-foreground",
                )}>
                  {getCategoryLabel(d.category)}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <ListOrdered className="text-muted-foreground size-3.5" />
                  {d.stepsCount}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  {d.isActive ? (
                    <>
                      <CheckCircle2 className="size-4 text-emerald-500" />
                      <span className="text-xs text-emerald-600 dark:text-emerald-400">{t("dialogues.activeStatus")}</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="text-muted-foreground size-4" />
                      <span className="text-muted-foreground text-xs">{t("dialogues.inactiveStatus")}</span>
                    </>
                  )}
                </div>
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <TableActions
                  actions={[
                    buildEditAction(() => handleEdit(d), t("common.edit")),
                    {
                      ...buildToggleAction(
                        () => onToggleActive(d.id, !d.isActive),
                        d.isActive ? t("common.deactivate") : t("common.activate"),
                      ),
                      color: d.isActive ? "text-amber-500" : "text-emerald-500",
                    },
                    buildDeleteAction(() => handleDelete(d.id, d.title), t("common.delete")),
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
