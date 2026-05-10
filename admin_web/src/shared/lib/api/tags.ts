import { fetchApi } from "./client";
import { buildQueryString } from "@/shared/lib/utils/query-builder";

const MAX_TAGS_LIMIT = 100;

export interface Tag {
  id: number;
  name: string;
  slug: string;
  article_count?: number;
  created_at?: string;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[а-яё]/g, (ch) => {
      const map: Record<string, string> = {
        а: "a",
        б: "b",
        в: "v",
        г: "g",
        д: "d",
        е: "e",
        ё: "e",
        ж: "zh",
        з: "z",
        и: "i",
        й: "y",
        к: "k",
        л: "l",
        м: "m",
        н: "n",
        о: "o",
        п: "p",
        р: "r",
        с: "s",
        т: "t",
        у: "u",
        ф: "f",
        х: "h",
        ц: "c",
        ч: "ch",
        ш: "sh",
        щ: "shch",
        ъ: "",
        ы: "y",
        э: "e",
        ю: "yu",
        я: "ya",
      };
      return map[ch] || ch;
    })
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function normalizeTagCreatePayload(data: { name: string; slug?: string }) {
  const name = data.name.trim();
  return {
    name,
    slug: (data.slug || slugify(name)).trim(),
  };
}

export const tagsApi = {
  list: (params?: { search?: string; skip?: number; limit?: number }) => {
    const safeParams = params?.limit
      ? { ...params, limit: Math.min(params.limit, MAX_TAGS_LIMIT) }
      : params;
    const qs = buildQueryString(safeParams);
    return fetchApi<Tag[]>(`/api/v1/tags${qs ? `?${qs}` : ""}`);
  },
  get: (id: number) => fetchApi<Tag>(`/api/v1/tags/${id}`),
  create: (data: { name: string; slug?: string }) =>
    fetchApi<Tag>("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify(normalizeTagCreatePayload(data)),
    }),
  update: (id: number, data: { name?: string }) =>
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
