import { fetchApi } from "./client";
import type { AuditFeedResponse, AuditFeedParams, HistoryFilters, NormalizedAuditEvent } from "@/types/audit";

export const auditApi = {
  feed: (params: AuditFeedParams) => {
    const searchParams = new URLSearchParams();
    if (params.from_date) searchParams.set("from_date", params.from_date);
    if (params.to_date) searchParams.set("to_date", params.to_date);
    if (params.sources && params.sources.length > 0) searchParams.set("sources", params.sources.join(","));
    if (params.event_types && params.event_types.length > 0) searchParams.set("event_types", params.event_types.join(","));
    if (params.actor_id !== undefined) searchParams.set("actor_id", String(params.actor_id));
    searchParams.set("page", String(params.page));
    searchParams.set("page_size", String(params.page_size));

    const queryString = searchParams.toString();
    const url = queryString ? `/api/v1/audit-feed?${queryString}` : "/api/v1/audit-feed";
    return fetchApi<AuditFeedResponse>(url);
  },

  // Helper to fetch all events for a filter set (used by CSV/PDF export)
  fetchAll: async (filters: HistoryFilters, maxRows: number = 10000): Promise<NormalizedAuditEvent[]> => {
    const allEvents: NormalizedAuditEvent[] = [];
    let page = 1;
    const pageSize = 100;

    while (true) {
      const result = await auditApi.feed({
        ...filters,
        page,
        page_size: pageSize,
      });

      if (!result.success || !result.data) {
        break;
      }

      allEvents.push(...result.data.items);

      if (allEvents.length >= maxRows || result.data.items.length < pageSize) {
        break;
      }

      page++;
    }

    return allEvents.slice(0, maxRows);
  },
};
