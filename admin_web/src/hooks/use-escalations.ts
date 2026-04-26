import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { EscalationRequest } from "@/types";
import { useQuery, useMutation } from "@tanstack/react-query";

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

// Placeholder form type - escalations don't have create/edit
interface EscalationFormData {
  _placeholder: boolean;
}

const defaultFormData: EscalationFormData = {
  _placeholder: true,
};

function toForm(): EscalationFormData {
  return defaultFormData;
}

function toPayload(): Record<string, never> {
  return {};
}

export function useEscalations() {
  const entity = useEntity<EscalationItem, EscalationFormData, ReturnType<typeof toPayload>, ReturnType<typeof toPayload>>({
    entityName: "Запрос",
    translationNamespace: "escalations",
    queryKeyPrefix: "escalations",
    listFn: (params) => api.escalations.list(params),
    listDataKey: "requests",
    deleteFn: (id) => api.escalations.delete(id),
    defaultForm: defaultFormData,
    mapItem: (item: unknown) => mapEscalation(item as EscalationRequest),
    toCreatePayload: toPayload,
    toUpdatePayload: toPayload,
    toForm,
    searchable: true,
    searchParamName: "search",
    filters: [
      { name: "status", defaultValue: "ALL" },
      { name: "type", defaultValue: "ALL", paramName: "escalation_type" },
    ],
    sortable: true,
    sortFieldParam: "sort_by",
    sortDirectionParam: "sort_order",
    labels: {
      deletedKey: "escalations.deleted",
      deleteErrorKey: "escalations.deleteError",
    },
  });

  // Fetch users for name lookup
  const { data: usersData } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => api.users.list({ limit: 1000 }),
    select: (result) => {
      const map = new Map<number, string>();
      if (result.data) {
        for (const u of result.data.users) {
          map.set(u.id, `${u.first_name ?? ""} ${u.last_name ?? ""}`.trim() || String(u.id));
        }
      }
      return map;
    },
    staleTime: 5 * 60 * 1000,
  });

  const getUserName = (id: number | null): string => {
    if (id === null || id === undefined) return "-";
    return usersData?.get(id) ?? String(id);
  };

  const resolveMutation = useMutation({
    mutationFn: (id: number) => api.escalations.resolve(id),
    onSuccess: () => {
      entity.invalidate();
    },
  });

  const handleResolve = (id: number) => {
    resolveMutation.mutate(id);
  };

  return {
    // Data
    escalations: entity.items,
    loading: entity.loading,
    getUserName,

    // Pagination
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    totalCount: entity.totalCount,
    totalPages: entity.totalPages,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,

    // Search & Filters
    searchQuery: entity.searchQuery,
    setSearchQuery: entity.setSearchQuery,
    statusFilter: entity.filterValues.status ?? "ALL",
    setStatusFilter: (value: string) => entity.setFilterValue("status", value),
    typeFilter: entity.filterValues.type ?? "ALL",
    setTypeFilter: (value: string) => entity.setFilterValue("type", value),

    // Handlers
    loadEscalations: entity.invalidate,
    handleResolve,
    handleDelete: entity.handleDelete,
    resetFilters: entity.resetFilters,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,

    // Loading states
    isResolving: resolveMutation.isPending,
    isDeleting: entity.isDeleting,
  };
}
