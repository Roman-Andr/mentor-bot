/** Tests for certificates API client. */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { certificatesApi } from "@/lib/api/certificates";

// Mock the apiClient
vi.mock("@/lib/api", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import { apiClient } from "@/lib/api";

describe("certificatesApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getMyCertificates", () => {
    it("should fetch my certificates", async () => {
      const mockCertificates = [
        { cert_uid: "cert-1", issued_at: "2024-01-15T00:00:00Z" },
        { cert_uid: "cert-2", issued_at: "2024-02-20T00:00:00Z" },
      ];

      (apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockCertificates,
      });

      const result = await certificatesApi.getMyCertificates();

      expect(apiClient.get).toHaveBeenCalledWith("/certificates/my");
      expect(result).toEqual(mockCertificates);
    });

    it("should handle API errors", async () => {
      (apiClient.get as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error("Network error")
      );

      await expect(certificatesApi.getMyCertificates()).rejects.toThrow(
        "Network error"
      );
    });
  });

  describe("downloadCertificate", () => {
    it("should download certificate PDF", async () => {
      const mockBlob = new Blob(["PDF content"], { type: "application/pdf" });

      (apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockBlob,
      });

      const result = await certificatesApi.downloadCertificate("cert-123", "en");

      expect(apiClient.get).toHaveBeenCalledWith("/certificates/cert-123/download", {
        params: { locale: "en" },
        responseType: "blob",
      });
      expect(result).toBe(mockBlob);
    });

    it("should use default locale if not provided", async () => {
      const mockBlob = new Blob(["PDF content"], { type: "application/pdf" });

      (apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockBlob,
      });

      await certificatesApi.downloadCertificate("cert-123");

      expect(apiClient.get).toHaveBeenCalledWith("/certificates/cert-123/download", {
        params: { locale: "en" },
        responseType: "blob",
      });
    });
  });

  describe("issueCertificate", () => {
    it("should issue certificate for checklist", async () => {
      const mockResponse = {
        cert_uid: "new-cert-456",
        message: "Certificate issued successfully",
      };

      (apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockResponse,
      });

      const result = await certificatesApi.issueCertificate(123);

      expect(apiClient.post).toHaveBeenCalledWith("/certificates/issue", {
        checklist_id: 123,
      });
      expect(result).toEqual(mockResponse);
    });

    it("should handle validation errors", async () => {
      (apiClient.post as ReturnType<typeof vi.fn>).mockRejectedValue({
        response: { status: 400, data: { detail: "Checklist must be completed" } },
      });

      await expect(certificatesApi.issueCertificate(123)).rejects.toThrow();
    });
  });

  describe("listCertificates", () => {
    it("should list certificates with filters", async () => {
      const mockResponse = {
        certificates: [
          {
            id: 1,
            cert_uid: "cert-1",
            user_id: 10,
            checklist_id: 100,
            issued_at: "2024-01-15T00:00:00Z",
          },
        ],
        total: 1,
        page: 1,
        size: 50,
      };

      (apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockResponse,
      });

      const result = await certificatesApi.listCertificates({
        skip: 0,
        limit: 50,
        user_id: 10,
      });

      expect(apiClient.get).toHaveBeenCalledWith("/certificates/list", {
        params: { skip: 0, limit: 50, user_id: 10 },
      });
      expect(result).toEqual(mockResponse);
    });

    it("should list certificates without filters", async () => {
      const mockResponse = {
        certificates: [],
        total: 0,
        page: 1,
        size: 50,
      };

      (apiClient.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockResponse,
      });

      const result = await certificatesApi.listCertificates();

      expect(apiClient.get).toHaveBeenCalledWith("/certificates/list", {
        params: {},
      });
      expect(result).toEqual(mockResponse);
    });
  });
});
