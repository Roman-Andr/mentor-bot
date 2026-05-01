import { apiClient } from "./client";

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
  getMyCertificates: async (): Promise<MyCertificate[]> => {
    const response = await apiClient.get("/certificates/my");
    return response.data;
  },

  downloadCertificate: async (certUid: string, locale: string = "en"): Promise<Blob> => {
    const response = await apiClient.get(`/certificates/${certUid}/download`, {
      params: { locale },
      responseType: "blob",
    });
    return response.data;
  },

  issueCertificate: async (checklistId: number): Promise<{ cert_uid: string; message: string }> => {
    const response = await apiClient.post("/certificates/issue", { checklist_id: checklistId });
    return response.data;
  },

  listCertificates: async (params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    from_date?: string;
    to_date?: string;
  }): Promise<CertificateListResponse> => {
    const response = await apiClient.get("/certificates/list", { params });
    return response.data;
  },
};
