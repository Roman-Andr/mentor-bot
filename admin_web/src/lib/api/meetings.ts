import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
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
    const qs = buildQueryString(params);
    return fetchApi<MeetingListResponse>(`/api/v1/meetings${qs ? `?${qs}` : ""}`);
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
