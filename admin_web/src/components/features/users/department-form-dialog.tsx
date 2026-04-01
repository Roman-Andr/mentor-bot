"use client";

import { useTranslations } from "next-intl";
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
  const t = useTranslations("departments");
  const tCommon = useTranslations("common");
  const isEdit = mode === "edit";

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("editDepartment") : t("addDepartment")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("editDepartment") : t("addDepartment")}
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
          <label className="text-sm font-medium">{tCommon("description")}</label>
          <Textarea
            placeholder={tCommon("description")}
            value={formData.description}
            onChange={(e) => onFormDataChange("description", e.target.value)}
          />
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