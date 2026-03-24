import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
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

/** Manages all template CRUD state and operations. */
export function useTemplates() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null);
  const [formData, setFormData] = useState<TemplateFormData>({ ...defaultFormData });
  const [tasks, setTasks] = useState<TaskTemplate[]>([]);

  const debouncedSearch = useDebounce(searchQuery);
  const pageSize = 20;

  const resetForm = useCallback(() => {
    setFormData({ ...defaultFormData });
    setTasks([]);
  }, []);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (statusFilter !== "ALL") params.status = statusFilter;
      params.skip = (currentPage - 1) * pageSize;
      params.limit = pageSize;

      const response = await api.templates.list(params);
      if (response.data) {
        const items: TemplateItem[] = [];
        for (const t of response.data) {
          let taskCount = 0;
          try {
            const detail = await api.templates.get(t.id);
            if (detail.data?.tasks) taskCount = detail.data.tasks.length;
          } catch {
            /* ignore */
          }
          items.push(mapTemplateToItem(t, taskCount));
        }
        setTemplates(items);
        setTotalCount(response.data.length);
        setTotalPages(Math.max(1, Math.ceil(response.data.length / pageSize)));
      }
    } catch (err) {
      console.error("Failed to load templates:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter]);

  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  const loadTemplateTasks = async (templateId: number) => {
    try {
      const response = await api.templates.get(templateId);
      if (response.data?.tasks) setTasks(response.data.tasks);
    } catch (err) {
      console.error("Failed to load template tasks:", err);
    }
  };

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
      const response = await api.templates.create({
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
        setTemplates([...templates, mapTemplateToItem(response.data, tasks.length)]);
        setTotalCount((c) => c + 1);
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Шаблон создан", "success");
      } else {
        toast(response.error || "Ошибка создания шаблона", "error");
      }
    } catch (err) {
      console.error("Failed to create template:", err);
      toast("Ошибка создания шаблона", "error");
    }
  };

  const handleUpdate = async () => {
    if (!selectedTemplate) return;
    try {
      const response = await api.templates.update(selectedTemplate.id, {
        name: formData.name,
        description: formData.description,
        status: (formData.status || "DRAFT") as "DRAFT" | "ACTIVE" | "ARCHIVED",
        is_default: formData.is_default,
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
        const updatedCount = selectedTemplate.taskCount + newTasks.length;
        setTemplates(
          templates.map((t) =>
            t.id === selectedTemplate.id ? mapTemplateToItem(response.data!, updatedCount) : t,
          ),
        );
        setIsEditDialogOpen(false);
        setSelectedTemplate(null);
        resetForm();
        toast("Шаблон обновлён", "success");
      } else {
        toast(response.error || "Ошибка обновления", "error");
      }
    } catch (err) {
      console.error("Failed to update template:", err);
      toast("Ошибка обновления шаблона", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление шаблона", description: "Вы уверены, что хотите удалить этот шаблон?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.templates.delete(id);
      setTemplates(templates.filter((t) => t.id !== id));
      setTotalCount((c) => c - 1);
      toast("Шаблон удалён", "success");
    } catch (err) {
      console.error("Failed to delete template:", err);
      toast("Ошибка удаления шаблона", "error");
    }
  };

  const handlePublish = async (id: number) => {
    try {
      const response = await api.templates.publish(id);
      if (response.data) {
        setTemplates(templates.map((t) => (t.id === id ? { ...t, status: "ACTIVE" } : t)));
        toast("Шаблон опубликован", "success");
      } else {
        toast(response.error || "Ошибка публикации", "error");
      }
    } catch (err) {
      console.error("Failed to publish template:", err);
      toast("Ошибка публикации шаблона", "error");
    }
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
    loadTemplateTasks(template.id);
    setIsEditDialogOpen(true);
  };

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
  };
}
