import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, type Department } from "@/lib/api";

export interface DepartmentRow {
  id: number;
  name: string;
  description: string;
  createdAt: string;
}

export interface DepartmentFormData {
  name: string;
  description: string;
}

const EMPTY_FORM: DepartmentFormData = {
  name: "",
  description: "",
};

function mapDepartment(d: Department): DepartmentRow {
  return {
    id: d.id,
    name: d.name,
    description: d.description || "",
    createdAt: d.created_at ? d.created_at.split("T")[0] : "",
  };
}

export function useDepartments() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [departments, setDepartments] = useState<DepartmentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState<DepartmentRow | null>(null);
  const [formData, setFormData] = useState<DepartmentFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  const debouncedSearch = useDebounce(searchQuery);

  const loadDepartments = useCallback(async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * pageSize;
      const response = await api.departments.list({ skip, limit: pageSize, search: debouncedSearch || undefined });
      if (response.data) {
        setDepartments(response.data.departments.map(mapDepartment));
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages || 1);
      }
    } catch (err) {
      console.error("Failed to load departments:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch]);

  useEffect(() => {
    loadDepartments();
  }, [loadDepartments]);

  const handleSubmit = async () => {
    const payload = {
      name: formData.name,
      description: formData.description || null,
    };

    try {
      if (selectedDepartment) {
        const response = await api.departments.update(selectedDepartment.id, payload);
        if (response.data) {
          setDepartments(
            departments.map((d) =>
              d.id === selectedDepartment.id ? mapDepartment(response.data!) : d,
            ),
          );
          setIsEditDialogOpen(false);
          setSelectedDepartment(null);
          toast("Отдел обновлён", "success");
        } else {
          toast(response.error || "Ошибка обновления", "error");
        }
      } else {
        const response = await api.departments.create(payload);
        if (response.data) {
          setTotalCount((c) => c + 1);
          setDepartments([mapDepartment(response.data), ...departments]);
          setIsCreateDialogOpen(false);
          resetForm();
          toast("Отдел создан", "success");
        } else {
          toast(response.error || "Ошибка создания", "error");
        }
      }
    } catch (err) {
      console.error("Failed to save department:", err);
      toast("Ошибка сохранения отдела", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление отдела", description: "Вы уверены, что хотите удалить этот отдел?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.departments.delete(id);
      setDepartments(departments.filter((d) => d.id !== id));
      setTotalCount((prev) => prev - 1);
      toast("Отдел удалён", "success");
    } catch (err) {
      console.error("Failed to delete department:", err);
      toast("Ошибка удаления отдела", "error");
    }
  };

  const openEdit = (department: DepartmentRow) => {
    setSelectedDepartment(department);
    setFormData({
      name: department.name,
      description: department.description,
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setSelectedDepartment(null);
  };

  const updateFormField = (field: keyof DepartmentFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return {
    departments,
    loading,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedDepartment,
    setSelectedDepartment,
    formData,
    setFormData,
    updateFormField,
    searchQuery,
    setSearchQuery,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    pageSize,
    loadDepartments,
    handleSubmit,
    handleDelete,
    openEdit,
    resetForm,
  };
}
