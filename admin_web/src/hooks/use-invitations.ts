import { useEffect } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import type { Invitation } from "@/types";
import { useMutation } from "@tanstack/react-query";

export interface InvitationItem {
  id: number;
  email: string;
  role: string;
  department: string;
  status: string;
  createdAt: string;
  expiresAt: string;
  invitationUrl: string;
}

export interface InvitationFormData {
  email: string;
  role: string;
  employee_id: string;
  department_id: number;
  position: string;
  level: string;
  mentor_id: number;
  expires_in_days: number;
}

interface ExtendedState {
  emailTouched: boolean;
  createdUrl: string | null;
}

const defaultFormData: InvitationFormData = {
  email: "",
  role: "NEWBIE",
  employee_id: "",
  department_id: 0,
  position: "",
  level: "",
  mentor_id: 0,
  expires_in_days: 7,
};

const defaultExtendedState: ExtendedState = {
  emailTouched: false,
  createdUrl: null,
};

function toInvitationItem(i: Invitation): InvitationItem {
  return {
    id: i.id,
    email: i.email,
    role: i.role,
    department: i.department?.name || "",
    status:
      i.is_expired && i.status === "PENDING"
        ? "EXPIRED"
        : i.status === "USED"
          ? "ACCEPTED"
          : i.status,
    createdAt: i.created_at ? i.created_at.split("T")[0] : "",
    expiresAt: i.expires_at ? i.expires_at.split("T")[0] : "",
    invitationUrl: i.invitation_url,
  };
}

function toPayload(form: InvitationFormData) {
  return {
    email: form.email,
    role: form.role,
    employee_id: form.employee_id || undefined,
    department_id: form.department_id || undefined,
    position: form.position || undefined,
    level: form.level || undefined,
    mentor_id: form.mentor_id || undefined,
    expires_in_days: form.expires_in_days,
  };
}

export function useInvitations() {
  const entity = useEntity<InvitationItem, InvitationFormData, ReturnType<typeof toPayload>, ReturnType<typeof toPayload>>({
    entityName: "Приглашение",
    translationNamespace: "invitations",
    queryKeyPrefix: "invitations",
    listFn: (params) => api.invitations.list(params),
    listDataKey: "invitations",
    createFn: (data) => api.invitations.create(data),
    deleteFn: (id) => api.invitations.delete(id),
    defaultForm: defaultFormData,
    mapItem: (item: unknown) => toInvitationItem(item as Invitation),
    toCreatePayload: toPayload,
    toUpdatePayload: toPayload,
    toForm: () => defaultFormData, // No edit for invitations
    searchable: true,
    searchParamName: "email",
    filters: [
      { name: "role", defaultValue: "ALL" },
      { name: "status", defaultValue: "ALL" },
    ],
    sortable: true,
    labels: {
      createdKey: "invitations.created",
      deletedKey: "invitations.deleted",
      createErrorKey: "invitations.createError",
      deleteErrorKey: "invitations.deleteError",
    },
  });

  // Initialize emailTouched and createdUrl state
  useEffect(() => {
    if (entity.extendedState.emailTouched === undefined) {
      entity.setExtendedState(() => ({ emailTouched: false, createdUrl: null }));
    }
  }, []);

  // Custom mutations
  const resendMutation = useMutation({
    mutationFn: (id: number) => api.invitations.resend(id),
    onSuccess: () => {
      entity.invalidate();
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: number) => api.invitations.revoke(id),
    onSuccess: () => {
      entity.invalidate();
    },
  });

  // Stats derived from entity items (no duplicate API call)
  const stats = {
    total: entity.totalCount,
    pending: entity.items.filter(i => i.status === "PENDING").length,
    accepted: entity.items.filter(i => i.status === "ACCEPTED").length,
    expired: entity.items.filter(i => i.status === "EXPIRED").length,
  };

  const handleCreateInvitation = () => {
    const payload = toPayload(entity.formData);
    entity.createFn?.(payload).then((result) => {
      if (result?.error) {
        // Error is already handled by entity hook's onError
        return;
      }
      if (result?.data) {
        entity.setExtendedState((prev) => ({
          ...(prev as unknown as ExtendedState),
          createdUrl: (result.data as { invitation_url: string }).invitation_url,
        }));
        entity.invalidate();
        entity.setIsCreateDialogOpen(false);
        entity.resetForm();
      }
    });
  };

  const resetForm = () => {
    entity.resetForm();
    entity.setExtendedState(() => defaultExtendedState as unknown as Record<string, unknown>);
  };

  return {
    // Data
    invitations: entity.items,
    stats,
    loading: entity.loading,
    totalCount: entity.totalCount,
    totalPages: entity.totalPages,

    // Pagination
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,

    // Search & Filters
    searchQuery: entity.searchQuery,
    setSearchQuery: entity.setSearchQuery,
    roleFilter: entity.filterValues.role ?? "ALL",
    setRoleFilter: (value: string) => entity.setFilterValue("role", value),
    statusFilter: entity.filterValues.status ?? "ALL",
    setStatusFilter: (value: string) => entity.setFilterValue("status", value),

    // Dialog
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,
    emailTouched: (entity.extendedState as unknown as ExtendedState).emailTouched ?? false,
    setEmailTouched: (touched: boolean) =>
      entity.setExtendedState((prev) => ({ ...(prev as unknown as ExtendedState), emailTouched: touched })),
    createdUrl: (entity.extendedState as unknown as ExtendedState).createdUrl ?? null,
    setCreatedUrl: (url: string | null) =>
      entity.setExtendedState((prev) => ({ ...(prev as unknown as ExtendedState), createdUrl: url })),

    // Handlers
    handleCreateInvitation,
    handleResendInvitation: (id: number) => resendMutation.mutate(id),
    handleRevokeInvitation: (id: number) => revokeMutation.mutate(id),
    handleDeleteInvitation: entity.handleDelete,
    resetForm,
    resetFilters: entity.resetFilters,

    // Loading states
    isCreating: entity.isSubmitting,
    isResending: resendMutation.isPending,
    isRevoking: revokeMutation.isPending,
    isDeleting: entity.isDeleting,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,
  };
}
