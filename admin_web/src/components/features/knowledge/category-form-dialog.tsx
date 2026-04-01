"use client";

import { useTranslations } from "next-intl";
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
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");

  const isEdit = mode === "edit";

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("editCategoryTitle") : t("addCategoryTitle")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("changeCategory") : t("createNewCategory")}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("name")} *</label>
          <Input
            placeholder={t("name")}
            value={formData.name}
            onChange={(e) => onFormDataChange("name", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("slug")}</label>
          <Input
            placeholder="category-slug"
            value={formData.slug}
            onChange={(e) => onFormDataChange("slug", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{tCommon("description")}</label>
          <Textarea
            placeholder={tCommon("description")}
            value={formData.description}
            onChange={(e) => onFormDataChange("description", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("parentCategory")}</label>
            <Select
              value={formData.parent_id ? String(formData.parent_id) : ""}
              onChange={(val) => onFormDataChange("parent_id", parseInt(val) || 0)}
              placeholder={t("noCategory")}
              options={[
                { value: "0", label: t("noCategory") },
                ...categories
                  .filter((c) => c.id !== formData.parent_id)
                  .map((cat) => ({ value: String(cat.id), label: cat.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("order")}</label>
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
            <label className="text-sm font-medium">{tCommon("department")}</label>
            <Select
              value={formData.department_id ? String(formData.department_id) : ""}
              onChange={(val) => onFormDataChange("department_id", parseInt(val) || 0)}
              placeholder={tCommon("all")}
              options={[
                { value: "0", label: tCommon("all") },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("position")}</label>
            <Input
              placeholder="e.g., Developer"
              value={formData.position}
              onChange={(e) => onFormDataChange("position", e.target.value)}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("level")}</label>
            <Select
              value={formData.level || ""}
              onChange={(val) => onFormDataChange("level", val)}
              placeholder={tCommon("all")}
              options={LEVELS_WITH_EMPTY.map((l) => ({ value: l.value, label: l.label }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("icon")}</label>
            <Input
              placeholder="Icon name"
              value={formData.icon}
              onChange={(e) => onFormDataChange("icon", e.target.value)}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("color")}</label>
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
          {tCommon("cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={!formData.name}>
          {isEdit ? tCommon("save") : tCommon("create")}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}