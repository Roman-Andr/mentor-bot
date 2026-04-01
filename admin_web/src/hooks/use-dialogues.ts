import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/components/ui/toast";
import {
  api,
  type DialogueScenario,
  type DialogueCategory,
  type DialogueAnswerType,
} from "@/lib/api";

export interface DialogueRow {
  id: number;
  title: string;
  description: string;
  keywords: string[];
  category: DialogueCategory;
  isActive: boolean;
  displayOrder: number;
  stepsCount: number;
  createdAt: string;
}

export interface DialogueStepRow {
  id: number;
  scenario_id: number;
  step_number: number;
  question: string;
  answer_type: DialogueAnswerType;
  options: { label: string; next_step: number }[] | null;
  answer_content: string | null;
  is_final: boolean;
}

export interface DialogueFormData {
  title: string;
  description: string;
  keywords: string;
  category: DialogueCategory;
  is_active: boolean;
  display_order: number;
}

const EMPTY_FORM: DialogueFormData = {
  title: "",
  description: "",
  keywords: "",
  category: "VACATION",
  is_active: true,
  display_order: 0,
};

function mapDialogue(d: DialogueScenario): DialogueRow {
  return {
    id: d.id,
    title: d.title,
    description: d.description || "",
    keywords: d.keywords,
    category: d.category as DialogueCategory,
    isActive: d.is_active,
    displayOrder: d.display_order,
    stepsCount: d.steps?.length || 0,
    createdAt: d.created_at ? d.created_at.split("T")[0] : "",
  };
}

const DIALOGUES_KEY = ["dialogues"] as const;

export function useDialogues() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedDialogue, setSelectedDialogue] = useState<DialogueRow | null>(null);
  const [selectedSteps, setSelectedSteps] = useState<DialogueStepRow[]>([]);
  const [formData, setFormData] = useState<DialogueFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);

  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(categoryFilter !== "ALL" && { category: categoryFilter }),
    ...(searchQuery && { search: searchQuery }),
  };

  const { data: dialoguesData, isLoading: loading } = useQuery({
    queryKey: [...DIALOGUES_KEY, queryParams],
    queryFn: () => api.dialogues.list(queryParams),
    select: (result) =>
      result.data
        ? {
            dialogues: result.data.scenarios.map(mapDialogue),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.dialogues.create>[0]) => api.dialogues.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: DIALOGUES_KEY });
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Диалог создан", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка создания диалога", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.dialogues.update>[1] }) =>
      api.dialogues.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: DIALOGUES_KEY });
        setIsEditDialogOpen(false);
        setSelectedDialogue(null);
        toast("Диалог обновлён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка обновления диалога", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.dialogues.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: DIALOGUES_KEY });
        toast("Диалог удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления диалога", "error"),
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      api.dialogues.update(id, { is_active }),
    onSuccess: (result, { is_active }) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: DIALOGUES_KEY });
        toast(is_active ? "Диалог активирован" : "Диалог деактивирован", "success");
      }
    },
    onError: () => toast("Ошибка изменения статуса", "error"),
  });

  const detailsQuery = useQuery({
    queryKey: ["dialogue", selectedDialogue?.id],
    queryFn: () => api.dialogues.get(selectedDialogue!.id),
    enabled: !!selectedDialogue,
    select: (result) => {
      if (!result.data) return null;
      return (
        result.data.steps?.map((s) => ({
          id: s.id,
          scenario_id: s.scenario_id,
          step_number: s.step_number,
          question: s.question,
          answer_type: s.answer_type as DialogueAnswerType,
          options: s.options,
          answer_content: s.answer_content,
          is_final: s.is_final,
        })) || []
      );
    },
  });

  const handleSubmit = () => {
    const keywordsArray = formData.keywords
      .split(",")
      .map((k) => k.trim())
      .filter(Boolean);

    const payload = {
      title: formData.title,
      description: formData.description || undefined,
      keywords: keywordsArray,
      category: formData.category,
      is_active: formData.is_active,
      display_order: formData.display_order,
    };

    if (selectedDialogue) {
      updateMutation.mutate({ id: selectedDialogue.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const handleToggleActive = (id: number, isActive: boolean) => {
    toggleActiveMutation.mutate({ id, is_active: isActive });
  };

  const openEdit = (dialogue: DialogueRow) => {
    setSelectedDialogue(dialogue);
    setFormData({
      title: dialogue.title,
      description: dialogue.description,
      keywords: dialogue.keywords.join(", "),
      category: dialogue.category,
      is_active: dialogue.isActive,
      display_order: dialogue.displayOrder,
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setSelectedDialogue(null);
    setSelectedSteps([]);
  };

  const dialogues = dialoguesData?.dialogues || [];
  const totalCount = dialoguesData?.total || 0;
  const totalPages = dialoguesData?.pages || 1;

  return {
    dialogues,
    loading,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedDialogue,
    setSelectedDialogue,
    selectedSteps: detailsQuery.data || selectedSteps,
    formData,
    setFormData,
    searchQuery,
    setSearchQuery,
    categoryFilter,
    setCategoryFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    handleSubmit,
    handleDelete,
    handleToggleActive,
    openEdit,
    resetForm,
    isSubmitting:
      createMutation.isPending || updateMutation.isPending || toggleActiveMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
