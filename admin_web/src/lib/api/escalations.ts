import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type { EscalationRequest, EscalationListResponse } from "@/types";

export const escalationsApi = {
  list: (params?: {
    user_id?: number;
    assigned_to?: number;
    escalation_type?: string;
    status?: string;
    search?: string;
    skip?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: "asc" | "desc";
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<EscalationListResponse>(`/api/v1/escalations${qs ? `?${qs}` : ""}`);
  },
  create: (data: {
    user_id: number;
    type: string;
    source: string;
    reason?: string | null;
    context?: Record<string, unknown>;
    assigned_to?: number | null;
  }) =>
    fetchApi<EscalationRequest>("/api/v1/escalations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  get: (id: number) => fetchApi<EscalationRequest>(`/api/v1/escalations/${id}`),
  update: (
    id: number,
    data: {
      status?: string;
      assigned_to?: number | null;
      resolution_note?: string | null;
    },
  ) =>
    fetchApi<EscalationRequest>(`/api/v1/escalations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  assign: (id: number, assigneeId: number) =>
    fetchApi<EscalationRequest>(`/api/v1/escalations/${id}/assign/${assigneeId}`, {
      method: "POST",
    }),
  resolve: (id: number) =>
    fetchApi<EscalationRequest>(`/api/v1/escalations/${id}/resolve`, {
      method: "POST",
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/escalations/${id}`, {
      method: "DELETE",
    }),
};
