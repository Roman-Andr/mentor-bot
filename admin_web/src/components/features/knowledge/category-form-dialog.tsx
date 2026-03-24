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
  const isEdit = mode === "edit";

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>
          {isEdit ? "Редактирование категории" : "Создание категории"}
        </DialogTitle>
        <DialogDescription>
          {isEdit
            ? "Измените категорию в базе знаний"
            : "Создайте новую категорию в базе знаний"}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">Название *</label>
          <Input
            placeholder="Название категории"
            value={formData.name}
            onChange={(e) => onFormDataChange("name", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Slug</label>
          <Input
            placeholder="category-slug"
            value={formData.slug}
            onChange={(e) => onFormDataChange("slug", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Описание</label>
          <Textarea
            placeholder="Описание категории"
            value={formData.description}
            onChange={(e) => onFormDataChange("description", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Родительская категория</label>
            <Select
              value={formData.parent_id}
              onChange={(e) => onFormDataChange("parent_id", parseInt(e.target.value))}
              placeholder="Нет"
              options={[
                { value: "0", label: "Нет" },
                ...categories
                  .filter((c) => c.id !== formData.parent_id)
                  .map((cat) => ({ value: String(cat.id), label: cat.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Порядок</label>
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
            <label className="text-sm font-medium">Отдел</label>
            <Select
              value={formData.department_id}
              onChange={(e) => onFormDataChange("department_id", parseInt(e.target.value) || 0)}
              placeholder="Все"
              options={[
                { value: "0", label: "Все" },
                ...departments.map((d) => ({ value: String(d.id), label: d.name })),
              ]}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Должность</label>
            <Input
              placeholder="Например: Developer"
              value={formData.position}
              onChange={(e) => onFormDataChange("position", e.target.value)}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Уровень</label>
            <Select
              value={formData.level}
              onChange={(e) => onFormDataChange("level", e.target.value)}
              placeholder="Любой"
              options={LEVELS_WITH_EMPTY.map((l) => ({ value: l.value, label: l.label }))}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Иконка</label>
            <Input
              placeholder="Название иконки"
              value={formData.icon}
              onChange={(e) => onFormDataChange("icon", e.target.value)}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Цвет</label>
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
          Отмена
        </Button>
        <Button onClick={onSubmit} disabled={!formData.name}>
          {isEdit ? "Сохранить" : "Создать"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}
