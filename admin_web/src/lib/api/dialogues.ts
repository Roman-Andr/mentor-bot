import { fetchApi } from "./client";
import type { DialogueScenario, DialogueScenarioListResponse, DialogueStep } from "./types";

export const dialoguesApi = {
  list: (params?: {
    category?: string;
    is_active?: boolean;
    search?: string;
    skip?: number;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    if (params?.search) searchParams.set("search", params.search);
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<DialogueScenarioListResponse>(
      `/api/v1/dialogue-scenarios?${searchParams.toString()}`,
    );
  },
  get: (id: number) => fetchApi<DialogueScenario>(`/api/v1/dialogue-scenarios/${id}`),
  getActive: (params?: { skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<DialogueScenarioListResponse>(
      `/api/v1/dialogue-scenarios/active?${searchParams.toString()}`,
    );
  },
  create: (data: {
    title: string;
    description?: string;
    keywords?: string[];
    category: string;
    is_active?: boolean;
    display_order?: number;
    steps?: {
      step_number: number;
      question: string;
      answer_type: string;
      options?: { label: string; next_step: number }[];
      answer_content?: string;
      next_step_id?: number | null;
      parent_step_id?: number | null;
      is_final?: boolean;
    }[];
  }) =>
    fetchApi<DialogueScenario>("/api/v1/dialogue-scenarios", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: {
      title?: string;
      description?: string;
      keywords?: string[];
      category?: string;
      is_active?: boolean;
      display_order?: number;
    },
  ) =>
    fetchApi<DialogueScenario>(`/api/v1/dialogue-scenarios/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/dialogue-scenarios/${id}`, {
      method: "DELETE",
    }),
  addStep: (
    scenarioId: number,
    data: {
      step_number: number;
      question: string;
      answer_type: string;
      options?: { label: string; next_step: number }[];
      answer_content?: string;
      next_step_id?: number | null;
      parent_step_id?: number | null;
      is_final?: boolean;
    },
  ) =>
    fetchApi<DialogueStep>(`/api/v1/dialogue-scenarios/${scenarioId}/steps`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateStep: (
    stepId: number,
    data: {
      step_number?: number;
      question?: string;
      answer_type?: string;
      options?: { label: string; next_step: number }[];
      answer_content?: string;
      next_step_id?: number | null;
      parent_step_id?: number | null;
      is_final?: boolean;
    },
  ) =>
    fetchApi<DialogueStep>(`/api/v1/dialogue-scenarios/steps/${stepId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteStep: (stepId: number) =>
    fetchApi<{ message: string }>(`/api/v1/dialogue-scenarios/steps/${stepId}`, {
      method: "DELETE",
    }),
  reorderSteps: (scenarioId: number, stepIds: number[]) =>
    fetchApi<{ message: string }>(`/api/v1/dialogue-scenarios/${scenarioId}/reorder`, {
      method: "POST",
      body: JSON.stringify({ step_ids: stepIds }),
    }),
};
