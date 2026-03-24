import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";

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

/** Manages all checklist CRUD state and operations. */
export function useChecklists() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [checklists, setChecklists] = useState<ChecklistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedChecklist, setSelectedChecklist] = useState<ChecklistItem | null>(null);
  const [formData, setFormData] = useState<ChecklistFormData>({ ...defaultFormData });

  const debouncedSearch = useDebounce(searchQuery, 300);
  const pageSize = 20;

  const resetForm = useCallback(() => {
    setFormData({ ...defaultFormData });
  }, []);

  const loadChecklists = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.checklists.list({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        status: statusFilter !== "ALL" ? statusFilter : undefined,
        department_id: departmentFilter !== "ALL" ? parseInt(departmentFilter) : undefined,
      });
      if (response.data) {
        setChecklists(response.data.checklists.map(mapToItem));
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      console.error("Failed to load checklists:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter, departmentFilter]);

  useEffect(() => {
    loadChecklists();
  }, [loadChecklists]);

  const filteredChecklists = searchQuery
    ? checklists.filter(
        (c) =>
          c.employeeId.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
          c.notes?.toLowerCase().includes(debouncedSearch.toLowerCase()),
      )
    : checklists;

  const handleCreate = async () => {
    try {
      const response = await api.checklists.create({
        user_id: formData.user_id,
        employee_id: formData.employee_id,
        template_id: formData.template_id,
        start_date: new Date(formData.start_date).toISOString(),
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
        mentor_id: formData.mentor_id,
        hr_id: formData.hr_id,
        notes: formData.notes || null,
      });
      if (response.data) {
        setChecklists([mapToItem(response.data), ...checklists]);
        setIsCreateDialogOpen(false);
        resetForm();
        setTotalCount((c) => c + 1);
        toast("Чек-лист назначен", "success");
      } else {
        toast(response.error || "Ошибка создания", "error");
      }
    } catch (err) {
      console.error("Failed to create checklist:", err);
      toast("Ошибка создания чек-листа", "error");
    }
  };

  const handleUpdate = async () => {
    if (!selectedChecklist) return;
    try {
      const response = await api.checklists.update(selectedChecklist.id, {
        mentor_id: formData.mentor_id,
        hr_id: formData.hr_id,
        notes: formData.notes || null,
      });
      if (response.data) {
        setChecklists(
          checklists.map((c) => (c.id === selectedChecklist.id ? mapToItem(response.data!) : c)),
        );
        setIsEditDialogOpen(false);
        setSelectedChecklist(null);
        resetForm();
        toast("Чек-лист обновлён", "success");
      } else {
        toast(response.error || "Ошибка обновления", "error");
      }
    } catch (err) {
      console.error("Failed to update checklist:", err);
      toast("Ошибка обновления чек-листа", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление чек-листа", description: "Вы уверены, что хотите удалить этот чек-лист?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.checklists.delete(id);
      setChecklists(checklists.filter((c) => c.id !== id));
      setTotalCount((c) => c - 1);
      toast("Чек-лист удалён", "success");
    } catch (err) {
      console.error("Failed to delete checklist:", err);
      toast("Ошибка удаления чек-листа", "error");
    }
  };

  const handleComplete = async (id: number) => {
    try {
      const response = await api.checklists.complete(id);
      if (response.data) {
        setChecklists(checklists.map((c) => (c.id === id ? mapToItem(response.data!) : c)));
        toast("Чек-лист завершён", "success");
      } else {
        toast(response.error || "Ошибка завершения", "error");
      }
    } catch (err) {
      console.error("Failed to complete checklist:", err);
      toast("Ошибка завершения чек-листа", "error");
    }
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

  return {
    checklists: filteredChecklists,
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
  };
}
