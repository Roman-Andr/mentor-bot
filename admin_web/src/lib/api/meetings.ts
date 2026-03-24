import { fetchApi } from "./client";
import type { Meeting, MeetingListResponse } from "./types";

export const meetingsApi = {
  list: (params?: {
    meeting_type?: string;
    department_id?: number;
    position?: string;
    level?: string;
    is_mandatory?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.meeting_type) searchParams.set("meeting_type", params.meeting_type);
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    if (params?.position) searchParams.set("position", params.position);
    if (params?.level) searchParams.set("level", params.level);
    if (params?.is_mandatory !== undefined)
      searchParams.set("is_mandatory", String(params.is_mandatory));
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<MeetingListResponse>(`/api/v1/meetings?${searchParams.toString()}`);
  },
  create: (data: {
    title: string;
    description?: string | null;
    type: string;
    department_id?: number | null;
    position?: string | null;
    level?: string | null;
    deadline_days?: number;
    is_mandatory?: boolean;
    order?: number;
  }) =>
    fetchApi<Meeting>("/api/v1/meetings", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  get: (id: number) => fetchApi<Meeting>(`/api/v1/meetings/${id}`),
  update: (id: number, data: Partial<Meeting>) =>
    fetchApi<Meeting>(`/api/v1/meetings/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) => fetchApi<void>(`/api/v1/meetings/${id}`, { method: "DELETE" }),
};
