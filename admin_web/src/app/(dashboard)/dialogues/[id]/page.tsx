"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "@/hooks/use-translations";
import { useDialogueEdit } from "@/hooks/use-dialogue-edit";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useConfirm } from "@/hooks/use-confirm";
import { StepFormDialog } from "@/components/features/dialogues/step-form-dialog";
import { ArrowLeft, Plus, Edit, Trash2, GripVertical } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DialogueCategory, DialogueStep } from "@/types";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

const CATEGORY_OPTIONS: { value: DialogueCategory; label: string }[] = [
  { value: "VACATION", label: "Vacation & Time Off" },
  { value: "ACCESS", label: "Passes & Access" },
  { value: "BENEFITS", label: "Benefits" },
  { value: "CONTACTS", label: "Contacts" },
  { value: "WORKTIME", label: "Work Time" },
];

const ANSWER_TYPE_LABEL: Record<string, string> = {
  TEXT: "Text",
  CHOICE: "Choice",
  LINK: "Link",
};

interface SortableStepRowProps {
  step: DialogueStep;
  position: number;
  onEdit: (id: number) => void;
  onDelete: (id: number, question: string) => void;
  t: (key: string) => string;
}

function SortableStepRow({ step, position, onEdit, onDelete, t }: SortableStepRowProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: step.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <TableRow ref={setNodeRef} style={style} className={cn(isDragging && "bg-muted")}>
      <TableCell className="w-8 px-2">
        <button
          {...attributes}
          {...listeners}
          className="text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing"
          tabIndex={-1}
        >
          <GripVertical className="size-4" />
        </button>
      </TableCell>
      <TableCell className="w-16 text-center font-mono">{position}</TableCell>
      <TableCell>
        <p className="line-clamp-2">{step.question}</p>
      </TableCell>
      <TableCell className="w-24">
        <span className="bg-muted rounded px-2 py-0.5 text-xs font-medium">
          {ANSWER_TYPE_LABEL[step.answer_type] ?? step.answer_type}
        </span>
      </TableCell>
      <TableCell className="w-32">
        {step.answer_type === "CHOICE" ? (
          <span className="text-muted-foreground text-xs">
            {step.options?.length ?? 0} {t("dialogues.options")}
          </span>
        ) : (
          <p className="text-muted-foreground line-clamp-1 text-xs">
            {step.answer_content || "—"}
          </p>
        )}
      </TableCell>
      <TableCell className="w-16">
        <span
          className={cn(
            "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
            step.is_final ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-600",
          )}
        >
          {step.is_final ? t("common.yes") : t("common.no")}
        </span>
      </TableCell>
      <TableCell className="w-20">
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" onClick={() => onEdit(step.id)}>
            <Edit className="size-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => onDelete(step.id, step.question)}>
            <Trash2 className="size-4 text-red-500" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

export default function DialogueEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const dialogueId = parseInt(id);
  const router = useRouter();
  const t = useTranslations();
  const confirm = useConfirm();

  const {
    dialogue,
    isLoading,
    metaForm,
    setMetaForm,
    handleSaveMeta,
    isSavingMeta,
    isStepDialogOpen,
    setIsStepDialogOpen,
    editingStepId,
    stepForm,
    setStepForm,
    openAddStep,
    openEditStep,
    handleSaveStep,
    handleDeleteStep,
    isSavingStep,
    orderedSteps,
    setOrderedSteps,
    saveCurrentOrder,
  } = useDialogueEdit(dialogueId);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const reorder = (steps: typeof orderedSteps, activeId: number, overId: number) => {
    const oldIndex = steps.findIndex((s) => s.id === activeId);
    const newIndex = steps.findIndex((s) => s.id === overId);
    if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) return steps;
    return arrayMove(steps, oldIndex, newIndex);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    setOrderedSteps((prev: DialogueStep[]) => reorder(prev, active.id as number, over.id as number));
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { over } = event;
    if (!over) return;
    saveCurrentOrder();
  };

  const handleDeleteStepConfirm = async (stepId: number, question: string) => {
    if (
      !(await confirm({
        title: t("dialogues.deleteStep"),
        description: t("common.confirmDelete").replace("item", `"${question}"`),
        variant: "destructive",
        confirmText: t("common.delete"),
      }))
    )
      return;
    handleDeleteStep(stepId);
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </div>
    );
  }

  if (!dialogue || !metaForm) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground">{t("common.notFound")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dialogues")}>
          <ArrowLeft className="size-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">{t("dialogues.editDialogueTitle")}</h1>
          <p className="text-muted-foreground text-sm">{dialogue.title}</p>
        </div>
      </div>

      {/* Metadata card */}
      <Card>
        <CardHeader>
          <CardTitle>{t("dialogues.generalInfo")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.title_field")} *</label>
              <Input
                value={metaForm.title}
                onChange={(e) => setMetaForm({ ...metaForm, title: e.target.value })}
                placeholder={t("dialogues.title_field")}
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.category")} *</label>
              <Select
                options={CATEGORY_OPTIONS}
                value={metaForm.category}
                onChange={(v) => setMetaForm({ ...metaForm, category: v as DialogueCategory })}
              />
            </div>
          </div>

          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("dialogues.description")}</label>
            <Textarea
              value={metaForm.description}
              onChange={(e) => setMetaForm({ ...metaForm, description: e.target.value })}
              placeholder={t("dialogues.description")}
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.keywords")}</label>
              <Input
                value={metaForm.keywords}
                onChange={(e) => setMetaForm({ ...metaForm, keywords: e.target.value })}
                placeholder="key1, key2, key3"
              />
              <p className="text-muted-foreground text-xs">{t("dialogues.keywordsHint")}</p>
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("dialogues.displayOrder")}</label>
              <Input
                type="number"
                value={metaForm.display_order}
                onChange={(e) =>
                  setMetaForm({ ...metaForm, display_order: parseInt(e.target.value) || 0 })
                }
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={metaForm.is_active}
              onChange={(e) => setMetaForm({ ...metaForm, is_active: e.target.checked })}
            />
            <label htmlFor="is_active" className="text-sm">
              {t("dialogues.isActive")}
            </label>
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleSaveMeta}
              disabled={!metaForm.title || !metaForm.category || isSavingMeta}
            >
              {t("common.save")}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Steps card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {t("dialogues.steps")}{" "}
              <span className="text-muted-foreground text-sm font-normal">
                ({orderedSteps.length})
              </span>
            </CardTitle>
            <Button size="sm" onClick={openAddStep} className="gap-1">
              <Plus className="size-4" />
              {t("dialogues.addStep")}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {orderedSteps.length === 0 ? (
            <div className="flex h-32 items-center justify-center">
              <p className="text-muted-foreground text-sm">{t("dialogues.noSteps")}</p>
            </div>
          ) : (
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragOver={handleDragOver}
              onDragEnd={handleDragEnd}
            >
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-8" />
                    <TableHead className="w-16">{t("dialogues.stepNumber")}</TableHead>
                    <TableHead>{t("dialogues.question")}</TableHead>
                    <TableHead className="w-24">{t("dialogues.answerType")}</TableHead>
                    <TableHead className="w-32">{t("dialogues.answerContent")}</TableHead>
                    <TableHead className="w-16">{t("dialogues.isFinal")}</TableHead>
                    <TableHead className="w-20">{t("common.actions")}</TableHead>
                  </TableRow>
                </TableHeader>
                <SortableContext
                  items={orderedSteps.map((s) => s.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <TableBody>
                    {orderedSteps.map((step, index) => (
                      <SortableStepRow
                        key={step.id}
                        step={step}
                        position={index + 1}
                        onEdit={openEditStep}
                        onDelete={handleDeleteStepConfirm}
                        t={t}
                      />
                    ))}
                  </TableBody>
                </SortableContext>
              </Table>
            </DndContext>
          )}
        </CardContent>
      </Card>

      <StepFormDialog
        open={isStepDialogOpen}
        onOpenChange={setIsStepDialogOpen}
        mode={editingStepId === null ? "create" : "edit"}
        formData={stepForm}
        onFormDataChange={setStepForm}
        onSubmit={handleSaveStep}
        onCancel={() => setIsStepDialogOpen(false)}
        isSubmitting={isSavingStep}
        availableSteps={orderedSteps}
        editingStepId={editingStepId}
      />
    </div>
  );
}
