import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
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

const DEPARTMENTS_KEY = ["departments"] as const;

export function useDepartments() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState<DepartmentRow | null>(null);
  const [formData, setFormData] = useState<DepartmentFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const debouncedSearch = useDebounce(searchQuery);

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(debouncedSearch && { search: debouncedSearch }),
  };

  const { data: departmentsData, isLoading: loading } = useQuery({
    queryKey: [...DEPARTMENTS_KEY, queryParams],
    queryFn: () => api.departments.list(queryParams),
    select: (result) =>
      result.data
        ? {
            departments: result.data.departments.map(mapDepartment),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.departments.create>[0]) =>
      api.departments.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: DEPARTMENTS_KEY });
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Отдел создан", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения отдела", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Parameters<typeof api.departments.update>[1];
    }) => api.departments.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: DEPARTMENTS_KEY });
        setIsEditDialogOpen(false);
        setSelectedDepartment(null);
        toast("Отдел обновлён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения отдела", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.departments.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: DEPARTMENTS_KEY });
        toast("Отдел удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления отдела", "error"),
  });

  const handleSubmit = () => {
    const payload = {
      name: formData.name,
      description: formData.description || null,
    };

    if (selectedDepartment) {
      updateMutation.mutate({ id: selectedDepartment.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
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

  const departments = departmentsData?.departments || [];
  const totalCount = departmentsData?.total || 0;
  const totalPages = departmentsData?.pages || 1;

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
    handleSubmit,
    handleDelete,
    openEdit,
    resetForm,
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
