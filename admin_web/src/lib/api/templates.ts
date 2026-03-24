import { fetchApi } from "./client";
import type { Template, TemplateWithTasks, TaskTemplate } from "./types";

export const templatesApi = {
  list: (params?: { department_id?: number; status?: string; skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    if (params?.status) searchParams.set("status", params.status);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<Template[]>(`/api/v1/templates?${searchParams.toString()}`);
  },
  get: (id: number) => fetchApi<TemplateWithTasks>(`/api/v1/templates/${id}`),
  create: (data: Partial<Template>) =>
    fetchApi<Template>("/api/v1/templates", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<Template>) =>
    fetchApi<Template>(`/api/v1/templates/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/templates/${id}`, {
      method: "DELETE",
    }),
  publish: (id: number) =>
    fetchApi<Template>(`/api/v1/templates/${id}/publish`, { method: "POST" }),
  clone: (id: number) => fetchApi<Template>(`/api/v1/templates/${id}/clone`, { method: "POST" }),
  addTask: (
    templateId: number,
    data: {
      template_id: number;
      title: string;
      description?: string | null;
      instructions?: string | null;
      category: string;
      order?: number;
      due_days: number;
      estimated_minutes?: number | null;
    },
  ) =>
    fetchApi<TaskTemplate>(`/api/v1/templates/${templateId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
