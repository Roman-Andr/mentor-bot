"use client";

import { useMemo } from "react";
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
import type { Category, Attachment } from "@/types";
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

const articleStatusValues = ARTICLE_STATUSES.filter((s) => s.value !== "ALL");

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
  const t = useTranslations();

  const isEdit = mode === "edit";

  const articleStatuses = useMemo(() => {
    const statusLabels: Record<string, string> = {
      PUBLISHED: t("knowledge.published"),
      DRAFT: t("knowledge.draft"),
    };
    return articleStatusValues.map((s) => ({
      value: s.value,
      label: statusLabels[s.value] ?? s.value,
    }));
  }, [t]);

  const update = (field: keyof ArticleFormData, value: string | number | boolean) => {
    onFormDataChange({ ...formData, [field]: value });
  };

  return (
    <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("knowledge.editArticleTitle") : t("knowledge.addArticleTitle")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("knowledge.changeArticle") : t("knowledge.createNewArticle")}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.articleTitle")} *</label>
          <Input
            placeholder={t("knowledge.articleTitle")}
            value={formData.title}
            onChange={(e) => update("title", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.excerpt")}</label>
          <Textarea
            placeholder={t("knowledge.excerpt")}
            value={formData.excerpt}
            onChange={(e) => update("excerpt", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.content")}</label>
          <Textarea
            placeholder={t("knowledge.articleContent")}
            value={formData.content}
            onChange={(e) => update("content", e.target.value)}
            className="min-h-[200px]"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.category")}</label>
            <Select
              value={formData.category_id ? String(formData.category_id) : ""}
              onChange={(val) => update("category_id", parseInt(val))}
              placeholder={t("knowledge.selectCategory")}
              options={categories.map((cat) => ({ value: String(cat.id), label: cat.name }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("common.status")}</label>
            <Select
              value={formData.status}
              onChange={update.bind(null, "status")}
              options={articleStatuses}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("common.department")}</label>
            <Select
              value={formData.department_id ? String(formData.department_id) : ""}
              onChange={(val) => update("department_id", parseInt(val) || 0)}
              placeholder={t("common.notSelected")}
              options={[
                { value: "0", label: t("common.notSelected") },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.position")}</label>
            <Input
              placeholder="e.g., Developer"
              value={formData.position}
              onChange={(e) => update("position", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("knowledge.level")}</label>
            <Select
              value={formData.level || ""}
              onChange={(val) => update("level", val)}
              placeholder={t("common.all")}
              options={LEVELS}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("knowledge.keywords")}</label>
          <Input
            placeholder={t("knowledge.keywordsPlaceholder")}
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
            <span className="text-sm">{t("knowledge.pin")}</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) => update("is_featured", e.target.checked)}
              className="border-input rounded"
            />
            <span className="text-sm">{t("knowledge.featured")}</span>
          </label>
        </div>
        <div className="grid gap-3 rounded-md border p-3">
          <label className="text-sm font-medium">{t("knowledge.attachments")}</label>
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
          {t("common.cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={!formData.title}>
          {isEdit ? t("common.save") : t("common.create")}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}