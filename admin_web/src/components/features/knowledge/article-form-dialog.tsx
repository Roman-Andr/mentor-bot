"use client";

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
import { type Category, type Attachment } from "@/lib/api";
import { ARTICLE_STATUSES, LEVELS } from "@/lib/constants";
import type { ArticleFormData } from "@/hooks/use-articles";
import { AttachmentManager } from "./attachment-manager";

interface ArticleFormDialogProps {
  mode: "create" | "edit";
  formData: ArticleFormData;
  onFormDataChange: (data: ArticleFormData) => void;
  categories: Category[];
  departments?: { id: number; name: string }[];
  articleId: number | null;
  attachments: Attachment[];
  onAttachmentsChange: (attachments: Attachment[]) => void;
  pendingFiles?: File[];
  onPendingFilesChange?: (files: File[]) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

const articleStatuses = ARTICLE_STATUSES.filter((s) => s.value !== "ALL");

export function ArticleFormDialog({
  mode,
  formData,
  onFormDataChange,
  categories,
  departments = [],
  articleId,
  attachments,
  onAttachmentsChange,
  pendingFiles,
  onPendingFilesChange,
  onSubmit,
  onCancel,
}: ArticleFormDialogProps) {
  const isEdit = mode === "edit";

  const update = (field: keyof ArticleFormData, value: string | number | boolean) => {
    onFormDataChange({ ...formData, [field]: value });
  };

  return (
    <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? "Редактирование статьи" : "Создание статьи"}</DialogTitle>
        <DialogDescription>
          {isEdit ? "Измените статью в базе знаний" : "Создайте новую статью в базе знаний"}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">Заголовок *</label>
          <Input
            placeholder="Заголовок статьи"
            value={formData.title}
            onChange={(e) => update("title", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Краткое описание</label>
          <Textarea
            placeholder="Краткое описание для списка статей"
            value={formData.excerpt}
            onChange={(e) => update("excerpt", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Содержание</label>
          <Textarea
            placeholder="Полный текст статьи (поддерживается Markdown)"
            value={formData.content}
            onChange={(e) => update("content", e.target.value)}
            className="min-h-[200px]"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Категория</label>
            <Select
              value={formData.category_id}
              onChange={(e) => update("category_id", parseInt(e.target.value))}
              placeholder="Выберите категорию"
              options={categories.map((cat) => ({ value: String(cat.id), label: cat.name }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Статус</label>
            <Select
              value={formData.status}
              onChange={(e) => update("status", e.target.value)}
              options={articleStatuses}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Отдел</label>
            <Select
              value={formData.department_id}
              onChange={(e) => update("department_id", parseInt(e.target.value) || 0)}
              placeholder="Выберите отдел"
              options={[
                { value: "0", label: "Не указан" },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Должность</label>
            <Input
              placeholder="Например: Developer"
              value={formData.position}
              onChange={(e) => update("position", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Уровень</label>
            <Select
              value={formData.level}
              onChange={(e) => update("level", e.target.value)}
              placeholder="Любой"
              options={LEVELS}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Ключевые слова</label>
          <Input
            placeholder="Ключевые слова через запятую"
            value={formData.keywords}
            onChange={(e) => update("keywords", e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_pinned}
              onChange={(e) => update("is_pinned", e.target.checked)}
               className="border-input rounded"
            />
            <span className="text-sm">Закрепить</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) => update("is_featured", e.target.checked)}
               className="border-input rounded"
            />
            <span className="text-sm">Избранное</span>
          </label>
        </div>
        <div className="grid gap-3 rounded-md border p-3">
          <label className="text-sm font-medium">Файлы и вложения</label>
          <AttachmentManager
            articleId={articleId}
            attachments={attachments}
            onAttachmentsChange={onAttachmentsChange}
            pendingFiles={pendingFiles}
            onPendingFilesChange={onPendingFilesChange}
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Отмена
        </Button>
        <Button onClick={onSubmit} disabled={!formData.title}>
          {isEdit ? "Сохранить" : "Создать"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}
