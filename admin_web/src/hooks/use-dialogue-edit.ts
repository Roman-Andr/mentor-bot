"use client";

/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useMemo, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "@/hooks/use-translations";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { DialogueAnswerType, DialogueCategory, DialogueStep } from "@/types";

export interface StepFormData {
  step_number: number;
  question: string;
  answer_type: DialogueAnswerType;
  answer_content: string;
  options: { label: string; next_step: number }[];
  next_step_id: number | null;
  parent_step_id: number | null;
  is_final: boolean;
}

const EMPTY_STEP: StepFormData = {
  step_number: 1,
  question: "",
  answer_type: "TEXT",
  answer_content: "",
  options: [],
  next_step_id: null,
  parent_step_id: null,
  is_final: false,
};

export interface DialogueMetaFormData {
  title: string;
  description: string;
  keywords: string;
  category: DialogueCategory;
  is_active: boolean;
  display_order: number;
}

export function useDialogueEdit(id: number) {
  const t = useTranslations("dialogues");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [metaForm, setMetaForm] = useState<DialogueMetaFormData | null>(null);
  const [isStepDialogOpen, setIsStepDialogOpen] = useState(false);
  const [editingStepId, setEditingStepId] = useState<number | null>(null);
  const [stepForm, setStepForm] = useState<StepFormData>(EMPTY_STEP);
  // Local state for optimistic reordering UI
  const [localOrderedSteps, setLocalOrderedSteps] = useState<DialogueStep[]>([]);

  const QUERY_KEY = ["dialogue", id];

  const { data: dialogue, isLoading } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: () => api.dialogues.get(id),
    select: (r) => r.success ? r.data ?? null : null,
    enabled: !!id,
  });

  // Initialize metaForm once dialogue loads using useMemo
  const initialMetaForm = useMemo(() => {
    if (!dialogue) return null;
    return {
      title: dialogue.title,
      description: dialogue.description ?? "",
      keywords: dialogue.keywords.join(", "),
      category: dialogue.category as DialogueCategory,
      is_active: dialogue.is_active,
      display_order: dialogue.display_order,
    };
  }, [dialogue]);

  // Set metaForm when initialMetaForm changes and metaForm is null
  useEffect(() => {
    if (initialMetaForm && metaForm === null) {
      setMetaForm(initialMetaForm);
    }
  }, [initialMetaForm, metaForm]);

  // Compute ordered steps from server data
  const serverOrderedSteps = useMemo(() => {
    if (!dialogue?.steps) return [];
    return [...dialogue.steps].sort((a, b) => a.step_number - b.step_number);
  }, [dialogue]);

  // Initialize localOrderedSteps with server data on first load
  useEffect(() => {
    if (localOrderedSteps.length === 0 && serverOrderedSteps.length > 0) {
      setLocalOrderedSteps(serverOrderedSteps);
    }
  }, [serverOrderedSteps, localOrderedSteps.length]);

  // Use localOrderedSteps for UI, fall back to serverOrderedSteps
  const orderedSteps = localOrderedSteps.length > 0 ? localOrderedSteps : serverOrderedSteps;

  const updateMeta = useMutation({
    mutationFn: (data: Parameters<typeof api.dialogues.update>[1]) =>
      api.dialogues.update(id, data),
    onSuccess: (r) => {
      if (r.success) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: ["dialogues"] });
        toast(t("saved"), "success");
      } else {
        toast(r.error.message, "error");
      }
    },
    onError: () => toast(t("saveError"), "error"),
  });

  const addStep = useMutation({
    mutationFn: (data: Parameters<typeof api.dialogues.addStep>[1]) =>
      api.dialogues.addStep(id, data),
    onSuccess: (r) => {
      if (r.success) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEY });
        setIsStepDialogOpen(false);
        toast(t("stepAdded"), "success");
      } else {
        toast(r.error.message, "error");
      }
    },
    onError: () => toast(t("stepAddError"), "error"),
  });

  const updateStep = useMutation({
    mutationFn: ({ stepId, data }: { stepId: number; data: Parameters<typeof api.dialogues.updateStep>[1] }) =>
      api.dialogues.updateStep(stepId, data),
    onSuccess: (r) => {
      if (r.success) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEY });
        setIsStepDialogOpen(false);
        toast(t("stepUpdated"), "success");
      } else {
        toast(r.error.message, "error");
      }
    },
    onError: () => toast(t("stepUpdateError"), "error"),
  });

  const deleteStep = useMutation({
    mutationFn: (stepId: number) => api.dialogues.deleteStep(stepId),
    onSuccess: (r) => {
      if (r.success) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEY });
        toast(t("stepDeleted"), "success");
      } else {
        toast(r.error.message, "error");
      }
    },
    onError: () => toast(t("stepDeleteError"), "error"),
  });

  const reorderStepsMutation = useMutation({
    mutationFn: (stepIds: number[]) => api.dialogues.reorderSteps(id, stepIds),
    onSuccess: (r) => {
      if (r.success) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      } else {
        toast(r.error.message, "error");
        // Revert optimistic update on error
        if (dialogue?.steps) {
          setLocalOrderedSteps([...dialogue.steps].sort((a, b) => a.step_number - b.step_number));
        }
      }
    },
    onError: () => {
      toast(t("stepReorderError"), "error");
      if (dialogue?.steps) {
        setLocalOrderedSteps([...dialogue.steps].sort((a, b) => a.step_number - b.step_number));
      }
    },
  });

  const handleSaveMeta = () => {
    if (!metaForm) return;
    const keywordsArray = metaForm.keywords
      .split(",")
      .map((k) => k.trim())
      .filter(Boolean);
    updateMeta.mutate({
      title: metaForm.title,
      description: metaForm.description || undefined,
      keywords: keywordsArray,
      category: metaForm.category,
      is_active: metaForm.is_active,
      display_order: metaForm.display_order,
    });
  };

  const openAddStep = () => {
    const nextNum = (dialogue?.steps?.length ?? 0) + 1;
    setEditingStepId(null);
    setStepForm({ ...EMPTY_STEP, step_number: nextNum });
    setIsStepDialogOpen(true);
  };

  const openEditStep = (stepId: number) => {
    const step = dialogue?.steps?.find((s) => s.id === stepId);
    if (!step) return;
    setEditingStepId(stepId);
    setStepForm({
      step_number: step.step_number,
      question: step.question,
      answer_type: step.answer_type as DialogueAnswerType,
      answer_content: step.answer_content ?? "",
      options: step.options ?? [],
      next_step_id: step.next_step_id ?? null,
      parent_step_id: step.parent_step_id ?? null,
      is_final: step.is_final,
    });
    setIsStepDialogOpen(true);
  };

  const handleSaveStep = () => {
    const payload = {
      step_number: stepForm.step_number,
      question: stepForm.question,
      answer_type: stepForm.answer_type,
      answer_content: stepForm.answer_content || undefined,
      options: stepForm.answer_type === "CHOICE" ? stepForm.options : undefined,
      next_step_id: stepForm.next_step_id,
      parent_step_id: stepForm.parent_step_id,
      is_final: stepForm.is_final,
    };
    if (editingStepId !== null) {
      updateStep.mutate({ stepId: editingStepId, data: payload });
    } else {
      addStep.mutate(payload);
    }
  };

  const handleDeleteStep = (stepId: number) => {
    deleteStep.mutate(stepId);
  };

  const handleReorderSteps = (newSteps: DialogueStep[]) => {
    setLocalOrderedSteps(newSteps);
    reorderStepsMutation.mutate(newSteps.map((s) => s.id));
  };

  const saveCurrentOrder = () => {
    reorderStepsMutation.mutate(orderedSteps.map((s) => s.id));
  };

  return {
    dialogue,
    isLoading,
    metaForm,
    setMetaForm,
    handleSaveMeta,
    isSavingMeta: updateMeta.isPending,
    isStepDialogOpen,
    setIsStepDialogOpen,
    editingStepId,
    stepForm,
    setStepForm,
    openAddStep,
    openEditStep,
    handleSaveStep,
    handleDeleteStep,
    isSavingStep: addStep.isPending || updateStep.isPending,
    isDeletingStep: deleteStep.isPending,
    orderedSteps,
    setOrderedSteps: setLocalOrderedSteps,
    handleReorderSteps,
    saveCurrentOrder,
    isReordering: reorderStepsMutation.isPending,
  };
}
