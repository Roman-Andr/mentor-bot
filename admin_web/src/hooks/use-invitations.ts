import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
import { useToast } from "@/components/ui/toast";
import { api, type Invitation } from "@/lib/api";

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

interface InvitationFormData {
  email: string;
  role: string;
  employee_id: string;
  department_id: number;
  position: string;
  level: string;
  mentor_id: number;
  expires_in_days: number;
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

const INVITATIONS_KEY = ["invitations"] as const;

export function useInvitations() {
  const { toast } = useToast();

  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState<InvitationFormData>(defaultFormData);
  const [emailTouched, setEmailTouched] = useState(false);
  const [createdUrl, setCreatedUrl] = useState<string | null>(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  const queryParams = {
    ...(debouncedSearch && { email: debouncedSearch }),
    ...(roleFilter !== "ALL" && { role: roleFilter }),
    ...(statusFilter === "EXPIRED" && { expired_only: true }),
    ...(statusFilter !== "ALL" && statusFilter !== "EXPIRED" && { status: statusFilter }),
  };

  const {
    data: invitationsData,
    isLoading: loading,
    refetch,
  } = useQuery({
    queryKey: [...INVITATIONS_KEY, queryParams],
    queryFn: () => api.invitations.list(queryParams),
    select: (result) =>
      result.data
        ? {
            invitations: result.data.invitations.map(toInvitationItem),
            stats: result.data.stats,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.invitations.create>[0]) =>
      api.invitations.create(data),
    onSuccess: (result) => {
      if (result.data) {
        setIsCreateDialogOpen(false);
        resetForm();
        setCreatedUrl(result.data.invitation_url);
        refetch();
        toast("Приглашение создано", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка создания приглашения", "error"),
  });

  const resendMutation = useMutation({
    mutationFn: (id: number) => api.invitations.resend(id),
    onSuccess: () => {
      refetch();
      toast("Приглашение отправлено повторно", "success");
    },
    onError: () => toast("Ошибка отправки приглашения", "error"),
  });

  const revokeMutation = useMutation({
    mutationFn: (id: number) => api.invitations.revoke(id),
    onSuccess: () => {
      refetch();
      toast("Приглашение отозвано", "success");
    },
    onError: () => toast("Ошибка отзыва приглашения", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.invitations.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        refetch();
        toast("Приглашение удалено", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления приглашения", "error"),
  });

  const handleCreateInvitation = () => {
    createMutation.mutate({
      email: formData.email,
      role: formData.role,
      employee_id: formData.employee_id || undefined,
      department_id: formData.department_id || undefined,
      position: formData.position || undefined,
      level: formData.level || undefined,
      mentor_id: formData.mentor_id || undefined,
      expires_in_days: formData.expires_in_days,
    });
  };

  const handleResendInvitation = (id: number) => {
    resendMutation.mutate(id);
  };

  const handleRevokeInvitation = (id: number) => {
    revokeMutation.mutate(id);
  };

  const handleDeleteInvitation = (id: number) => {
    deleteMutation.mutate(id);
  };

  const resetForm = () => {
    setFormData(defaultFormData);
    setEmailTouched(false);
  };

  const invitations = invitationsData?.invitations || [];
  const stats = invitationsData?.stats
    ? {
        total: invitationsData.stats.total,
        pending: invitationsData.stats.pending,
        accepted: invitationsData.stats.used || invitationsData.stats.pending,
        expired: invitationsData.stats.expired,
      }
    : { total: 0, pending: 0, accepted: 0, expired: 0 };

  return {
    invitations,
    stats,
    loading,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    formData,
    setFormData,
    emailTouched,
    setEmailTouched,
    searchQuery,
    setSearchQuery,
    roleFilter,
    setRoleFilter,
    statusFilter,
    setStatusFilter,
    createdUrl,
    setCreatedUrl,
    handleCreateInvitation,
    handleResendInvitation,
    handleRevokeInvitation,
    handleDeleteInvitation,
    resetForm,
    resetFilters: () => {
      setSearchQuery("");
      setRoleFilter("ALL");
      setStatusFilter("ALL");
    },
    isCreating: createMutation.isPending,
    isResending: resendMutation.isPending,
    isRevoking: revokeMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
