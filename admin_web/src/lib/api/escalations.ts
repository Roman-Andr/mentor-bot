import { fetchApi } from "./client";
import type { EscalationRequest, EscalationListResponse } from "./types";

export const escalationsApi = {
  list: (params?: {
    user_id?: number;
    assigned_to?: number;
    escalation_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.user_id !== undefined) searchParams.set("user_id", String(params.user_id));
    if (params?.assigned_to !== undefined)
      searchParams.set("assigned_to", String(params.assigned_to));
    if (params?.escalation_type) searchParams.set("escalation_type", params.escalation_type);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<EscalationListResponse>(`/api/v1/escalations?${searchParams.toString()}`);
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
