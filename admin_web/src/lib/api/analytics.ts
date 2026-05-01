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
    const queryString = searchParams.toString();
    const url = queryString ? `/api/v1/checklists/stats/summary?${queryString}` : "/api/v1/checklists/stats/summary";
    return fetchApi<ChecklistStats>(url);
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
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/analytics/summary?${queryString}` : "/api/v1/knowledge/analytics/summary";
      return fetchApi<KnowledgeSummary>(url);
    },
    topArticles: (params?: DateRange & { limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.limit) searchParams.set("limit", String(params.limit));
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/analytics/top-articles?${queryString}` : "/api/v1/knowledge/analytics/top-articles";
      return fetchApi<TopArticleStats[]>(url);
    },
    timeseries: (params?: DateRange & { granularity?: "day" | "week" }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.granularity) searchParams.set("granularity", params.granularity);
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/analytics/views-timeseries?${queryString}` : "/api/v1/knowledge/analytics/views-timeseries";
      return fetchApi<TimeseriesPoint[]>(url);
    },
    byCategory: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/analytics/views-by-category?${queryString}` : "/api/v1/knowledge/analytics/views-by-category";
      return fetchApi<CategoryStats[]>(url);
    },
    byTag: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/analytics/views-by-tag?${queryString}` : "/api/v1/knowledge/analytics/views-by-tag";
      return fetchApi<TagStats[]>(url);
    },
  },
  search: {
    summary: (params?: DateRange & { department_id?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.department_id !== undefined) searchParams.set("department_id", String(params.department_id));
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/search-analytics/summary?${queryString}` : "/api/v1/knowledge/search-analytics/summary";
      return fetchApi<SearchSummary>(url);
    },
    topQueries: (params?: DateRange & { department_id?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.department_id !== undefined)
        searchParams.set("department_id", String(params.department_id));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/search-analytics/top-queries?${queryString}` : "/api/v1/knowledge/search-analytics/top-queries";
      return fetchApi<TopQueryStats[]>(url);
    },
    zeroResults: (params?: DateRange & { department_id?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.department_id !== undefined)
        searchParams.set("department_id", String(params.department_id));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/search-analytics/zero-results?${queryString}` : "/api/v1/knowledge/search-analytics/zero-results";
      return fetchApi<ZeroResultQuery[]>(url);
    },
    byDepartment: (params?: DateRange) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/search-analytics/by-department?${queryString}` : "/api/v1/knowledge/search-analytics/by-department";
      return fetchApi<DepartmentSearchStats[]>(url);
    },
    timeseries: (params?: DateRange & { granularity?: "day" | "week" }) => {
      const searchParams = new URLSearchParams();
      if (params?.from_date) searchParams.set("from_date", params.from_date);
      if (params?.to_date) searchParams.set("to_date", params.to_date);
      if (params?.granularity) searchParams.set("granularity", params.granularity);
      const queryString = searchParams.toString();
      const url = queryString ? `/api/v1/knowledge/search-analytics/timeseries?${queryString}` : "/api/v1/knowledge/search-analytics/timeseries";
      return fetchApi<SearchTimeseriesPoint[]>(url);
    },
  },
};
