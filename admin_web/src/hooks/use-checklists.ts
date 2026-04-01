import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

export interface ChecklistItem {
  id: number;
  userId: number;
  employeeId: string;
  templateId: number;
  status: string;
  progressPercentage: number;
  completedTasks: number;
  totalTasks: number;
  startDate: string;
  dueDate: string | null;
  completedAt: string | null;
  mentorId: number | null;
  hrId: number | null;
  notes: string | null;
  isOverdue: boolean;
  daysRemaining: number | null;
  createdAt: string;
}

export interface ChecklistFormData {
  user_id: number;
  employee_id: string;
  template_id: number;
  start_date: string;
  due_date: string;
  mentor_id: number | null;
  hr_id: number | null;
  notes: string;
}

const defaultFormData: ChecklistFormData = {
  user_id: 0,
  employee_id: "",
  template_id: 0,
  start_date: new Date().toISOString().split("T")[0],
  due_date: "",
  mentor_id: null,
  hr_id: null,
  notes: "",
};

function mapToItem(c: {
  id: number;
  user_id: number;
  employee_id: string;
  template_id: number;
  status: string;
  progress_percentage: number;
  completed_tasks: number;
  total_tasks: number;
  start_date: string;
  due_date: string | null;
  completed_at: string | null;
  mentor_id: number | null;
  hr_id: number | null;
  notes: string | null;
  is_overdue: boolean;
  days_remaining: number | null;
  created_at: string;
}): ChecklistItem {
  return {
    id: c.id,
    userId: c.user_id,
    employeeId: c.employee_id,
    templateId: c.template_id,
    status: c.status,
    progressPercentage: c.progress_percentage,
    completedTasks: c.completed_tasks,
    totalTasks: c.total_tasks,
    startDate: c.start_date,
    dueDate: c.due_date,
    completedAt: c.completed_at,
    mentorId: c.mentor_id,
    hrId: c.hr_id,
    notes: c.notes,
    isOverdue: c.is_overdue,
    daysRemaining: c.days_remaining,
    createdAt: c.created_at,
  };
}

const CHECKLISTS_KEY = ["checklists"] as const;

export function useChecklists() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedChecklist, setSelectedChecklist] = useState<ChecklistItem | null>(null);
  const [formData, setFormData] = useState<ChecklistFormData>({ ...defaultFormData });

  const debouncedSearch = useDebounce(searchQuery, 300);
  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(statusFilter !== "ALL" && { status: statusFilter }),
    ...(departmentFilter !== "ALL" && { department_id: parseInt(departmentFilter) }),
    ...(debouncedSearch && { search: debouncedSearch }),
  };

  const { data: checklistsData, isLoading: loading } = useQuery({
    queryKey: [...CHECKLISTS_KEY, queryParams],
    queryFn: () => api.checklists.list(queryParams),
    select: (result) =>
      result.data
        ? {
            checklists: result.data.checklists.map(mapToItem),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.checklists.create>[0]) => api.checklists.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: CHECKLISTS_KEY });
        setIsCreateDialogOpen(false);
        setFormData(defaultFormData);
        toast("Чек-лист назначен", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка создания чек-листа", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.checklists.update>[1] }) =>
      api.checklists.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: CHECKLISTS_KEY });
        setIsEditDialogOpen(false);
        setSelectedChecklist(null);
        setFormData(defaultFormData);
        toast("Чек-лист обновлён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка обновления чек-листа", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.checklists.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: CHECKLISTS_KEY });
        toast("Чек-лист удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления чек-листа", "error"),
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => api.checklists.complete(id),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: CHECKLISTS_KEY });
        toast("Чек-лист завершён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка завершения чек-листа", "error"),
  });

  const handleCreate = () => {
    createMutation.mutate({
      user_id: formData.user_id,
      employee_id: formData.employee_id,
      template_id: formData.template_id,
      start_date: new Date(formData.start_date).toISOString(),
      due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
      mentor_id: formData.mentor_id,
      hr_id: formData.hr_id,
      notes: formData.notes || null,
    });
  };

  const handleUpdate = () => {
    if (!selectedChecklist) return;
    updateMutation.mutate({
      id: selectedChecklist.id,
      data: {
        mentor_id: formData.mentor_id,
        hr_id: formData.hr_id,
        notes: formData.notes || null,
      },
    });
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const handleComplete = (id: number) => {
    completeMutation.mutate(id);
  };

  const openEditDialog = (checklist: ChecklistItem) => {
    setSelectedChecklist(checklist);
    setFormData({
      user_id: checklist.userId,
      employee_id: checklist.employeeId,
      template_id: checklist.templateId,
      start_date: checklist.startDate.split("T")[0],
      due_date: checklist.dueDate ? checklist.dueDate.split("T")[0] : "",
      mentor_id: checklist.mentorId,
      hr_id: checklist.hrId,
      notes: checklist.notes || "",
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(defaultFormData);
    setSelectedChecklist(null);
  };

  const resetFilters = () => {
    setSearchQuery("");
    setStatusFilter("ALL");
    setDepartmentFilter("ALL");
    setCurrentPage(1);
  };

  const checklists = checklistsData?.checklists || [];
  const totalCount = checklistsData?.total || 0;
  const totalPages = checklistsData?.pages || 1;

  return {
    checklists,
    loading,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    departmentFilter,
    setDepartmentFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedChecklist,
    setSelectedChecklist,
    formData,
    setFormData,
    handleCreate,
    handleUpdate,
    handleDelete,
    handleComplete,
    openEditDialog,
    resetForm,
    resetFilters,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
