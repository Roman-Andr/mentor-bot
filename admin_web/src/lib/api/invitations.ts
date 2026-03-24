import { fetchApi } from "./client";
import type { Invitation, InvitationListResponse } from "./types";

export const invitationsApi = {
  list: (params?: {
    status?: string;
    email?: string;
    department_id?: number;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.email) searchParams.set("email", params.email);
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<InvitationListResponse>(`/api/v1/invitations?${searchParams.toString()}`);
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
