import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/use-translations";
import type { DialogueCategory } from "@/types";

const CATEGORY_OPTIONS: { value: DialogueCategory; label: string }[] = [
  { value: "VACATION", label: "Vacation & Time Off" },
  { value: "ACCESS", label: "Passes & Access" },
  { value: "BENEFITS", label: "Benefits" },
  { value: "CONTACTS", label: "Contacts" },
  { value: "WORKTIME", label: "Work Time" },
];

interface DialogueMetadataFormProps {
  title: string;
  category: DialogueCategory;
  description: string;
  keywords: string;
  displayOrder: number;
  isActive: boolean;
  onTitleChange: (value: string) => void;
  onCategoryChange: (value: DialogueCategory) => void;
  onDescriptionChange: (value: string) => void;
  onKeywordsChange: (value: string) => void;
  onDisplayOrderChange: (value: number) => void;
  onIsActiveChange: (value: boolean) => void;
  onSave: () => void;
  isSaving: boolean;
}

export function DialogueMetadataForm({
  title,
  category,
  description,
  keywords,
  displayOrder,
  isActive,
  onTitleChange,
  onCategoryChange,
  onDescriptionChange,
  onKeywordsChange,
  onDisplayOrderChange,
  onIsActiveChange,
  onSave,
  isSaving,
}: DialogueMetadataFormProps) {
  const t = useTranslations();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("dialogues.generalInfo")}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.title_field")} *</label>
            <Input
              value={title}
              onChange={(e) => onTitleChange(e.target.value)}
              placeholder={t("dialogues.title_field")}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.category")} *</label>
            <Select
              options={CATEGORY_OPTIONS}
              value={category}
              onChange={(v) => onCategoryChange(v as DialogueCategory)}
            />
          </div>
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("dialogues.description")}</label>
          <Textarea
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            placeholder={t("dialogues.description")}
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.keywords")}</label>
            <Input
              value={keywords}
              onChange={(e) => onKeywordsChange(e.target.value)}
              placeholder="key1, key2, key3"
            />
            <p className="text-muted-foreground text-xs">{t("dialogues.keywordsHint")}</p>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.displayOrder")}</label>
            <Input
              type="number"
              value={displayOrder}
              onChange={(e) => onDisplayOrderChange(parseInt(e.target.value) || 0)}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_active"
            checked={isActive}
            onChange={(e) => onIsActiveChange(e.target.checked)}
          />
          <label htmlFor="is_active" className="text-sm">
            {t("dialogues.isActive")}
          </label>
        </div>

        <div className="flex justify-end">
          <Button onClick={onSave} disabled={!title || !category || isSaving}>
            {t("common.save")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
