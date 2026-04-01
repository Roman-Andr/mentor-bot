import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
import { useToast } from "@/components/ui/toast";
import { api, type User } from "@/lib/api";

export interface UserItem {
  id: number;
  name: string;
  email: string;
  employee_id: string;
  role: string;
  department_id: number | null;
  department: string;
  position: string;
  isActive: boolean;
  createdAt: string;
}

export interface UserFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  employee_id: string;
  department_id: number;
  position: string;
  level: string;
  role: string;
  is_active: boolean;
  password: string;
}

const PAGE_SIZE = 20;

const INITIAL_FORM: UserFormData = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  employee_id: "",
  department_id: 0,
  position: "",
  level: "",
  role: "NEWBIE",
  is_active: true,
  password: "",
};

function mapUser(u: User): UserItem {
  return {
    id: u.id,
    name: `${u.first_name} ${u.last_name || ""}`.trim(),
    email: u.email,
    employee_id: u.employee_id,
    role: u.role,
    department_id: u.department_id,
    department: u.department?.name || "",
    position: u.position || "",
    isActive: u.is_active,
    createdAt: u.created_at,
  };
}

const USERS_KEY = ["users"] as const;
const DEPARTMENTS_KEY = ["departments"] as const;

export function useUsers() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [formData, setFormData] = useState<UserFormData>(INITIAL_FORM);

  const debouncedSearch = useDebounce(searchQuery);

  const queryParams = {
    skip: (currentPage - 1) * PAGE_SIZE,
    limit: PAGE_SIZE,
    ...(roleFilter !== "ALL" && { role: roleFilter }),
    ...(departmentFilter !== "ALL" && { department_id: parseInt(departmentFilter) }),
    ...(debouncedSearch && { search: debouncedSearch }),
  };

  const { data: usersData, isLoading: loading } = useQuery({
    queryKey: [...USERS_KEY, queryParams],
    queryFn: () => api.users.list(queryParams),
    select: (result) =>
      result.data
        ? {
            users: result.data.users.map(mapUser),
            total: result.data.total,
          }
        : undefined,
  });

  const { data: departmentsData } = useQuery({
    queryKey: DEPARTMENTS_KEY,
    queryFn: () => api.departments.list({ limit: 1000 }),
    select: (result) => result.data?.departments || [],
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.users.create>[0]) => api.users.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: USERS_KEY });
        setIsCreateDialogOpen(false);
        setFormData(INITIAL_FORM);
        toast("Пользователь успешно создан", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => {
      toast("Ошибка создания пользователя", "error");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.users.update>[1] }) =>
      api.users.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: USERS_KEY });
        setIsEditDialogOpen(false);
        setSelectedUser(null);
        setFormData(INITIAL_FORM);
        toast("Пользователь обновлён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => {
      toast("Ошибка обновления пользователя", "error");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.users.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: USERS_KEY });
        toast("Пользователь удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => {
      toast("Ошибка удаления пользователя", "error");
    },
  });

  const handleCreateUser = () => {
    createMutation.mutate({
      first_name: formData.first_name,
      last_name: formData.last_name || null,
      email: formData.email,
      phone: formData.phone || null,
      employee_id: formData.employee_id,
      department_id: formData.department_id || undefined,
      position: formData.position || null,
      level: formData.level || null,
      role: formData.role,
      is_active: formData.is_active,
      password: formData.password,
    });
  };

  const handleUpdateUser = () => {
    if (!selectedUser) return;
    updateMutation.mutate({
      id: selectedUser.id,
      data: {
        first_name: formData.first_name,
        last_name: formData.last_name || null,
        email: formData.email,
        phone: formData.phone || null,
        employee_id: formData.employee_id,
        department_id: formData.department_id || undefined,
        position: formData.position || null,
        level: formData.level || null,
        role: formData.role,
        is_active: formData.is_active,
      },
    });
  };

  const handleDeleteUser = (id: number) => {
    deleteMutation.mutate(id);
  };

  const openEditDialog = (user: UserItem) => {
    const nameParts = user.name.split(" ");
    setSelectedUser(user);
    setFormData({
      first_name: nameParts[0] || "",
      last_name: nameParts.slice(1).join(" ") || "",
      email: user.email,
      phone: "",
      employee_id: user.employee_id || "",
      department_id: user.department_id || 0,
      position: user.position,
      level: "",
      role: user.role,
      is_active: user.isActive,
      password: "",
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(INITIAL_FORM);
    setSelectedUser(null);
  };

  const resetFilters = () => {
    setSearchQuery("");
    setRoleFilter("ALL");
    setDepartmentFilter("ALL");
    setCurrentPage(1);
  };

  const users = usersData?.users || [];
  const totalUsers = usersData?.total || 0;
  const totalPages = Math.ceil(totalUsers / PAGE_SIZE) || 1;
  const departments = departmentsData || [];

  return {
    users,
    loading,
    totalUsers,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedUser,
    setSelectedUser,
    formData,
    setFormData,
    searchQuery,
    setSearchQuery,
    currentPage,
    setCurrentPage,
    totalPages,
    roleFilter,
    setRoleFilter,
    departmentFilter,
    setDepartmentFilter,
    departments,
    loadDepartments: () => queryClient.invalidateQueries({ queryKey: DEPARTMENTS_KEY }),
    handleCreateUser,
    handleUpdateUser,
    handleDeleteUser,
    openEditDialog,
    resetForm,
    resetFilters,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
