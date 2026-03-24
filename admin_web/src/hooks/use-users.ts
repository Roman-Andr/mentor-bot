import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, type User, type Department } from "@/lib/api";

export interface UserItem {
  id: number;
  name: string;
  email: string;
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
    role: u.role,
    department_id: u.department_id,
    department: u.department?.name || "",
    position: u.position || "",
    isActive: u.is_active,
    createdAt: u.created_at,
  };
}

export function useUsers() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [formData, setFormData] = useState<UserFormData>(INITIAL_FORM);
  const [departments, setDepartments] = useState<Department[]>([]);

  const debouncedSearch = useDebounce(searchQuery);

  const loadDepartments = useCallback(async () => {
    try {
      const response = await api.departments.list({ limit: 1000 });
      if (response.data) {
        setDepartments(response.data.departments);
      }
    } catch (err) {
      console.error("Failed to load departments:", err);
    }
  }, []);

  useEffect(() => {
    loadDepartments();
  }, [loadDepartments]);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {};
      if (roleFilter !== "ALL") params.role = roleFilter;
      if (departmentFilter !== "ALL") params.department_id = parseInt(departmentFilter);
      if (debouncedSearch) params.search = debouncedSearch;
      params.skip = (currentPage - 1) * PAGE_SIZE;
      params.limit = PAGE_SIZE;

      const response = await api.users.list(params);
      if (response.data) {
        setUsers(response.data.users.map(mapUser));
        setTotalUsers(response.data.total);
      }
    } catch (err) {
      console.error("Failed to load users:", err);
    } finally {
      setLoading(false);
    }
  }, [roleFilter, departmentFilter, currentPage, debouncedSearch]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearch]);

  const handleCreateUser = async () => {
    try {
      const response = await api.users.create({
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

      if (response.data) {
        setTotalUsers((t) => t + 1);
        setIsCreateDialogOpen(false);
        setFormData(INITIAL_FORM);
        loadUsers();
        toast("Пользователь успешно создан", "success");
      } else {
        toast(response.error || "Ошибка создания пользователя", "error");
      }
    } catch (err) {
      console.error("Failed to create user:", err);
      toast("Ошибка создания пользователя", "error");
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    try {
      const response = await api.users.update(selectedUser.id, {
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
      });

      if (response.data) {
        setUsers((prev) =>
          prev.map((u) => (u.id === selectedUser.id ? mapUser(response.data!) : u)),
        );
        setIsEditDialogOpen(false);
        setSelectedUser(null);
        setFormData(INITIAL_FORM);
        toast("Пользователь обновлён", "success");
      } else {
        toast(response.error || "Ошибка обновления", "error");
      }
    } catch (err) {
      console.error("Failed to update user:", err);
      toast("Ошибка обновления пользователя", "error");
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (!(await confirm({ title: "Удаление пользователя", description: "Вы уверены, что хотите удалить этого пользователя?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.users.delete(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
      toast("Пользователь удалён", "success");
    } catch (err) {
      console.error("Failed to delete user:", err);
      toast("Ошибка удаления пользователя", "error");
    }
  };

  const openEditDialog = (user: UserItem) => {
    const nameParts = user.name.split(" ");
    setSelectedUser(user);
    setFormData({
      first_name: nameParts[0] || "",
      last_name: nameParts.slice(1).join(" ") || "",
      email: user.email,
      phone: "",
      employee_id: "",
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

  const totalPages = Math.ceil(totalUsers / PAGE_SIZE) || 1;

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
    loadUsers,
    loadDepartments,
    handleCreateUser,
    handleUpdateUser,
    handleDeleteUser,
    openEditDialog,
    resetForm,
  };
}
