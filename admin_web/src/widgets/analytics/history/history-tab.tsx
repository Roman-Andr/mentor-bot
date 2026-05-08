"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "@/shared/hooks/use-translations";
import { api } from "@/shared/lib/api";
import { queryKeys } from "@/shared/lib/query-keys";
import { HistoryFilters } from "./history-filters";
import { HistoryTable } from "./history-table";
import { HistoryDetailDrawer } from "./history-detail-drawer";
import { HistoryEmpty } from "./history-empty";
import { Pagination } from "@/shared/ui/pagination";
import { Select } from "@/shared/ui/select";
import type { HistoryFilters as HistoryFiltersType, NormalizedAuditEvent } from "@/shared/types/audit";
import { subDays } from "date-fns";
import { useSearchParams, useRouter } from "next/navigation";

// Set default date range to last 7 days
const getDefaultDateRange = () => {
  const to = new Date();
  const from = subDays(to, 7);
  return {
    from_date: from.toISOString(),
    to_date: to.toISOString(),
  };
};

interface HistoryTabProps {
  onExportCSV?: () => void;
  onExportPDF?: () => void;
}

export function HistoryTab({ onExportCSV, onExportPDF }: HistoryTabProps) {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const router = useRouter();

  // Initialize filters from URL params
  const [filters, setFilters] = useState<HistoryFiltersType>(() => {
    const fromParam = searchParams.get("from_date");
    const toParam = searchParams.get("to_date");
    return {
      from_date: fromParam ?? getDefaultDateRange().from_date,
      to_date: toParam ?? getDefaultDateRange().to_date,
    };
  });

  const [page, setPage] = useState(() => {
    const pageParam = searchParams.get("page");
    return pageParam ? parseInt(pageParam, 10) : 1;
  });

  const [pageSize, setPageSize] = useState(() => {
    const pageSizeParam = searchParams.get("page_size");
    return pageSizeParam ? parseInt(pageSizeParam, 10) : 50;
  });

  const [selectedEvent, setSelectedEvent] = useState<NormalizedAuditEvent | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.analytics.history.feed({ ...filters, page, page_size: pageSize }),
    queryFn: () => api.audit.feed({ ...filters, page, page_size: pageSize }),
    staleTime: 30_000,
  });

  const handleFiltersChange = useCallback((newFilters: HistoryFiltersType) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    params.set("from_date", newFilters.from_date);
    params.set("to_date", newFilters.to_date);
    params.delete("page");
    router.push(`?${params.toString()}`, { scroll: false });
  }, [searchParams, router]);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    if (newPage === 1) {
      params.delete("page");
    } else {
      params.set("page", newPage.toString());
    }
    router.push(`?${params.toString()}`, { scroll: false });
  }, [searchParams, router]);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    params.set("page_size", newPageSize.toString());
    params.delete("page");
    router.push(`?${params.toString()}`, { scroll: false });
  }, [searchParams, router]);

  const handleRowClick = (event: NormalizedAuditEvent) => {
    setSelectedEvent(event);
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setSelectedEvent(null);
  };

  const auditData = data?.success ? data.data : null;
  const totalPages = auditData ? Math.ceil(auditData.total / pageSize) : 0;

  return (
    <div className="space-y-6">
      <HistoryFilters filters={filters} onChange={handleFiltersChange} />

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading...</div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">
          Error loading audit events. Please try again.
        </div>
      ) : !auditData || auditData.items.length === 0 ? (
        <HistoryEmpty />
      ) : (
        <>
          {auditData.partial && auditData.partial.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              {t("analytics.history.partial")}
            </div>
          )}

          <HistoryTable events={auditData.items} onRowClick={handleRowClick} />

          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {t("analytics.history.showing", {
                count: auditData.items.length,
                total: auditData.total,
              })}
            </div>
            <div className="flex items-center gap-4">
              <Select
                value={String(pageSize)}
                onChange={(value) => {
                  handlePageSizeChange(parseInt(value, 10));
                }}
                options={[
                  { value: "25", label: "25" },
                  { value: "50", label: "50" },
                  { value: "100", label: "100" },
                ]}
                className="w-20"
              />
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            </div>
          </div>
        </>
      )}

      <HistoryDetailDrawer
        event={selectedEvent}
        open={drawerOpen}
        onClose={handleDrawerClose}
      />
    </div>
  );
}
