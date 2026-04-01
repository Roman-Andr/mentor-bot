import { fetchApi, fetchUpload } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type {
  Article,
  ArticleListResponse,
  AttachmentListResponse,
  Attachment,
  Category,
  CategoryListResponse,
} from "./types";

export const articlesApi = {
  list: (params?: {
    status?: string;
    category_id?: number;
    department_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
    pinned_only?: boolean;
    featured_only?: boolean;
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<ArticleListResponse>(`/api/v1/articles${qs ? `?${qs}` : ""}`);
  },
  get: (id: number | string) => fetchApi<Article>(`/api/v1/articles/${id}`),
  create: (data: {
    title: string;
    content: string;
    excerpt?: string;
    category_id?: number | null;
    department_id?: number | null;
    position?: string | null;
    level?: string | null;
    status?: string;
    is_pinned?: boolean;
    is_featured?: boolean;
    keywords?: string[];
  }) =>
    fetchApi<Article>("/api/v1/articles", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: {
      title?: string;
      content?: string;
      excerpt?: string;
      category_id?: number | null;
      department_id?: number | null;
      position?: string | null;
      level?: string | null;
      status?: string;
      is_pinned?: boolean;
      is_featured?: boolean;
      keywords?: string[];
    },
  ) =>
    fetchApi<Article>(`/api/v1/articles/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/articles/${id}`, {
      method: "DELETE",
    }),
  publish: (id: number) => fetchApi<Article>(`/api/v1/articles/${id}/publish`, { method: "POST" }),
};

export const categoriesApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    parent_id?: number | null;
    department_id?: number;
    search?: string;
    include_tree?: boolean;
  }) => {
    const qs = buildQueryString(params);
    return fetchApi<CategoryListResponse>(`/api/v1/categories${qs ? `?${qs}` : ""}`);
  },
  create: (data: {
    name: string;
    slug: string;
    description?: string | null;
    parent_id?: number | null;
    order?: number;
    department_id?: number | null;
    position?: string | null;
    level?: string | null;
    icon?: string | null;
    color?: string | null;
  }) =>
    fetchApi<Category>("/api/v1/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: {
      name?: string;
      description?: string | null;
      parent_id?: number | null;
      order?: number;
      department_id?: number | null;
      position?: string | null;
      level?: string | null;
      icon?: string | null;
      color?: string | null;
    },
  ) =>
    fetchApi<Category>(`/api/v1/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/categories/${id}`, {
      method: "DELETE",
    }),
};

export const attachmentsApi = {
  listByArticle: (articleId: number) =>
    fetchApi<AttachmentListResponse>(`/api/v1/attachments/article/${articleId}`),
  upload: (articleId: number, file: File, description?: string) => {
    const formData = new FormData();
    formData.append("article_id", String(articleId));
    formData.append("file", file);
    if (description) formData.append("description", description);
    return fetchUpload<Attachment>("/api/v1/attachments/upload", formData);
  },
  uploadMultiple: (articleId: number, files: File[]) => {
    const formData = new FormData();
    formData.append("article_id", String(articleId));
    for (const file of files) {
      formData.append("files", file);
    }
    return fetchUpload<AttachmentListResponse>("/api/v1/attachments/batch-upload", formData);
  },
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/attachments/${id}`, {
      method: "DELETE",
    }),
  getDownloadUrl: (articleId: number, filename: string) =>
    `/api/v1/attachments/file/${articleId}/${encodeURIComponent(filename)}`,
};
