"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
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
import { useConfirm } from "@/hooks/use-confirm";
import { cn } from "@/lib/utils";
import { TableActions, buildEditAction, buildDeleteAction, buildToggleAction } from "@/components/shared";
import { useRouter } from "next/navigation";
import type { DialogueRow } from "@/hooks/use-dialogues";
import type { SortDirection } from "@/hooks/use-sorting";

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
  onEdit,
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

  const columns = [
    { key: "title", label: t("dialogues.name"), sortable: true },
    { key: "category", label: t("dialogues.category"), sortable: true },
    { key: "stepsCount", label: t("dialogues.stepsCount"), sortable: false },
    { key: "isActive", label: t("common.status"), sortable: true },
  ];

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
          <div className="flex items-center justify-between">
            <CardTitle>
              {t("dialogues.title")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({totalCount ?? dialogues.length})
              </span>
            </CardTitle>
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
          {dialogues.map((d) => (
            <TableRow key={d.id} className="hover:bg-muted cursor-pointer" onClick={() => handleEdit(d)}>
              <TableCell>
                <div>
                  <p className="font-medium">{d.title}</p>
                  <p className="text-muted-foreground text-sm">{d.description}</p>
                </div>
              </TableCell>
              <TableCell>{getCategoryLabel(d.category)}</TableCell>
              <TableCell>{d.stepsCount}</TableCell>
              <TableCell>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                    d.isActive
                      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400",
                  )}
                >
                  {d.isActive ? t("dialogues.activeStatus") : t("dialogues.inactiveStatus")}
                </span>
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
                      color: d.isActive ? "text-orange-500" : "text-green-500",
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
