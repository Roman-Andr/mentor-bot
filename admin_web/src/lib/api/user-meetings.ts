import { fetchApi } from "./client";

export interface UserMeetingResponse {
  id: number;
  user_id: number;
  meeting_id: number;
  status: string;
  scheduled_at: string | null;
  completed_at: string | null;
  feedback: string | null;
  rating: number | null;
  created_at: string;
}

export interface UserMeetingListResponse {
  total: number;
  items: UserMeetingResponse[];
  page: number;
  size: number;
  pages: number;
}

export const userMeetingsApi = {
  list: (params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<UserMeetingListResponse>(`/api/v1/user-meetings/my?${searchParams.toString()}`);
  },
  listByMeeting: (meetingId: number, params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<UserMeetingListResponse>(`/api/v1/user-meetings/by-meeting/${meetingId}?${searchParams.toString()}`);
  },
  listAll: (params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<UserMeetingListResponse>(`/api/v1/user-meetings?${searchParams.toString()}`);
  },
  assign: (data: { user_id: number; meeting_id: number; scheduled_at?: string | null }) =>
    fetchApi<UserMeetingResponse>("/api/v1/user-meetings/assign", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  autoAssign: (userId: number, params?: { department_id?: number; position?: string; level?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    if (params?.position) searchParams.set("position", params.position);
    if (params?.level) searchParams.set("level", params.level);
    return fetchApi<UserMeetingResponse[]>(`/api/v1/user-meetings/auto-assign/${userId}?${searchParams.toString()}`, {
      method: "POST",
    });
  },
  get: (id: number) => fetchApi<UserMeetingResponse>(`/api/v1/user-meetings/${id}`),
  update: (id: number, data: { status?: string; scheduled_at?: string | null }) =>
    fetchApi<UserMeetingResponse>(`/api/v1/user-meetings/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  complete: (id: number, data: { feedback?: string | null; rating?: number | null }) =>
    fetchApi<UserMeetingResponse>(`/api/v1/user-meetings/${id}/complete`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  delete: (id: number) => fetchApi<void>(`/api/v1/user-meetings/${id}`, { method: "DELETE" }),
};
