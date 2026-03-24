import { fetchApi } from "./client";
import type { User, UserListResponse } from "./types";

export const usersApi = {
  list: (params?: {
    role?: string;
    department_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.role) searchParams.set("role", params.role);
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    if (params?.search) searchParams.set("search", params.search);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<UserListResponse>(`/api/v1/users?${searchParams.toString()}`);
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
