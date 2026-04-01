import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
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

const ESCALATIONS_KEY = ["escalations"] as const;

export function useEscalations() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(statusFilter !== "ALL" && { status: statusFilter }),
    ...(typeFilter !== "ALL" && { escalation_type: typeFilter }),
  };

  const {
    data: escalationsData,
    isLoading: loading,
    refetch,
  } = useQuery({
    queryKey: [...ESCALATIONS_KEY, queryParams],
    queryFn: () => api.escalations.list(queryParams),
    select: (result) =>
      result.data
        ? {
            requests: result.data.requests.map(mapEscalation),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const resolveMutation = useMutation({
    mutationFn: (id: number) => api.escalations.resolve(id),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: ESCALATIONS_KEY });
        toast("Запрос решён", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка решения запроса", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.escalations.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: ESCALATIONS_KEY });
        toast("Запрос удалён", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления запроса", "error"),
  });

  const handleResolve = (id: number) => {
    resolveMutation.mutate(id);
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const escalations = escalationsData?.requests || [];
  const totalCount = escalationsData?.total || 0;
  const totalPages = escalationsData?.pages || 1;

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
    loadEscalations: refetch,
    handleResolve,
    handleDelete,
    resetFilters: () => {
      setSearchQuery("");
      setStatusFilter("ALL");
      setTypeFilter("ALL");
      setCurrentPage(1);
    },
    isResolving: resolveMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
