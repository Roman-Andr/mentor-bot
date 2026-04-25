"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "@/hooks/use-translations";
import { useDialogueEdit } from "@/hooks/use-dialogue-edit";
import { useConfirm } from "@/hooks/use-confirm";
import { StepFormDialog } from "@/components/features/dialogues/step-form-dialog";
import {
  DialogueEditHeader,
  DialogueMetadataForm,
  DialogueStepsTable,
} from "@/components/features/dialogues";
import type { DialogueStep, DialogueCategory } from "@/types";
import { arrayMove } from "@dnd-kit/sortable";
import type { DragEndEvent, DragOverEvent } from "@dnd-kit/core";

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
      <DialogueEditHeader title={dialogue.title} onBack={() => router.push("/dialogues")} />
      <DialogueMetadataForm
        title={metaForm.title}
        category={metaForm.category}
        description={metaForm.description}
        keywords={metaForm.keywords}
        displayOrder={metaForm.display_order}
        isActive={metaForm.is_active}
        onTitleChange={(value: string) => setMetaForm({ ...metaForm, title: value })}
        onCategoryChange={(value: string) => setMetaForm({ ...metaForm, category: value as DialogueCategory })}
        onDescriptionChange={(value: string) => setMetaForm({ ...metaForm, description: value })}
        onKeywordsChange={(value: string) => setMetaForm({ ...metaForm, keywords: value })}
        onDisplayOrderChange={(value: number) => setMetaForm({ ...metaForm, display_order: value })}
        onIsActiveChange={(value: boolean) => setMetaForm({ ...metaForm, is_active: value })}
        onSave={handleSaveMeta}
        isSaving={isSavingMeta}
      />
      <DialogueStepsTable
        steps={orderedSteps}
        onEdit={openEditStep}
        onDelete={handleDeleteStepConfirm}
        onAddStep={openAddStep}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
        t={t}
      />
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
