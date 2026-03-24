import { fetchApi } from "./client";
import type { ChecklistStats } from "./types";

export const analyticsApi = {
  checklistStats: (params?: { department_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
    return fetchApi<ChecklistStats>(`/api/v1/checklists/stats/summary?${searchParams.toString()}`);
  },
  onboardingProgress: () =>
    fetchApi<{
      checklists: Array<{
        user_id: number;
        employee_id?: string;
        department?: string;
        start_date: string;
        progress_percentage: number;
        days_remaining?: number;
        status: string;
      }>;
    }>("/api/v1/checklists?overdue_only=false&limit=50"),
};
