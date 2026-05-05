import { fetchApi } from "./client";
import type { ApiResult } from "./client";

export interface Certificate {
  id: number;
  cert_uid: string;
  user_id: number;
  checklist_id: number;
  hr_id: number | null;
  mentor_id: number | null;
  issued_at: string;
}

export interface CertificateListResponse {
  total: number;
  certificates: Certificate[];
  page: number;
  size: number;
  pages: number;
}

export interface MyCertificate {
  cert_uid: string;
  checklist_id: number;
  issued_at: string | null;
}

export const certificatesApi = {
  getMyCertificates: async (): Promise<ApiResult<MyCertificate[]>> => {
    return fetchApi<MyCertificate[]>("/certificates/my");
  },

  downloadCertificate: async (certUid: string, locale: string = "en"): Promise<Blob> => {
    const response = await fetch(`/certificates/${certUid}/download?locale=${locale}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.blob();
  },

  issueCertificate: async (checklistId: number): Promise<ApiResult<{ cert_uid: string; message: string }>> => {
    return fetchApi<{ cert_uid: string; message: string }>("/certificates/issue", {
      method: "POST",
      body: JSON.stringify({ checklist_id: checklistId }),
    });
  },

  listCertificates: async (params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    from_date?: string;
    to_date?: string;
  }): Promise<ApiResult<CertificateListResponse>> => {
    const url = new URL("/certificates/list", window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    return fetchApi<CertificateListResponse>(url.toString());
  },
};
