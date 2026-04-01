import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type { Invitation, InvitationListResponse } from "./types";

export const invitationsApi = {
  list: (params?: {
    status?: string;
    role?: string;
    email?: string;
    department_id?: number;
    expired_only?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<InvitationListResponse>(`/api/v1/invitations${qs ? `?${qs}` : ""}`);
  },
  create: (data: {
    email: string;
    role: string;
    employee_id?: string;
    department_id?: number;
    position?: string;
    level?: string;
    mentor_id?: number;
    expires_in_days?: number;
  }) =>
    fetchApi<Invitation>("/api/v1/invitations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  resend: (id: number) =>
    fetchApi<Invitation>(`/api/v1/invitations/${id}/resend`, { method: "POST" }),
  revoke: (id: number) =>
    fetchApi<Invitation>(`/api/v1/invitations/${id}/revoke`, { method: "POST" }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/invitations/${id}`, {
      method: "DELETE",
    }),
};
