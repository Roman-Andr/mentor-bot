import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { User } from "@/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useCallback } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { useToast } from "@/hooks/use-toast";

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
  telegram_id?: number | null;
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
  telegram_id: number | null;
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
  telegram_id: null,
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
    telegram_id: u.telegram_id,
  };
}

function toCreatePayload(form: UserFormData) {
  return {
    first_name: form.first_name,
    last_name: form.last_name || null,
    email: form.email,
    phone: form.phone || null,
    employee_id: form.employee_id,
    department_id: form.department_id || undefined,
    position: form.position || null,
    level: form.level || null,
    role: form.role,
    is_active: form.is_active,
    password: form.password,
    telegram_id: form.telegram_id,
  };
}

function toUpdatePayload(form: UserFormData) {
  return {
    first_name: form.first_name,
    last_name: form.last_name || null,
    email: form.email,
    phone: form.phone || null,
    employee_id: form.employee_id,
    department_id: form.department_id || undefined,
    position: form.position || null,
    level: form.level || null,
    role: form.role,
    is_active: form.is_active,
    telegram_id: form.telegram_id,
  };
}

function toForm(user: UserItem): UserFormData {
  const nameParts = user.name.split(" ");
  return {
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
    telegram_id: user.telegram_id || null,
  };
}

export function useUsers() {
  const entity = useEntity<UserItem, UserFormData, ReturnType<typeof toCreatePayload>, ReturnType<typeof toUpdatePayload>>({
    entityName: "Пользователь",
    translationNamespace: "users",
    queryKeyPrefix: "users",
    listFn: (params) => api.users.list(params),
    listDataKey: "users",
    createFn: (data) => api.users.create(data),
    updateFn: (id, data) => api.users.update(id, data),
    deleteFn: (id) => api.users.delete(id),
    defaultForm: INITIAL_FORM,
    mapItem: (item: unknown) => mapUser(item as User),
    toCreatePayload,
    toUpdatePayload,
    toForm,
    pageSize: PAGE_SIZE,
    searchable: true,
    searchParamName: "search",
    filters: [
      { name: "role", defaultValue: "ALL", paramName: "role" },
      { name: "department", defaultValue: "ALL", paramName: "department_id", transform: (v) => parseInt(v) },
    ],
    labels: {
      createdKey: "users.created",
      updatedKey: "users.updated",
      deletedKey: "users.deleted",
      createErrorKey: "users.createError",
      updateErrorKey: "users.updateError",
      deleteErrorKey: "users.deleteError",
    },
    sortable: true,
    sortFieldParam: "sort_by",
    sortDirectionParam: "sort_order",
  });

  // Fetch departments for the filter dropdown
  const { data: departmentsData } = useQuery({
    queryKey: queryKeys.departments.all,
    queryFn: () => api.departments.list({ limit: 1000 }),
    select: (result) => result.success ? result.data?.departments || [] : [],
  });

  const departments = departmentsData || [];

  // Mentor assignment state and handlers
  const t = useTranslations();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [assignMentorDialogOpen, setAssignMentorDialogOpen] = useState(false);
  const [selectedUserForMentor, setSelectedUserForMentor] = useState<UserItem | null>(null);

  // Fetch current mentor for selected user
  const { data: userMentorsData, refetch: refetchUserMentors } = useQuery({
    queryKey: queryKeys.userMentors.byUser(selectedUserForMentor?.id || 0),
    queryFn: () => api.userMentors.list({ user_id: selectedUserForMentor?.id }),
    enabled: !!selectedUserForMentor && assignMentorDialogOpen,
    select: (result) => result.success ? result.data?.relations || [] : [],
  });

  const currentMentor = userMentorsData?.find((m) => m.is_active) || null;

  const openAssignMentorDialog = useCallback((user: UserItem) => {
    setSelectedUserForMentor(user);
    setAssignMentorDialogOpen(true);
  }, []);

  const handleAssignMentor = useCallback(async (userId: number, mentorId: number) => {
    // TODO: Implement assignMentor API when available
    console.warn('assignMentor API not yet implemented');
  }, []);

  const handleUnassignMentor = useCallback(async (mentorRelationId: number) => {
    const resp = await api.userMentors.delete(mentorRelationId);
    if (resp.success) {
      toast(t("mentorUnassigned"), "success");
      await queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    } else {
      toast(resp.error.message || t("unassignMentorError"), "error");
    }
  }, [t, toast, queryClient]);

  return {
    // Data - map generic names to specific names for backward compatibility
    users: entity.items,
    loading: entity.loading,
    totalUsers: entity.totalCount,

    // Pagination
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    totalPages: entity.totalPages,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,

    // Search
    searchQuery: entity.searchQuery,
    setSearchQuery: entity.setSearchQuery,

    // Filters
    roleFilter: entity.filterValues.role ?? "ALL",
    setRoleFilter: (value: string) => entity.setFilterValue("role", value),
    departmentFilter: entity.filterValues.department ?? "ALL",
    setDepartmentFilter: (value: string) => entity.setFilterValue("department", value),
    resetFilters: entity.resetFilters,

    // Departments
    departments,
    loadDepartments: () => {}, // Handled by React Query stale time

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedUser: entity.selectedItem,
    setSelectedUser: entity.setSelectedItem,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Handlers
    handleCreateUser: entity.handleSubmit,
    handleUpdateUser: entity.handleSubmit,
    handleDeleteUser: entity.handleDelete,
    openEditDialog: entity.openEditDialog,
    resetForm: entity.resetForm,

    // Loading states
    isCreating: entity.isSubmitting,
    isUpdating: entity.isSubmitting,
    isDeleting: entity.isDeleting,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,

    // Mentor assignment
    assignMentorDialogOpen,
    setAssignMentorDialogOpen,
    selectedUserForMentor,
    currentMentor,
    openAssignMentorDialog,
    handleAssignMentor,
    handleUnassignMentor,
  };
}
