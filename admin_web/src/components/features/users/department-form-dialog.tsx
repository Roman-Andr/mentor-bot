"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { DepartmentFormData } from "@/hooks/use-departments";

interface DepartmentFormDialogProps {
  mode: "create" | "edit";
  formData: DepartmentFormData;
  onFormDataChange: (field: keyof DepartmentFormData, value: string) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

export function DepartmentFormDialog({
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
}: DepartmentFormDialogProps) {
  const t = useTranslations();
  const isEdit = mode === "edit";

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("departments.editDepartment") : t("departments.addDepartment")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("departments.editDepartment") : t("departments.addDepartment")}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("departments.name")} *</label>
          <Input
            placeholder={t("departments.name")}
            value={formData.name}
            onChange={(e) => onFormDataChange("name", e.target.value)}
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