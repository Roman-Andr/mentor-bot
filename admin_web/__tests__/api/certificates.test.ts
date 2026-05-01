/** Tests for certificates API client. */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { certificatesApi } from "@/lib/api/certificates";
import { fetchApi } from "@/lib/api/client";

// Mock the fetchApi function
vi.mock("@/lib/api/client", () => ({
  fetchApi: vi.fn(),
}));

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

      (fetchApi as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: mockCertificates,
      });

      const result = await certificatesApi.getMyCertificates();

      expect(fetchApi).toHaveBeenCalledWith("/certificates/my");
      expect(result).toEqual({ data: mockCertificates });
    });

    it("should handle API errors", async () => {
      (fetchApi as ReturnType<typeof vi.fn>).mockRejectedValue(
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
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        ok: true,
        blob: async () => mockBlob,
      }));

      const result = await certificatesApi.downloadCertificate("cert-123", "en");

      expect(global.fetch).toHaveBeenCalledWith(
        "/certificates/cert-123/download?locale=en",
      );
      expect(result).toBe(mockBlob);
    });

    it("should use default locale if not provided", async () => {
      const mockBlob = new Blob(["PDF content"], { type: "application/pdf" });
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        ok: true,
        blob: async () => mockBlob,
      }));

      const result = await certificatesApi.downloadCertificate("cert-123");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/certificates/cert-123/download?locale=en"),
      );
      expect(result).toBe(mockBlob);
    });
  });

  describe("issueCertificate", () => {
    it("should issue certificate for checklist", async () => {
      const mockResponse = {
        cert_uid: "new-cert-456",
        message: "Certificate issued successfully",
      };

      (fetchApi as ReturnType<typeof vi.fn>).mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await certificatesApi.issueCertificate(123);

      expect(fetchApi).toHaveBeenCalledWith("/certificates/issue", {
        method: "POST",
        body: JSON.stringify({ checklist_id: 123 }),
      });
      expect(result).toEqual({ success: true, data: mockResponse });
    });

    it("should handle validation errors", async () => {
      (fetchApi as ReturnType<typeof vi.fn>).mockRejectedValue({
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
        pages: 1,
      };

      (fetchApi as ReturnType<typeof vi.fn>).mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await certificatesApi.listCertificates({
        skip: 0,
        limit: 50,
        user_id: 10,
      });

      const fetchCall = (fetchApi as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(fetchCall[0]).toContain("/certificates/list");
      expect(fetchCall[0]).toContain("skip=0");
      expect(fetchCall[0]).toContain("limit=50");
      expect(fetchCall[0]).toContain("user_id=10");
      expect(result).toEqual({ success: true, data: mockResponse });
    });

    it("should list certificates without filters", async () => {
      const mockResponse = {
        certificates: [],
        total: 0,
        page: 1,
        size: 50,
        pages: 0,
      };

      (fetchApi as ReturnType<typeof vi.fn>).mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await certificatesApi.listCertificates();

      const fetchCall = (fetchApi as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(fetchCall[0]).toContain("/certificates/list");
      expect(result).toEqual({ success: true, data: mockResponse });
    });
  });
});
