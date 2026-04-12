"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import {
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { LEVELS_WITH_EMPTY } from "@/lib/constants";
import type { CategoryFormData } from "@/hooks/use-categories";

interface CategoryFormDialogProps {
  mode: "create" | "edit";
  formData: CategoryFormData;
  onFormDataChange: (field: keyof CategoryFormData, value: string | number) => void;
  categories: { id: number; name: string }[];
  departments?: { id: number; name: string }[];
  onSubmit: () => void;
  onCancel: () => void;
}

export function CategoryFormDialog({
  mode,
  formData,
  onFormDataChange,
  categories,
  departments = [],
  onSubmit,
  onCancel,
}: CategoryFormDialogProps) {
  const t = useTranslations();

  const isEdit = mode === "edit";

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("knowledge.editCategoryTitle") : t("knowledge.addCategoryTitle")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("knowledge.changeCategory") : t("knowledge.createNewCategory")}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.name")} *</label>
          <Input
            placeholder={t("knowledge.name")}
            value={formData.name}
            onChange={(e) => onFormDataChange("name", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.slug")}</label>
          <Input
            placeholder="category-slug"
            value={formData.slug}
            onChange={(e) => onFormDataChange("slug", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("common.description")}</label>
          <Textarea
            placeholder={t("common.description")}
            value={formData.description}
            onChange={(e) => onFormDataChange("description", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.parentCategory")}</label>
            <Select
              value={formData.parent_id ? String(formData.parent_id) : ""}
              onChange={(val) => onFormDataChange("parent_id", parseInt(val) || 0)}
              placeholder={t("knowledge.noCategory")}
              options={[
                { value: "0", label: t("knowledge.noCategory") },
                ...categories
                  .filter((c) => c.id !== formData.parent_id)
                  .map((cat) => ({ value: String(cat.id), label: cat.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.order")}</label>
            <Input
              type="number"
              min={0}
              value={formData.order}
              onChange={(e) => onFormDataChange("order", parseInt(e.target.value) || 0)}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("common.department")}</label>
            <Select
              value={formData.department_id ? String(formData.department_id) : ""}
              onChange={(val) => onFormDataChange("department_id", parseInt(val) || 0)}
              placeholder={t("common.all")}
              options={[
                { value: "0", label: t("common.all") },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.position")}</label>
            <Input
              placeholder="e.g., Developer"
              value={formData.position}
              onChange={(e) => onFormDataChange("position", e.target.value)}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.level")}</label>
            <Select
              value={formData.level || ""}
              onChange={(val) => onFormDataChange("level", val)}
              placeholder={t("common.all")}
              options={LEVELS_WITH_EMPTY.map((l) => ({ value: l.value, label: l.label }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.icon")}</label>
            <Input
              placeholder="Icon name"
              value={formData.icon}
              onChange={(e) => onFormDataChange("icon", e.target.value)}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.color")}</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={formData.color || "#6366f1"}
              onChange={(e) => onFormDataChange("color", e.target.value)}
              className="border-input h-9 w-12 cursor-pointer rounded border"
            />
            <Input
              placeholder="#6366f1"
              value={formData.color}
              onChange={(e) => onFormDataChange("color", e.target.value)}
            />
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          {t("common.cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={!formData.name}>
          {isEdit ? t("common.save") : t("common.create")}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}