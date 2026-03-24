import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, type EscalationRequest } from "@/lib/api";

export interface EscalationItem {
  id: number;
  userId: number;
  type: string;
  source: string;
  status: string;
  reason: string;
  assignedTo: number | null;
  createdAt: string;
  resolvedAt: string | null;
}

function mapEscalation(e: EscalationRequest): EscalationItem {
  return {
    id: e.id,
    userId: e.user_id,
    type: e.type,
    source: e.source,
    status: e.status,
    reason: e.reason || "",
    assignedTo: e.assigned_to,
    createdAt: e.created_at,
    resolvedAt: e.resolved_at,
  };
}

export function useEscalations() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const debouncedSearch = useDebounce(searchQuery);
  const pageSize = 20;

  const loadEscalations = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      };
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (typeFilter !== "ALL") params.escalation_type = typeFilter;

      const response = await api.escalations.list(params);
      if (response.data) {
        let items = response.data.requests.map(mapEscalation);
        if (debouncedSearch) {
          const q = debouncedSearch.toLowerCase();
          items = items.filter(
            (e) =>
              e.reason.toLowerCase().includes(q) ||
              e.type.toLowerCase().includes(q) ||
              String(e.userId).includes(q),
          );
        }
        setEscalations(items);
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages || 1);
      }
    } catch (err) {
      console.error("Failed to load escalations:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter, typeFilter, debouncedSearch]);

  useEffect(() => {
    loadEscalations();
  }, [loadEscalations]);

  const handleResolve = async (id: number) => {
    try {
      const response = await api.escalations.resolve(id);
      if (response.data) {
        setEscalations(
          escalations.map((e) => (e.id === id ? { ...e, status: "RESOLVED", resolvedAt: new Date().toISOString() } : e)),
        );
        toast("Запрос решён", "success");
      } else {
        toast(response.error || "Ошибка", "error");
      }
    } catch (err) {
      console.error("Failed to resolve escalation:", err);
      toast("Ошибка решения запроса", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление запроса", description: "Вы уверены, что хотите удалить этот запрос?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.escalations.delete(id);
      setEscalations(escalations.filter((e) => e.id !== id));
      setTotalCount((c) => c - 1);
      toast("Запрос удалён", "success");
    } catch (err) {
      console.error("Failed to delete escalation:", err);
      toast("Ошибка удаления запроса", "error");
    }
  };

  return {
    escalations,
    loading,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    typeFilter,
    setTypeFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    loadEscalations,
    handleResolve,
    handleDelete,
  };
}
