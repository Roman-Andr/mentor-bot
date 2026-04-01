import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, type TaskTemplate } from "@/lib/api";

export interface TemplateItem {
  id: number;
  name: string;
  description: string;
  department_id: number | null;
  department: string;
  position: string;
  durationDays: number;
  taskCount: number;
  status: string;
  isDefault: boolean;
}

export interface TemplateFormData {
  name: string;
  description: string;
  department_id: number;
  position: string;
  duration_days: number;
  status: string;
  is_default: boolean;
}

const defaultFormData: TemplateFormData = {
  name: "",
  description: "",
  department_id: 0,
  position: "",
  duration_days: 30,
  status: "DRAFT",
  is_default: false,
};

function mapTemplateToItem(
  data: {
    id: number;
    name: string;
    description: string | null;
    department_id: number | null;
    department: { id: number; name: string } | null;
    position: string | null;
    duration_days: number;
    status: string;
    is_default: boolean;
    task_categories: string[];
  },
  taskCount: number,
): TemplateItem {
  return {
    id: data.id,
    name: data.name,
    description: data.description || "",
    department_id: data.department_id,
    department: data.department?.name || "",
    position: data.position || "",
    durationDays: data.duration_days,
    taskCount,
    status: data.status,
    isDefault: data.is_default,
  };
}

const TEMPLATES_KEY = ["templates"] as const;

export function useTemplates() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null);
  const [formData, setFormData] = useState<TemplateFormData>({ ...defaultFormData });
  const [tasks, setTasks] = useState<TaskTemplate[]>([]);

  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(statusFilter !== "ALL" && { status: statusFilter }),
  };

  const { data: templatesData, isLoading: loading } = useQuery({
    queryKey: [...TEMPLATES_KEY, queryParams],
    queryFn: () => api.templates.list(queryParams),
    select: (result) => result.data?.map((t) => mapTemplateToItem(t, 0)) || [],
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.templates.create>[0]) => api.templates.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: TEMPLATES_KEY });
        setIsCreateDialogOpen(false);
        setFormData(defaultFormData);
        setTasks([]);
        toast("Шаблон создан", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка создания шаблона", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.templates.update>[1] }) =>
      api.templates.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: TEMPLATES_KEY });
        setIsEditDialogOpen(false);
        setSelectedTemplate(null);
        setFormData(defaultFormData);
        setTasks([]);
        toast("Шаблон обновлён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка обновления шаблона", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.templates.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: TEMPLATES_KEY });
        toast("Шаблон удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления шаблона", "error"),
  });

  const publishMutation = useMutation({
    mutationFn: (id: number) => api.templates.publish(id),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: TEMPLATES_KEY });
        toast("Шаблон опубликован", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка публикации шаблона", "error"),
  });

  const addTasksToTemplate = async (templateId: number) => {
    for (const task of tasks) {
      await api.templates.addTask(templateId, {
        template_id: templateId,
        title: task.title,
        description: task.description,
        instructions: task.instructions,
        category: task.category,
        order: task.order,
        due_days: task.due_days,
        estimated_minutes: task.estimated_minutes,
      });
    }
  };

  const handleCreate = async () => {
    try {
      const response = await createMutation.mutateAsync({
        name: formData.name,
        description: formData.description,
        department_id: formData.department_id || null,
        position: formData.position || null,
        level: null,
        duration_days: formData.duration_days,
        task_categories: [],
        status: (formData.status || "DRAFT") as "DRAFT" | "ACTIVE" | "ARCHIVED",
      });
      if (response.data) {
        await addTasksToTemplate(response.data.id);
      }
    } catch {
      // Error handled by mutation
    }
  };

  const handleUpdate = async () => {
    if (!selectedTemplate) return;
    try {
      const response = await updateMutation.mutateAsync({
        id: selectedTemplate.id,
        data: {
          name: formData.name,
          description: formData.description,
          status: (formData.status || "DRAFT") as "DRAFT" | "ACTIVE" | "ARCHIVED",
          is_default: formData.is_default,
        },
      });
      if (response.data) {
        const newTasks = tasks.filter((t) => !t.id || t.id === 0);
        for (const task of newTasks) {
          await api.templates.addTask(selectedTemplate.id, {
            template_id: selectedTemplate.id,
            title: task.title,
            description: task.description,
            instructions: task.instructions,
            category: task.category,
            order: task.order,
            due_days: task.due_days,
            estimated_minutes: task.estimated_minutes,
          });
        }
      }
    } catch {
      // Error handled by mutation
    }
  };

  const handleDelete = async (id: number) => {
    if (
      !(await confirm({
        title: "Удаление шаблона",
        description: "Вы уверены, что хотите удалить этот шаблон?",
        variant: "destructive",
        confirmText: "Удалить",
      }))
    )
      return;
    deleteMutation.mutate(id);
  };

  const handlePublish = (id: number) => {
    publishMutation.mutate(id);
  };

  const openEditDialog = (template: TemplateItem) => {
    setSelectedTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      department_id: template.department_id || 0,
      position: template.position,
      duration_days: template.durationDays,
      status: template.status,
      is_default: template.isDefault,
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(defaultFormData);
    setTasks([]);
  };

  const templates = templatesData || [];
  const totalCount = templates.length;
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return {
    templates,
    loading,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedTemplate,
    setSelectedTemplate,
    formData,
    setFormData,
    tasks,
    setTasks,
    handleCreate,
    handleUpdate,
    handleDelete,
    handlePublish,
    openEditDialog,
    resetForm,
    resetFilters: () => {
      setSearchQuery("");
      setStatusFilter("ALL");
      setCurrentPage(1);
    },
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
