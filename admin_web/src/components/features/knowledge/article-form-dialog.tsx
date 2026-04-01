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
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");

  const isEdit = mode === "edit";

  const update = (field: keyof ArticleFormData, value: string | number | boolean) => {
    onFormDataChange({ ...formData, [field]: value });
  };

  return (
    <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{isEdit ? t("editArticleTitle") : t("addArticleTitle")}</DialogTitle>
        <DialogDescription>
          {isEdit ? t("changeArticle") : t("createNewArticle")}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("articleTitle")} *</label>
          <Input
            placeholder={t("articleTitle")}
            value={formData.title}
            onChange={(e) => update("title", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("excerpt")}</label>
          <Textarea
            placeholder={t("excerpt")}
            value={formData.excerpt}
            onChange={(e) => update("excerpt", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("content")}</label>
          <Textarea
            placeholder={t("articleContent")}
            value={formData.content}
            onChange={(e) => update("content", e.target.value)}
            className="min-h-[200px]"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("category")}</label>
            <Select
              value={formData.category_id ? String(formData.category_id) : ""}
              onChange={(val) => update("category_id", parseInt(val))}
              placeholder={t("selectCategory")}
              options={categories.map((cat) => ({ value: String(cat.id), label: cat.name }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{tCommon("status")}</label>
            <Select
              value={formData.status}
              onChange={update.bind(null, "status")}
              options={articleStatuses}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{tCommon("department")}</label>
            <Select
              value={formData.department_id ? String(formData.department_id) : ""}
              onChange={(val) => update("department_id", parseInt(val) || 0)}
              placeholder={tCommon("notSelected")}
              options={[
                { value: "0", label: tCommon("notSelected") },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("position")}</label>
            <Input
              placeholder="e.g., Developer"
              value={formData.position}
              onChange={(e) => update("position", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("level")}</label>
            <Select
              value={formData.level || ""}
              onChange={(val) => update("level", val)}
              placeholder={tCommon("all")}
              options={LEVELS}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("keywords")}</label>
          <Input
            placeholder={t("keywordsPlaceholder")}
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
            <span className="text-sm">{t("pin")}</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) => update("is_featured", e.target.checked)}
              className="border-input rounded"
            />
            <span className="text-sm">{t("featured")}</span>
          </label>
        </div>
        <div className="grid gap-3 rounded-md border p-3">
          <label className="text-sm font-medium">{t("attachments")}</label>
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
          {tCommon("cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={!formData.title}>
          {isEdit ? tCommon("save") : tCommon("create")}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}