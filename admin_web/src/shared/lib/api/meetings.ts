import { fetchApi } from "./client";
import { buildQueryString } from "@/shared/lib/utils/query-builder";
import type { Meeting, MeetingListResponse } from "@/shared/types";

export interface MeetingMaterial {
  id: number;
  meeting_id: number;
  title: string;
  description?: string | null;
  url: string;
  type: "PDF" | "LINK" | "DOC" | "IMAGE" | "VIDEO";
  order: number;
  created_at: string;
}

export const meetingsApi = {
  list: (params?: {
    meeting_type?: string;
    department_id?: number;
    position?: string;
    level?: string;
    is_mandatory?: boolean;
    search?: string;
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
    duration_minutes?: number;
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
  getMaterials: (meetingId: number) =>
    fetchApi<MeetingMaterial[]>(`/api/v1/meetings/${meetingId}/materials`),
  addMaterial: (
    meetingId: number,
    data: { title: string; description?: string | null; url: string; type: string; order?: number },
  ) =>
    fetchApi<MeetingMaterial>(`/api/v1/meetings/${meetingId}/materials`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteMaterial: (materialId: number) =>
    fetchApi<void>(`/api/v1/meetings/materials/${materialId}`, { method: "DELETE" }),
};
