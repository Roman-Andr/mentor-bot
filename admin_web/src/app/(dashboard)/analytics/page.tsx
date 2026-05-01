"use client";

import { useState, useEffect, useMemo } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PDFExportButton } from "@/components/features/reports/pdf-export-button";
import { TabSwitcher } from "@/components/ui/tab-switcher";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { ChecklistStats, SearchSummary, TopQueryStats, ZeroResultQuery, DepartmentSearchStats, SearchTimeseriesPoint } from "@/types";
import { PageContent } from "@/components/layout/page-content";
import { AnalyticsStats } from "@/components/features/analytics/analytics-stats";
import { MonthlyChart } from "@/components/features/analytics/monthly-chart";
import { DepartmentChart } from "@/components/features/analytics/department-chart";
import { CompletionTimeChart } from "@/components/features/analytics/completion-time-chart";
import { ChecklistStatus } from "@/components/features/analytics/checklist-status";
import { KnowledgeSummaryCards } from "@/components/features/analytics/knowledge/knowledge-summary-cards";
import { KnowledgeTopArticlesChart } from "@/components/features/analytics/knowledge/knowledge-top-articles-chart";
import { KnowledgeViewsTimeseries } from "@/components/features/analytics/knowledge/knowledge-views-timeseries";
import { KnowledgeViewsByCategory } from "@/components/features/analytics/knowledge/knowledge-views-by-category";
import { KnowledgeViewsByTag } from "@/components/features/analytics/knowledge/knowledge-views-by-tag";
import { KnowledgeDateRangePicker } from "@/components/features/analytics/knowledge/knowledge-date-range-picker";
import { departmentsApi } from "@/lib/api/departments";
import { AnalyticsPageSkeleton } from "@/components/ui/page-skeleton";
import { useQuery } from "@tanstack/react-query";
import { SearchSummaryCards } from "@/components/features/analytics/search/search-summary-cards";
import { SearchTopQueriesTable } from "@/components/features/analytics/search/search-top-queries-table";
import { SearchZeroResultsTable } from "@/components/features/analytics/search/search-zero-results-table";
import { SearchByDepartmentChart } from "@/components/features/analytics/search/search-by-department-chart";
import { SearchTimeseriesChart } from "@/components/features/analytics/search/search-timeseries-chart";
import { SearchFilters } from "@/components/features/analytics/search/search-filters";

