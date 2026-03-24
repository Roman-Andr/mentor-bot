import { fetchApi } from "./client";
import type { Department, DepartmentListResponse } from "./types";

export const departmentsApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.search) searchParams.set("search", params.search);
    const qs = searchParams.toString();
    return fetchApi<DepartmentListResponse>(`/api/v1/departments${qs ? `?${qs}` : ""}`);
  },
  create: (data: { name: string; description?: string | null }) =>
    fetchApi<Department>("/api/v1/departments", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: { name?: string; description?: string | null },
  ) =>
    fetchApi<Department>(`/api/v1/departments/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/departments/${id}`, {
      method: "DELETE",
    }),
};
