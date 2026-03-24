import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
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

/** Maps an API Invitation to the local InvitationItem representation. */
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

/** Custom hook that manages invitation state and CRUD operations. */
export function useInvitations() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [invitations, setInvitations] = useState<InvitationItem[]>([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, accepted: 0, expired: 0 });
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState<InvitationFormData>(defaultFormData);
  const [emailTouched, setEmailTouched] = useState(false);
  const [createdUrl, setCreatedUrl] = useState<string | null>(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  const loadInvitations = useCallback(async () => {
    setLoading(true);
    try {
      const params: { email?: string } = {};
      if (debouncedSearch) params.email = debouncedSearch;
      const response = await api.invitations.list(params);
      if (response.data) {
        setInvitations(response.data.invitations.map(toInvitationItem));
        if (response.data.stats) {
          setStats({
            total: response.data.stats.total,
            pending: response.data.stats.pending,
            accepted: response.data.stats.used || 0,
            expired: response.data.stats.expired,
          });
        }
      }
    } catch (err) {
      console.error("Failed to load invitations:", err);
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch]);

  useEffect(() => {
    loadInvitations();
  }, [loadInvitations]);

  const resetForm = useCallback(() => {
    setFormData(defaultFormData);
    setEmailTouched(false);
  }, []);

  const handleCreateInvitation = async () => {
    try {
      const response = await api.invitations.create({
        email: formData.email,
        role: formData.role,
        employee_id: formData.employee_id || undefined,
        department_id: formData.department_id || undefined,
        position: formData.position || undefined,
        level: formData.level || undefined,
        mentor_id: formData.mentor_id || undefined,
        expires_in_days: formData.expires_in_days,
      });
      if (response.data) {
        setIsCreateDialogOpen(false);
        resetForm();
        setCreatedUrl(response.data.invitation_url);
        await loadInvitations();
        toast("Приглашение создано", "success");
      } else {
        toast(response.error || "Ошибка создания", "error");
      }
    } catch (err) {
      console.error("Failed to create invitation:", err);
      toast("Ошибка создания приглашения", "error");
    }
  };

  const handleResendInvitation = async (id: number) => {
    try {
      await api.invitations.resend(id);
      await loadInvitations();
      toast("Приглашение отправлено повторно", "success");
    } catch (err) {
      console.error("Failed to resend invitation:", err);
      toast("Ошибка отправки приглашения", "error");
    }
  };

  const handleRevokeInvitation = async (id: number) => {
    try {
      await api.invitations.revoke(id);
      await loadInvitations();
      toast("Приглашение отозвано", "success");
    } catch (err) {
      console.error("Failed to revoke invitation:", err);
      toast("Ошибка отзыва приглашения", "error");
    }
  };

  const handleDeleteInvitation = async (id: number) => {
    if (!(await confirm({ title: "Удаление приглашения", description: "Вы уверены, что хотите удалить это приглашение?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.invitations.delete(id);
      await loadInvitations();
      toast("Приглашение удалено", "success");
    } catch (err) {
      console.error("Failed to delete invitation:", err);
      toast("Ошибка удаления приглашения", "error");
    }
  };

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
    createdUrl,
    setCreatedUrl,
    loadInvitations,
    handleCreateInvitation,
    handleResendInvitation,
    handleRevokeInvitation,
    handleDeleteInvitation,
    resetForm,
  };
}
