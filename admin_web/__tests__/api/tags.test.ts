import { beforeEach, describe, expect, it, vi } from "vitest";
import { tagsApi } from "@/shared/lib/api/tags";

const mockFetchApi = vi.fn();
const mockBuildQueryString = vi.fn<(_params?: unknown) => string>(() => "");

vi.mock("@/shared/lib/api/client", () => ({
  fetchApi: (endpoint: string, options?: RequestInit) => mockFetchApi(endpoint, options),
}));

vi.mock("@/shared/lib/utils/query-builder", () => ({
  buildQueryString: (params?: unknown) => mockBuildQueryString(params),
}));

describe("tagsApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("list calls the tags endpoint without wrapping the backend array response", async () => {
    const tags = [{ id: 1, name: "Onboarding", slug: "onboarding" }];
    mockFetchApi.mockResolvedValueOnce({ success: true, data: tags });

    const result = await tagsApi.list();

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags", undefined);
    expect(result).toEqual({ success: true, data: tags });
  });

  it("list appends query parameters capped to the backend maximum", () => {
    mockBuildQueryString.mockReturnValueOnce("search=hr&limit=100");

    tagsApi.list({ search: "hr", limit: 200 });

    expect(mockBuildQueryString).toHaveBeenCalledWith({ search: "hr", limit: 100 });
    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags?search=hr&limit=100", undefined);
  });

  it("create sends tag payload with a generated slug", () => {
    tagsApi.create({ name: "HR" });

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify({ name: "HR", slug: "hr" }),
    });
  });

  it("keeps unknown transliteration characters in generated slugs until normalization", () => {
    tagsApi.create({ name: "Training Ω" });

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify({ name: "Training Ω", slug: "training" }),
    });
  });

  it("create transliterates generated slugs", () => {
    tagsApi.create({ name: "Обучение персонала ящ" });

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify({ name: "Обучение персонала ящ", slug: "obuchenie-personala-yashch" }),
    });
  });

  it("create trims explicit slugs and names", () => {
    tagsApi.create({ name: "  HR docs  ", slug: "  hr-docs  " });

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify({ name: "HR docs", slug: "hr-docs" }),
    });
  });

  it("calls item endpoints for get, update, delete, and merge", () => {
    tagsApi.get(7);
    tagsApi.update(7, { name: "Culture" });
    tagsApi.delete(7);
    tagsApi.merge(7, 9);

    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags/7", undefined);
    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags/7", {
      method: "PUT",
      body: JSON.stringify({ name: "Culture" }),
    });
    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags/7", { method: "DELETE" });
    expect(mockFetchApi).toHaveBeenCalledWith("/api/v1/tags/7/merge/9", { method: "POST" });
  });
});
