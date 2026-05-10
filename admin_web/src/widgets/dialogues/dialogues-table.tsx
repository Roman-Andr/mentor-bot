"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import { useConfirm } from "@/shared/hooks/use-confirm";
import { cn } from "@/shared/lib/utils";
import {
  TableActions,
  buildEditAction,
  buildDeleteAction,
  buildToggleAction,
} from "@/shared/components";
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

  function DialogueCard({
    dialogue,
    onEdit,
    onToggleActive,
    onDelete,
    t,
  }: {
    dialogue: DialogueRow;
    onEdit: (d: DialogueRow) => void;
    onToggleActive: (id: number, isActive: boolean) => void;
    onDelete: (id: number, title: string) => void;
    t: (key: string) => string;
  }) {
    return (
      <Card
        className="cursor-pointer transition-colors hover:bg-muted/50"
        onClick={() => onEdit(dialogue)}
      >
        <CardContent className="p-4">
          {/* Header: Title + Status */}
          <div className="mb-3 flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted">
              <MessageSquare className="size-4 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="truncate font-semibold">{dialogue.title}</h3>
                {dialogue.isActive ? (
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                    <CheckCircle2 className="size-3" />
                    {t("dialogues.activeStatus")}
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    <XCircle className="size-3" />
                    {t("dialogues.inactiveStatus")}
                  </span>
                )}
              </div>
              {dialogue.description && (
                <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                  {dialogue.description}
                </p>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                  CATEGORY_COLORS[dialogue.category] ?? "bg-muted text-muted-foreground",
                )}
              >
                {getCategoryLabel(dialogue.category)}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <ListOrdered className="size-3 text-muted-foreground" />
              <span className="text-muted-foreground">{t("dialogues.stepsCount")}: </span>
              <span>{dialogue.stepsCount}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(dialogue)}>
              {t("common.edit")}
            </Button>
            <Button
              size="sm"
              variant="outline"
              className={cn(
                "flex-1",
                dialogue.isActive
                  ? "text-amber-500 hover:text-amber-600"
                  : "text-emerald-500 hover:text-emerald-600",
              )}
              onClick={() => onToggleActive(dialogue.id, !dialogue.isActive)}
            >
              {dialogue.isActive ? t("common.deactivate") : t("common.activate")}
            </Button>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => onDelete(dialogue.id, dialogue.title)}
            >
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mobileView = (
    <div className="space-y-3 p-4">
      {dialogues.map((d) => (
        <DialogueCard
          key={d.id}
          dialogue={d}
          onEdit={handleEdit}
          onToggleActive={onToggleActive}
          onDelete={handleDelete}
          t={t}
        />
      ))}
    </div>
  );

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
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
                {t("dialogues.title")}{" "}
                <span className="text-sm font-normal text-muted-foreground">
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
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <SearchInput
                placeholder={t("dialogues.searchDialogues")}
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
              <Select
                value={categoryFilter}
                onChange={onCategoryFilterChange}
                options={categoryOptions}
                className="w-full sm:w-auto"
              />
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead
              field="title"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("dialogues.name")}
            </SortableTableHead>
            <SortableTableHead
              field="category"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("dialogues.category")}
            </SortableTableHead>
            <SortableTableHead
              field="stepsCount"
              sortable={false}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("dialogues.stepsCount")}
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
            <TableHead className="w-28">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dialogues.map((d) => (
            <TableRow
              key={d.id}
              className="cursor-pointer transition-colors hover:bg-muted"
              onClick={() => handleEdit(d)}
            >
              <TableCell>
                <div className="flex items-start gap-3">
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <MessageSquare className="size-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="leading-none font-medium">{d.title}</p>
                    {d.description && (
                      <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
                        {d.description}
                      </p>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                    CATEGORY_COLORS[d.category] ?? "bg-muted text-muted-foreground",
                  )}
                >
                  {getCategoryLabel(d.category)}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <ListOrdered className="size-3.5 text-muted-foreground" />
                  {d.stepsCount}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  {d.isActive ? (
                    <>
                      <CheckCircle2 className="size-4 text-emerald-500" />
                      <span className="text-xs text-emerald-600 dark:text-emerald-400">
                        {t("dialogues.activeStatus")}
                      </span>
                    </>
                  ) : (
                    <>
                      <XCircle className="size-4 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        {t("dialogues.inactiveStatus")}
                      </span>
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
