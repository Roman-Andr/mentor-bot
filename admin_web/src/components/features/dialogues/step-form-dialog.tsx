"use client";

import { useTranslations } from "@/hooks/use-translations";
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
import { Trash2, Plus, GripVertical } from "lucide-react";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { StepFormData } from "@/hooks/use-dialogue-edit";
import type { DialogueAnswerType, DialogueStep } from "@/types";

const ANSWER_TYPE_OPTIONS: { value: DialogueAnswerType; label: string }[] = [
  { value: "TEXT", label: "Text" },
  { value: "CHOICE", label: "Choice" },
  { value: "LINK", label: "Link" },
];

interface SortableOptionRowProps {
  idx: number;
  opt: { label: string; next_step: number };
  stepNumberOptions: { value: string; label: string }[];
  onUpdate: (idx: number, field: "label" | "next_step", value: string | number) => void;
  onRemove: (idx: number) => void;
  optionLabelPlaceholder: string;
}

function SortableOptionRow({ idx, opt, stepNumberOptions, onUpdate, onRemove, optionLabelPlaceholder }: SortableOptionRowProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: idx });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 };

  return (
    <div ref={setNodeRef} style={style} className="flex gap-2 items-center">
      <button
        {...attributes}
        {...listeners}
        type="button"
        className="text-gray-400 cursor-grab active:cursor-grabbing shrink-0"
        tabIndex={-1}
      >
        <GripVertical className="size-4" />
      </button>
      <Input
        value={opt.label}
        onChange={(e) => onUpdate(idx, "label", e.target.value)}
        placeholder={optionLabelPlaceholder}
        className="flex-1"
      />
      <div className="w-52 shrink-0">
        <Select
          options={stepNumberOptions}
          value={String(opt.next_step || 0)}
          onChange={(v) => onUpdate(idx, "next_step", parseInt(v) || 0)}
        />
      </div>
      <Button type="button" variant="ghost" size="icon" onClick={() => onRemove(idx)}>
        <Trash2 className="size-4 text-red-500" />
      </Button>
    </div>
  );
}

interface StepFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  formData: StepFormData;
  onFormDataChange: (data: StepFormData) => void;
  onSubmit: () => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  availableSteps?: DialogueStep[];
  editingStepId?: number | null;
}

