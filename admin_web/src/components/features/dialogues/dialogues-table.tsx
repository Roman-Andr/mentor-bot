"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { cn } from "@/lib/utils";
import { Edit, Trash2, Power, Search } from "lucide-react";
import { Select } from "@/components/ui/select";
import type { DialogueRow } from "@/hooks/use-dialogues";

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
    { value: "ALL", label: t("allCategories") },
    { value: "VACATION", label: t("vacation") },
    { value: "ACCESS", label: t("access") },
    { value: "BENEFITS", label: t("benefits") },
    { value: "CONTACTS", label: t("contacts") },
    { value: "WORKTIME", label: t("worktime") },
  ];
}

interface DialoguesTableProps {
  dialogues: DialogueRow[];
  loading: boolean;
  onEdit: (d: DialogueRow) => void;
  onDelete: (id: number) => void;
  onToggleActive: (id: number, isActive: boolean) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (category: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  onPageChange: (page: number) => void;
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
  onPageChange,
}: DialoguesTableProps) {
  const t = useTranslations("dialogues");
  const tCommon = useTranslations("common");
  const confirm = useConfirm();

  const categoryOptions = getCategoryOptions(t);

  const handleDelete = async (id: number, title: string) => {
    if (
      !(await confirm({
        title: t("deleteDialogue"),
        description: tCommon("confirmDelete").replace("item", `"${title}"`),
        variant: "destructive",
        confirmText: tCommon("delete"),
      }))
    )
      return;
    onDelete(id);
  };

  return (
    <div>
      <div className="mb-4 flex gap-4">
        <div className="relative flex-1">
          <Search className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
          <Input
            className="pl-9"
            placeholder={t("searchDialogues")}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
        <Select
          options={categoryOptions}
          value={categoryFilter}
          onChange={onCategoryFilterChange}
          className="w-48"
        />
      </div>

      <div className="rounded-md border">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="p-3 text-left text-sm font-medium">{t("name")}</th>
              <th className="p-3 text-left text-sm font-medium">{t("category")}</th>
              <th className="p-3 text-left text-sm font-medium">{t("stepsCount")}</th>
              <th className="p-3 text-left text-sm font-medium">{tCommon("status")}</th>
              <th className="p-3 text-left text-sm font-medium">{tCommon("actions")}</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="text-muted-foreground p-8 text-center">
                  {t("loading")}
                </td>
              </tr>
            ) : dialogues.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-muted-foreground p-8 text-center">
                  {t("noDialogues")}
                </td>
              </tr>
            ) : (
              dialogues.map((d) => (
                <tr key={d.id} className="border-t">
                  <td className="p-3">
                    <div className="font-medium">{d.title}</div>
                    <div className="text-muted-foreground text-sm">{d.description}</div>
                  </td>
                  <td className="p-3">{getCategoryLabel(d.category)}</td>
                  <td className="p-3">{d.stepsCount}</td>
                  <td className="p-3">
                    <span
                      className={cn(
                        "rounded px-2 py-1 text-xs",
                        d.isActive ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700",
                      )}
                    >
                      {d.isActive ? t("activeStatus") : t("inactiveStatus")}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex gap-1">
                      <Button size="icon" variant="ghost" onClick={() => onEdit(d)}>
                        <Edit className="size-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => onToggleActive(d.id, !d.isActive)}
                      >
                        <Power
                          className={cn(
                            "size-4",
                            d.isActive ? "text-orange-500" : "text-green-500",
                          )}
                        />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handleDelete(d.id, d.title)}
                      >
                        <Trash2 className="size-4 text-red-500" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div className="text-muted-foreground text-sm">
            {t("total")}: {totalCount}, {t("page")} {currentPage} {t("of")} {totalPages}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onClick={() => onPageChange(currentPage - 1)}
            >
              {t("back")}
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onClick={() => onPageChange(currentPage + 1)}
            >
              {t("forward")}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