export default function AnalyticsPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState("onboarding");
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [userCount, setUserCount] = useState(0);
  const [monthlyData, setMonthlyData] = useState<Array<{ month: string; newUsers: number; completed: number }>>([]);
  const [completionTimeData, setCompletionTimeData] = useState<Array<{ range: string; count: number }>>([]);
  const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({});
  
  // Knowledge analytics state
  const [dateRange, setDateRange] = useState<{ from_date?: string; to_date?: string }>({});
  const [granularity, setGranularity] = useState<"day" | "week">("day");

  const tabs = [
    { id: "onboarding", label: t("analytics.onboardingTab") },
    { id: "knowledge", label: t("analytics.knowledgeTab") },
    { id: "search", label: t("analytics.search.title") },
  ];

  // Search analytics state
  const [searchSummary, setSearchSummary] = useState<SearchSummary | null>(null);
  const [searchTopQueries, setSearchTopQueries] = useState<TopQueryStats[]>([]);
  const [searchZeroResults, setSearchZeroResults] = useState<ZeroResultQuery[]>([]);
  const [searchByDepartment, setSearchByDepartment] = useState<DepartmentSearchStats[]>([]);
  const [searchTimeseries, setSearchTimeseries] = useState<SearchTimeseriesPoint[]>([]);
  const [searchFilters, setSearchFilters] = useState<{ from_date?: string; to_date?: string; department_id?: number }>({});
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    async function loadOnboardingData() {
      try {
        const [statsResult, usersResult, monthlyResult, completionResult, deptResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
          api.analytics.monthlyStats(),
          api.analytics.completionTimeStats(),
          departmentsApi.list({ limit: 1000 }),
        ]);

        if (statsResult.data) {
          setStats(statsResult.data);
        }
        if (usersResult.data) {
          setUserCount(usersResult.data.total);
        }
        if (monthlyResult.data) {
          setMonthlyData(monthlyResult.data.map(m => ({
            month: m.month,
            newUsers: m.new_checklists,
            completed: m.completed,
          })));
        }
        if (completionResult.data) {
          setCompletionTimeData(completionResult.data);
        }
        if (deptResult.data?.departments) {
          const map: Record<string, string> = {};
          deptResult.data.departments.forEach((dept) => {
            map[String(dept.id)] = dept.name;
          });
          setDepartmentMap(map);
        }
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadOnboardingData();
  }, []);

  // Knowledge analytics queries with React Query caching
  const { data: knowledgeSummary, isLoading: summaryLoading } = useQuery({
    queryKey: queryKeys.analytics.knowledge.summary(dateRange),
    queryFn: () => api.analytics.knowledge.summary(dateRange),
    enabled: activeTab === "knowledge",
    staleTime: 60000,
  });

  const { data: topArticles, isLoading: topArticlesLoading } = useQuery({
    queryKey: queryKeys.analytics.knowledge.topArticles({ ...dateRange, limit: 10 }),
    queryFn: () => api.analytics.knowledge.topArticles({ ...dateRange, limit: 10 }),
    enabled: activeTab === "knowledge",
    staleTime: 60000,
  });

  const { data: timeseriesData, isLoading: timeseriesLoading } = useQuery({
    queryKey: queryKeys.analytics.knowledge.timeseries({ ...dateRange, granularity }),
    queryFn: () => api.analytics.knowledge.timeseries({ ...dateRange, granularity }),
    enabled: activeTab === "knowledge",
    staleTime: 60000,
  });

  const { data: categoryData, isLoading: categoryLoading } = useQuery({
    queryKey: queryKeys.analytics.knowledge.byCategory(dateRange),
    queryFn: () => api.analytics.knowledge.byCategory(dateRange),
    enabled: activeTab === "knowledge",
    staleTime: 60000,
  });

  const { data: tagData, isLoading: tagLoading } = useQuery({
    queryKey: queryKeys.analytics.knowledge.byTag(dateRange),
    queryFn: () => api.analytics.knowledge.byTag(dateRange),
    enabled: activeTab === "knowledge",
    staleTime: 60000,
  });

  const knowledgeLoading = summaryLoading || topArticlesLoading || timeseriesLoading || categoryLoading || tagLoading;

  useEffect(() => {
    async function loadSearchData() {
      if (activeTab !== "search") return;

      setSearchLoading(true);
      try {
        const [summaryResult, topQueriesResult, zeroResultsResult, byDepartmentResult, timeseriesResult] = await Promise.all([
          api.analytics.search.summary(searchFilters),
          api.analytics.search.topQueries({ ...searchFilters, limit: 20 }),
          api.analytics.search.zeroResults({ ...searchFilters, limit: 20 }),
          api.analytics.search.byDepartment(searchFilters),
          api.analytics.search.timeseries({ ...searchFilters, granularity: "day" }),
        ]);

        if (summaryResult.data) {
          setSearchSummary(summaryResult.data);
        }
        if (topQueriesResult.data) {
          setSearchTopQueries(topQueriesResult.data);
        }
        if (zeroResultsResult.data) {
          setSearchZeroResults(zeroResultsResult.data);
        }
        if (byDepartmentResult.data) {
          setSearchByDepartment(byDepartmentResult.data);
        }
        if (timeseriesResult.data) {
          setSearchTimeseries(timeseriesResult.data);
        }
      } catch (err) {
        console.error("Failed to load search analytics:", err);
      } finally {
        setSearchLoading(false);
      }
    }
    loadSearchData();
  }, [activeTab, searchFilters]);

  const departmentData = useMemo(() =>
    stats?.by_department
      ? Object.entries(stats.by_department)
          .filter(([id]) => id !== "None" && id !== "null")
          .map(([id, value], index) => {
            const colors = [
              "#3b82f6", "#8b5cf6", "#22c55e", "#f97316", "#ec4899", "#06b6d4", "#eab308",
            ];
            return {
              name: departmentMap[id] || `Department ${id}`,
              value,
              color: colors[index % colors.length],
            };
          })
      : [],
    [stats, departmentMap]
  );

  const handleExport = () => {
    const rows = [
      [t("analytics.totalNewbies"), String(stats?.total || userCount)],
      [t("common.completed"), String(stats?.completed || 0)],
      [t("common.inProgress"), String(stats?.in_progress || 0)],
      [t("analytics.overdue"), String(stats?.overdue || 0)],
      [t("analytics.averageTime"), String(Math.round(stats?.avg_completion_days || 0))],
      [t("analytics.completionRate"), String(Math.round(stats?.completion_rate || 0))],
    ];

    const csvContent = rows
      .map((row) => row.join(","))
      .join("\n");

    const bom = "\uFEFF";
    const content = bom + csvContent;

    const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "analytics_export.csv";
    link.click();
  };

  if (loading) {
    return (
      <PageContent title={t("analytics.title")} subtitle={t("analytics.overview")}>
        <AnalyticsPageSkeleton />
      </PageContent>
    );
  }

  return (
    <PageContent
      title={t("analytics.title")}
      subtitle={t("analytics.overview")}
      actions={
        <div className="flex items-center gap-2">
          <PDFExportButton
            data={{
              stats,
              userCount,
              monthlyData,
              completionTimeData,
              departmentData,
            }}
            variant="outline"
            size="default"
          />
          <Button onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            CSV
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <TabSwitcher tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === "onboarding" && (
          <>
            <AnalyticsStats stats={stats} userCount={userCount} />

            <div className="grid gap-6 lg:grid-cols-2">
              <MonthlyChart data={monthlyData} />
              <DepartmentChart data={departmentData} />
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <CompletionTimeChart data={completionTimeData} />
              <ChecklistStatus stats={stats} />
            </div>
          </>
        )}

        {activeTab === "knowledge" && (
          <>
            <KnowledgeDateRangePicker onChange={setDateRange} />

            {knowledgeLoading ? (
              <AnalyticsPageSkeleton />
            ) : (
              <>
                <KnowledgeSummaryCards summary={knowledgeSummary?.data || null} />

                <div className="grid gap-6 lg:grid-cols-2">
                  <KnowledgeTopArticlesChart data={topArticles?.data || []} />
                  <KnowledgeViewsTimeseries
                    data={timeseriesData?.data || []}
                    onGranularityChange={setGranularity}
                    currentGranularity={granularity}
                  />
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <KnowledgeViewsByCategory data={categoryData?.data || []} />
                  <KnowledgeViewsByTag data={tagData?.data || []} />
                </div>
              </>
            )}
          </>
        )}

        {activeTab === "search" && (
          <>
            <SearchFilters onFiltersChange={setSearchFilters} />

            {searchLoading ? (
              <AnalyticsPageSkeleton />
            ) : (
              <>
                <SearchSummaryCards summary={searchSummary} />

                <div className="grid gap-6 lg:grid-cols-2">
                  <SearchTopQueriesTable data={searchTopQueries} />
                  <SearchZeroResultsTable data={searchZeroResults} />
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <SearchTimeseriesChart data={searchTimeseries} />
                  <SearchByDepartmentChart data={searchByDepartment} />
                </div>
              </>
            )}
          </>
        )}
      </div>
    </PageContent>
  );
}
