"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DepartmentDocumentUploadZone } from "./department-document-upload-zone";
import { DOCUMENT_CATEGORIES } from "@/lib/constants";
import { useDepartments } from "@/hooks/use-departments";

interface DepartmentDocumentFormDialogProps {
  mode: "create" | "edit";
  formData: {
    department_id: number;
    title: string;
    description: string;
    category: string;
    is_public: boolean;
    file?: File;
  };
  onFormDataChange: (field: string, value: any) => void;
  onSubmit: () => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function DepartmentDocumentFormDialog({
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
  isSubmitting,
}: DepartmentDocumentFormDialogProps) {
  const t = useTranslations();
  const isEdit = mode === "edit";
  const { items: departments } = useDepartments();

  return (
    <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? "Редактировать документ" : "Добавить документ"}</DialogTitle>
        <DialogDescription>
          {isEdit ? "Измените информацию о документе" : "Загрузите новый документ для департамента"}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        {!isEdit && (
          <div className="grid gap-2">
            <Label>Файл *</Label>
            <DepartmentDocumentUploadZone
              onFileSelect={(file) => onFormDataChange("file", file)}
            />
            {formData.file && (
              <p className="text-sm text-muted-foreground">Выбран: {formData.file.name}</p>
            )}
          </div>
        )}
        <div className="grid gap-2">
          <Label htmlFor="department">Департамент *</Label>
          <Select
            id="department"
            options={departments.map((dept) => ({ value: dept.id.toString(), label: dept.name }))}
            value={formData.department_id.toString()}
            onChange={(value) => onFormDataChange("department_id", parseInt(value, 10))}
            placeholder="Выберите департамент"
            disabled={isEdit}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="title">Название *</Label>
          <Input
            id="title"
            placeholder="Название документа"
            value={formData.title}
            onChange={(e) => onFormDataChange("title", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="category">Категория *</Label>
          <Select
            id="category"
            options={DOCUMENT_CATEGORIES}
            value={formData.category}
            onChange={(value) => onFormDataChange("category", value)}
            placeholder="Выберите категорию"
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="description">Описание</Label>
          <Textarea
            id="description"
            placeholder="Описание документа"
            value={formData.description}
            onChange={(e) => onFormDataChange("description", e.target.value)}
            rows={3}
          />
        </div>
        <div className="flex items-center gap-2">
          <Checkbox
            id="is_public"
            checked={formData.is_public}
            onCheckedChange={(checked) => onFormDataChange("is_public", checked)}
          />
          <Label htmlFor="is_public" className="cursor-pointer">
            Публичный документ (доступен всем)
          </Label>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          {t("common.cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={isSubmitting || (!isEdit && !formData.file)}>
          {isSubmitting ? "Сохранение..." : isEdit ? t("common.save") : "Загрузить"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}
