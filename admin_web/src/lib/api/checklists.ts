import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type { Checklist, ChecklistListResponse, ChecklistStats } from "./types";

export const checklistsApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    status?: string;
    department_id?: number;
    overdue_only?: boolean;
    search?: string;
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<ChecklistListResponse>(`/api/v1/checklists${qs ? `?${qs}` : ""}`);
  },
  get: (id: number) => fetchApi<Checklist>(`/api/v1/checklists/${id}`),
  create: (data: {
    user_id: number;
    employee_id: string;
    template_id: number;
    start_date: string;
    due_date?: string | null;
    mentor_id?: number | null;
    hr_id?: number | null;
    notes?: string | null;
  }) =>
    fetchApi<Checklist>("/api/v1/checklists", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: {
      status?: string;
      progress_percentage?: number;
      mentor_id?: number | null;
      hr_id?: number | null;
      notes?: string | null;
      completed_at?: string | null;
    },
  ) =>
    fetchApi<Checklist>(`/api/v1/checklists/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/checklists/${id}`, {
      method: "DELETE",
    }),
  complete: (id: number) =>
    fetchApi<Checklist>(`/api/v1/checklists/${id}/complete`, { method: "POST" }),
  getProgress: (id: number) =>
    fetchApi<Record<string, unknown>>(`/api/v1/checklists/${id}/progress`),
  stats: (params?: { user_id?: number; department_id?: number }) => {
    const qs = buildQueryString(params);
    return fetchApi<ChecklistStats>(`/api/v1/checklists/stats/summary${qs ? `?${qs}` : ""}`);
  },
};