export function StepFormDialog({
  open,
  onOpenChange,
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
  isSubmitting,
  availableSteps = [],
  editingStepId,
}: StepFormDialogProps) {
  const t = useTranslations();
  const isCreate = mode === "create";

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleOptionDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = formData.options.findIndex((_, i) => i === active.id);
    const newIndex = formData.options.findIndex((_, i) => i === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    onFormDataChange({ ...formData, options: arrayMove(formData.options, oldIndex, newIndex) });
  };

  // Build step options for dropdowns, excluding the step being edited
  const otherSteps = availableSteps.filter((s) => s.id !== editingStepId);
  const stepIdOptions = [
    { value: "", label: t("dialogues.noneStep") },
    ...otherSteps.map((s) => ({
      value: String(s.id),
      label: `#${s.step_number} — ${s.question.length > 50 ? s.question.slice(0, 50) + "…" : s.question}`,
    })),
  ];
  const stepNumberOptions = [
    { value: "0", label: t("dialogues.noneStep") },
    ...otherSteps.map((s) => ({
      value: String(s.step_number),
      label: `#${s.step_number} — ${s.question.length > 50 ? s.question.slice(0, 50) + "…" : s.question}`,
    })),
  ];

  const addOption = () => {
    onFormDataChange({
      ...formData,
      options: [...formData.options, { label: "", next_step: 0 }],
    });
  };

  const updateOption = (idx: number, field: "label" | "next_step", value: string | number) => {
    const newOptions = formData.options.map((o, i) =>
      i === idx ? { ...o, [field]: value } : o,
    );
    onFormDataChange({ ...formData, options: newOptions });
  };

  const removeOption = (idx: number) => {
    onFormDataChange({
      ...formData,
      options: formData.options.filter((_, i) => i !== idx),
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isCreate ? t("dialogues.addStep") : t("dialogues.editStep")}
          </DialogTitle>
          <DialogDescription>
            {isCreate ? t("dialogues.addStepDesc") : t("dialogues.editStepDesc")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.stepNumber")} *</label>
              <Input
                type="number"
                min={1}
                value={formData.step_number}
                onChange={(e) =>
                  onFormDataChange({ ...formData, step_number: parseInt(e.target.value) || 1 })
                }
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.answerType")} *</label>
              <Select
                options={ANSWER_TYPE_OPTIONS}
                value={formData.answer_type}
                onChange={(v) =>
                  onFormDataChange({
                    ...formData,
                    answer_type: v as DialogueAnswerType,
                    options: [],
                    ...(v === "CHOICE" ? { next_step_id: null, parent_step_id: null } : {}),
                  })
                }
              />
            </div>
          </div>

          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.question")} *</label>
            <Textarea
              value={formData.question}
              onChange={(e) => onFormDataChange({ ...formData, question: e.target.value })}
              placeholder={t("dialogues.questionPlaceholder")}
              rows={3}
            />
          </div>

          {(formData.answer_type === "TEXT" || formData.answer_type === "LINK") && (
            <div className="grid gap-2">
              <label className="text-sm font-medium">
                {formData.answer_type === "LINK" ? t("dialogues.answerLink") : t("dialogues.answerContent")}
              </label>
              <Textarea
                value={formData.answer_content}
                onChange={(e) => onFormDataChange({ ...formData, answer_content: e.target.value })}
                placeholder={
                  formData.answer_type === "LINK"
                    ? "https://..."
                    : t("dialogues.answerContentPlaceholder")
                }
                rows={3}
              />
            </div>
          )}

          {formData.answer_type === "CHOICE" && (
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">{t("dialogues.choiceOptions")}</label>
                <Button type="button" variant="outline" size="sm" onClick={addOption}>
                  <Plus className="mr-1 size-3" />
                  {t("dialogues.addOption")}
                </Button>
              </div>
              {formData.options.length === 0 && (
                <p className="text-muted-foreground text-xs">{t("dialogues.noOptions")}</p>
              )}
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleOptionDragEnd}
              >
                <SortableContext
                  items={formData.options.map((_, i) => i)}
                  strategy={verticalListSortingStrategy}
                >
                  {formData.options.map((opt, idx) => (
                    <SortableOptionRow
                      key={idx}
                      idx={idx}
                      opt={opt}
                      stepNumberOptions={stepNumberOptions}
                      onUpdate={updateOption}
                      onRemove={removeOption}
                      optionLabelPlaceholder={t("dialogues.optionLabel")}
                    />
                  ))}
                </SortableContext>
              </DndContext>
              <p className="text-muted-foreground text-xs">{t("dialogues.optionsHint")}</p>
            </div>
          )}

          {formData.answer_type !== "CHOICE" && (
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">{t("dialogues.nextStepId")}</label>
                <p className="text-muted-foreground text-xs">{t("dialogues.nextStepIdHint")}</p>
                <Select
                  options={stepIdOptions}
                  value={formData.next_step_id !== null ? String(formData.next_step_id) : ""}
                  onChange={(v) =>
                    onFormDataChange({
                      ...formData,
                      next_step_id: v ? parseInt(v) : null,
                    })
                  }
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">{t("dialogues.parentStepId")}</label>
                <p className="text-muted-foreground text-xs">{t("dialogues.parentStepIdHint")}</p>
                <Select
                  options={stepIdOptions}
                  value={formData.parent_step_id !== null ? String(formData.parent_step_id) : ""}
                  onChange={(v) =>
                    onFormDataChange({
                      ...formData,
                      parent_step_id: v ? parseInt(v) : null,
                    })
                  }
                />
              </div>
            </div>
          )}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_final"
              checked={formData.is_final}
              onChange={(e) => onFormDataChange({ ...formData, is_final: e.target.checked })}
            />
            <label htmlFor="is_final" className="text-sm">
              {t("dialogues.isFinal")}
            </label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            {t("common.cancel")}
          </Button>
          <Button
            onClick={onSubmit}
            disabled={!formData.question || isSubmitting}
          >
            {isCreate ? t("common.create") : t("common.save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
