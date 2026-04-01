"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Select } from "@/components/ui/select";
import type { DialogueFormData } from "@/hooks/use-dialogues";
import type { DialogueCategory } from "@/lib/api";

function getCategoryOptions(t: (key: string) => string): { value: DialogueCategory; label: string }[] {
  return [
    { value: "VACATION", label: t("vacation") },
    { value: "ACCESS", label: t("access") },
    { value: "BENEFITS", label: t("benefits") },
    { value: "CONTACTS", label: t("contacts") },
    { value: "WORKTIME", label: t("worktime") },
  ];
}

interface DialogueFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  formData: DialogueFormData;
  onFormDataChange: (data: DialogueFormData) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

export function DialogueFormDialog({
  open,
  onOpenChange,
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
}: DialogueFormDialogProps) {
  const t = useTranslations("dialogues");
  const isCreate = mode === "create";

  const categoryOptions = getCategoryOptions(t);

  const handleSubmit = () => {
    onSubmit();
  };

  const handleCancel = () => {
    onCancel();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isCreate ? t("createDialogue") : t("editDialogueTitle")}</DialogTitle>
          <DialogDescription>
            {isCreate ? t("createNewDialogue") : t("changeDialogueParams")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("title_field")} *</label>
            <Input
              value={formData.title}
              onChange={(e) => onFormDataChange({ ...formData, title: e.target.value })}
              placeholder={t("title_field")}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("description")}</label>
            <Textarea
              value={formData.description}
              onChange={(e) => onFormDataChange({ ...formData, description: e.target.value })}
              placeholder={t("description")}
              rows={3}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("keywords")}</label>
            <Input
              value={formData.keywords}
              onChange={(e) => onFormDataChange({ ...formData, keywords: e.target.value })}
              placeholder="key1, key2, key3"
            />
            <p className="text-muted-foreground text-xs">{t("keywordsHint")}</p>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("category")} *</label>
            <Select
              options={categoryOptions}
              value={formData.category}
              onChange={(value) =>
                onFormDataChange({ ...formData, category: value as DialogueCategory })
              }
              placeholder={t("selectCategory") || t("category")}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("displayOrder")}</label>
            <Input
              type="number"
              value={formData.display_order}
              onChange={(e) =>
                onFormDataChange({ ...formData, display_order: parseInt(e.target.value) || 0 })
              }
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => onFormDataChange({ ...formData, is_active: e.target.checked })}
            />
            <label htmlFor="is_active" className="text-sm">
              {t("isActive")}
            </label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel}>
            {t("cancel")}
          </Button>
          <Button onClick={handleSubmit} disabled={!formData.title || !formData.category}>
            {isCreate ? t("create") : t("save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
