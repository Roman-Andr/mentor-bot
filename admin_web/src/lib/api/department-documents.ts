import { fetchApi } from "./client";
import { buildQueryString } from "@/lib/utils/query-builder";
import type {
  DepartmentDocument,
  DepartmentDocumentCreate,
  DepartmentDocumentListResponse,
  DepartmentDocumentUpdate,
} from "@/types/department-document";

export const departmentDocumentsApi = {
  list: (params?: { department_id?: number; category?: string; is_public?: boolean }) => {
    const qs = buildQueryString(params);
    return fetchApi<DepartmentDocumentListResponse>(
      `/api/v1/knowledge/department-documents${qs ? `?${qs}` : ""}`
    );
  },
  get: (id: number) => fetchApi<DepartmentDocument>(`/api/v1/knowledge/department-documents/${id}`),
  create: (data: FormData) =>
    fetchApi<DepartmentDocument>("/api/v1/knowledge/department-documents", {
      method: "POST",
      body: data,
    }),
  update: (id: number, data: DepartmentDocumentUpdate) =>
    fetchApi<DepartmentDocument>(`/api/v1/knowledge/department-documents/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/knowledge/department-documents/${id}`, {
      method: "DELETE",
    }),
  downloadUrl: (id: number) => `/api/v1/knowledge/department-documents/${id}/download`,
};
