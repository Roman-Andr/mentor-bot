import { fetchApi } from "./client";
import type { ChecklistStats, DepartmentSearchStats, SearchSummary, SearchTimeseriesPoint, TopQueryStats, ZeroResultQuery } from "@/types";

interface MonthlyStats {
  month: string;
  new_checklists: number;
  completed: number;
}

interface CompletionTimeStats {
  range: string;
  count: number;
}

interface DateRange {
  from_date?: string;
  to_date?: string;
}

interface TopArticleStats {
  article_id: number;
  title: string;
  view_count: number;
  unique_viewers: number;
}

interface TimeseriesPoint {
  bucket: string;
  views: number;
  unique_viewers: number;
}

interface CategoryStats {
  category_id: number;
  category_name: string;
  view_count: number;
}

interface TagStats {
  tag_id: number;
  tag_name: string;
  view_count: number;
}

interface KnowledgeSummary {
  total_views: number;
  unique_viewers: number;
  total_articles: number;
  avg_views_per_article: number;
}

export const analyticsApi = {
  checklistStats: (params?: { department_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.department_id !== undefined)
      searchParams.set("department_id", String(params.department_id));
    return fetchApi<ChecklistStats>(`/api/v1/checklists/stats/summary?${searchParams.toString()}`);
  },
  monthlyStats: (months: number = 6) => {
    return fetchApi<MonthlyStats[]>(`/api/v1/checklists/stats/monthly?months=${months}`);
  },
  completionTimeStats: () => {
    return fetchApi<CompletionTimeStats[]>("/api/v1/checklists/stats/completion-time");
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
  knowledge: {
    summary: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      return fetchApi<KnowledgeSummary>(`/api/v1/knowledge/analytics/summary?${searchParams.toString()}`);
    },
    topArticles: (params?: DateRange & { limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<TopArticleStats[]>(`/api/v1/knowledge/analytics/top-articles?${searchParams.toString()}`);
    },
    timeseries: (params?: DateRange & { granularity?: "day" | "week" }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.granularity) searchParams.set("granularity", params.granularity);
      return fetchApi<TimeseriesPoint[]>(`/api/v1/knowledge/analytics/views-timeseries?${searchParams.toString()}`);
    },
    byCategory: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      return fetchApi<CategoryStats[]>(`/api/v1/knowledge/analytics/views-by-category?${searchParams.toString()}`);
    },
    byTag: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      return fetchApi<TagStats[]>(`/api/v1/knowledge/analytics/views-by-tag?${searchParams.toString()}`);
    },
  },
  search: {
    summary: (params?: DateRange & { department_id?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      return fetchApi<SearchSummary>(`/api/v1/knowledge/search-analytics/summary?${searchParams.toString()}`);
    },
    topQueries: (params?: DateRange & { department_id?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.department_id !== undefined)
        searchParams.set("department_id", String(params.department_id));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<TopQueryStats[]>(`/api/v1/knowledge/search-analytics/top-queries?${searchParams.toString()}`);
    },
    zeroResults: (params?: DateRange & { department_id?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.department_id !== undefined)
        searchParams.set("department_id", String(params.department_id));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<ZeroResultQuery[]>(`/api/v1/knowledge/search-analytics/zero-results?${searchParams.toString()}`);
    },
    byDepartment: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      return fetchApi<DepartmentSearchStats[]>(`/api/v1/knowledge/search-analytics/by-department?${searchParams.toString()}`);
    },
    timeseries: (params?: DateRange & { granularity?: "day" | "week" }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.granularity) searchParams.set("granularity", params.granularity);
      return fetchApi<SearchTimeseriesPoint[]>(`/api/v1/knowledge/search-analytics/timeseries?${searchParams.toString()}`);
    },
  },
};
