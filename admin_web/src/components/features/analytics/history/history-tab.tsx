"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "@/hooks/use-translations";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { HistoryFilters } from "./history-filters";
import { HistoryTable } from "./history-table";
import { HistoryDetailDrawer } from "./history-detail-drawer";
import { HistoryEmpty } from "./history-empty";
import { Pagination } from "@/components/ui/pagination";
import type { HistoryFilters as HistoryFiltersType, NormalizedAuditEvent } from "@/types/audit";
import { subDays } from "date-fns";

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
  const [filters, setFilters] = useState<HistoryFiltersType>(getDefaultDateRange());
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedEvent, setSelectedEvent] = useState<NormalizedAuditEvent | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.analytics.history.feed({ ...filters, page, page_size: pageSize }),
    queryFn: () => api.audit.feed({ ...filters, page, page_size: pageSize }),
    staleTime: 30_000,
  });

  const handleFiltersChange = (newFilters: HistoryFiltersType) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };

  const handleRowClick = (event: NormalizedAuditEvent) => {
    setSelectedEvent(event);
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setSelectedEvent(null);
  };

  const totalPages = data?.data ? Math.ceil(data.data.total / pageSize) : 0;

  return (
    <div className="space-y-6">
      <HistoryFilters filters={filters} onChange={handleFiltersChange} />

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading...</div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">
          Error loading audit events. Please try again.
        </div>
      ) : !data?.data || data.data.items.length === 0 ? (
        <HistoryEmpty />
      ) : (
        <>
          {data.data.partial && data.data.partial.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              {t("analytics.history.partial")}
            </div>
          )}

          <HistoryTable events={data.data.items} onRowClick={handleRowClick} />

          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {t("analytics.history.showing", {
                count: data.data.items.length,
                total: data.data.total,
              })}
            </div>
            <div className="flex items-center gap-4">
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(parseInt(e.target.value, 10));
                  setPage(1);
                }}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
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
