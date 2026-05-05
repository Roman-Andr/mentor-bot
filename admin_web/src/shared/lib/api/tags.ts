import { fetchApi } from "./client";
import { buildQueryString } from "@/shared/lib/utils/query-builder";

export interface Tag {
  id: number;
  name: string;
  slug: string;
  article_count?: number;
  created_at?: string;
}

export interface TagListResponse {
  total: number;
  tags: Tag[];
}

export const tagsApi = {
  list: (params?: { search?: string; skip?: number; limit?: number }) => {
    const qs = buildQueryString(params);
    return fetchApi<TagListResponse>(`/api/v1/tags${qs ? `?${qs}` : ""}`);
  },
  get: (id: number) => fetchApi<Tag>(`/api/v1/tags/${id}`),
  create: (data: { name: string; slug?: string }) =>
    fetchApi<Tag>("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: { name?: string; slug?: string }) =>
    fetchApi<Tag>(`/api/v1/tags/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/tags/${id}`, {
      method: "DELETE",
    }),
  merge: (sourceId: number, targetId: number) =>
    fetchApi<Tag>(`/api/v1/tags/${sourceId}/merge/${targetId}`, {
      method: "POST",
    }),
};
