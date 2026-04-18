import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type { User, UserListResponse } from "@/types";

export const usersApi = {
  list: (params?: {
    role?: string;
    department_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: "asc" | "desc";
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<UserListResponse>(`/api/v1/users${qs ? `?${qs}` : ""}`);
  },
  get: (id: number) => fetchApi<User>(`/api/v1/users/${id}`),
  create: (data: Partial<User> & { password?: string }) =>
    fetchApi<User>("/api/v1/users", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<User>) =>
    fetchApi<User>(`/api/v1/users/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/users/${id}`, {
      method: "DELETE",
    }),
};
