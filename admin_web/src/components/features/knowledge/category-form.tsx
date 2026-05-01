import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useTranslations } from "@/hooks/use-translations";
import type { CategoryRow, CategoryFormData } from "@/hooks/use-categories";

interface CategoryFormProps {
  formData: CategoryFormData;
  onChange: (data: CategoryFormData) => void;
  categories: CategoryRow[];
  departments: { id: number; name: string }[];
  isEdit?: boolean;
}

export function CategoryForm({ formData, onChange, categories, departments, isEdit }: CategoryFormProps) {
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");

  // Filter out the current category and its children to prevent circular references
  const availableParents = isEdit
    ? categories.filter((c) => c.id !== (formData as { id?: number }).id)
    : categories;

  const parentOptions = [
    { value: "0", label: tCommon("notSelected") ?? "Not selected" },
    ...availableParents.map((c) => ({
      value: String(c.id),
      label: c.parent_id ? `— ${c.name}` : c.name,
    })),
  ];

  const departmentOptions = [
    { value: "0", label: tCommon("notSelected") ?? "Not selected" },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  const handleChange = (field: keyof CategoryFormData, value: string | number) => {
    onChange({ ...formData, [field]: value });
  };

  return (
    <div className="grid gap-4 py-4">
      <div className="grid gap-2">
        <label className="text-sm font-medium">{t("name")} *</label>
        <Input
          placeholder={t("name") ?? "Name"}
          value={formData.name}
          onChange={(e) => handleChange("name", e.target.value)}
        />
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium">{t("slug")}</label>
        <Input
          placeholder={t("slug") ?? "Slug"}
          value={formData.slug}
          onChange={(e) => handleChange("slug", e.target.value)}
          disabled={isEdit}
        />
        {isEdit && (
          <p className="text-muted-foreground text-xs">{t("slugImmutable")}</p>
        )}
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium">{tCommon("description")}</label>
        <Textarea
          placeholder={tCommon("description") ?? "Description"}
          value={formData.description}
          onChange={(e) => handleChange("description", e.target.value)}
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("parentCategory")}</label>
          <Select
            value={formData.parent_id ? String(formData.parent_id) : "0"}
            onChange={(val) => handleChange("parent_id", parseInt(val) || 0)}
            options={parentOptions}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{tCommon("department")}</label>
          <Select
            value={formData.department_id ? String(formData.department_id) : "0"}
            onChange={(val) => handleChange("department_id", parseInt(val) || 0)}
            options={departmentOptions}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("position")}</label>
          <Input
            placeholder={t("position") ?? "Position"}
            value={formData.position}
            onChange={(e) => handleChange("position", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("level")}</label>
          <Input
            placeholder={t("level") ?? "Level"}
            value={formData.level}
            onChange={(e) => handleChange("level", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("order")}</label>
          <Input
            type="number"
            value={formData.order}
            onChange={(e) => handleChange("order", parseInt(e.target.value) || 0)}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("icon")}</label>
          <Input
            placeholder={t("icon") ?? "Icon (e.g. Folder)"}
            value={formData.icon}
            onChange={(e) => handleChange("icon", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("color")}</label>
          <div className="flex items-center gap-2">
            <Input
              placeholder="#3b82f6"
              value={formData.color}
              onChange={(e) => handleChange("color", e.target.value)}
            />
            {formData.color && (
              <span
                className="inline-block size-9 shrink-0 rounded-md border"
                style={{ backgroundColor: formData.color }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
