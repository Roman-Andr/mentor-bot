import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { NORMALIZE_MAP } from "./normalize";
import type { NormalizedAuditEvent, AuditSource } from "@/types/audit";

const SERVICE_MAP: Record<string, string> = {
  auth: process.env.AUTH_SERVICE_URL || "http://localhost:8001",
  knowledge: process.env.KNOWLEDGE_SERVICE_URL || "http://localhost:8003",
  meetings: process.env.MEETING_SERVICE_URL || "http://localhost:8006",
  feedback: process.env.FEEDBACK_SERVICE_URL || "http://localhost:8007",
  checklists: process.env.CHECKLISTS_SERVICE_URL || "http://localhost:8002",
  escalations: process.env.ESCALATION_SERVICE_URL || "http://localhost:8005",
};

const ENDPOINTS: Array<{ source: AuditSource; path: string }> = [
  { source: "auth", path: "/auth/login-history" },
  { source: "auth", path: "/auth/role-change-history" },
  { source: "auth", path: "/auth/invitation-history" },
  { source: "auth", path: "/auth/mentor-assignment-history" },
  { source: "knowledge", path: "/knowledge/article-change-history" },
  { source: "knowledge", path: "/knowledge/article-view-history" },
  { source: "knowledge", path: "/knowledge/category-change-history" },
  { source: "knowledge", path: "/knowledge/dialogue-scenario-change-history" },
  { source: "meetings", path: "/meetings/meeting-status-change-history" },
  { source: "meetings", path: "/meetings/meeting-participant-history" },
  { source: "feedback", path: "/feedback/feedback-status-change-history" },
  { source: "checklists", path: "/checklists/checklist-status-history" },
  { source: "checklists", path: "/checklists/task-completion-history" },
  { source: "checklists", path: "/checklists/template-change-history" },
  { source: "escalations", path: "/escalations/escalation-status-change-history" },
  { source: "escalations", path: "/escalations/mentor-intervention-history" },
];

// Create a map from source to endpoint paths (without the /source/ prefix)
const ENDPOINT_MAP: Record<AuditSource, string[]> = {
  auth: ENDPOINTS.filter(e => e.source === "auth").map(e => e.path.replace("/auth/", "")),
  knowledge: ENDPOINTS.filter(e => e.source === "knowledge").map(e => e.path.replace("/knowledge/", "")),
  meetings: ENDPOINTS.filter(e => e.source === "meetings").map(e => e.path.replace("/meetings/", "")),
  feedback: ENDPOINTS.filter(e => e.source === "feedback").map(e => e.path.replace("/feedback/", "")),
  checklists: ENDPOINTS.filter(e => e.source === "checklists").map(e => e.path.replace("/checklists/", "")),
  escalations: ENDPOINTS.filter(e => e.source === "escalations").map(e => e.path.replace("/escalations/", "")),
};

const MAX_UPSTREAM_ROWS_PER_SOURCE = 1000;
const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "transfer-encoding",
  "host",
  "content-length",
  "te",
  "trailer",
  "upgrade",
]);

interface FetchFromSourceResult {
  source: AuditSource;
  events: NormalizedAuditEvent[];
  error?: { status: number; message: string };
}

async function fetchFromSource(
  source: AuditSource,
  baseUrl: string,
  headers: Headers,
  fromDate?: string,
  toDate?: string,
): Promise<FetchFromSourceResult> {
  const endpoints = ENDPOINT_MAP[source];
  const allEvents: NormalizedAuditEvent[] = [];

  for (const endpoint of endpoints) {
    const url = new URL(`/api/v1/${source}/audit/${endpoint}`, baseUrl);
    if (fromDate) url.searchParams.set("from_date", fromDate);
    if (toDate) url.searchParams.set("to_date", toDate);
    url.searchParams.set("limit", "100");

    let offset = 0;
    let totalFetched = 0;
    let hasMore = true;

    while (hasMore && totalFetched < MAX_UPSTREAM_ROWS_PER_SOURCE) {
      url.searchParams.set("offset", String(offset));

      try {
        const response = await fetch(url.toString(), {
          method: "GET",
          headers,
          credentials: "include",
        });

        if (!response.ok) {
          logger.error(`Failed to fetch ${source}/${endpoint}`, {
            status: response.status,
            source,
            endpoint,
          });
          return {
            source,
            events: allEvents,
            error: { status: response.status, message: `Failed to fetch ${source}/${endpoint}` },
          };
        }

        const data = await response.json();
        const items = data.items || [];

        if (items.length === 0) {
          hasMore = false;
          break;
        }

        const normalizeFn = NORMALIZE_MAP[endpoint];
        if (!normalizeFn) {
          logger.warn(`No normalize function for ${endpoint}`);
          continue;
        }

        for (const item of items) {
          try {
            allEvents.push(normalizeFn(item));
            totalFetched++;
          } catch (err) {
            logger.error(`Failed to normalize ${endpoint} item`, { error: err, item });
          }
        }

        const total = data.total || 0;
        if (offset + items.length >= total) {
          hasMore = false;
        } else {
          offset += items.length;
        }

        if (totalFetched >= MAX_UPSTREAM_ROWS_PER_SOURCE) {
          logger.warn(`Hit MAX_UPSTREAM_ROWS_PER_SOURCE cap for ${source}`, {
            source,
            totalFetched,
          });
          hasMore = false;
        }
      } catch (err) {
        logger.error(`Network error fetching ${source}/${endpoint}`, { error: err });
        return {
          source,
          events: allEvents,
          error: { status: 502, message: `Network error fetching ${source}/${endpoint}` },
        };
      }
    }
  }

  return { source, events: allEvents };
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const fromDate = searchParams.get("from_date") || undefined;
  const toDate = searchParams.get("to_date") || undefined;
  const sourcesParam = searchParams.get("sources");
  const eventTypesParam = searchParams.get("event_types");
  const actorIdParam = searchParams.get("actor_id");
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = Math.min(parseInt(searchParams.get("page_size") || "50", 10), 100);

  const sources: AuditSource[] = sourcesParam
    ? (sourcesParam.split(",") as AuditSource[])
    : Object.keys(SERVICE_MAP) as AuditSource[];
  const eventTypes = eventTypesParam ? eventTypesParam.split(",") : undefined;
  const actorId = actorIdParam ? parseInt(actorIdParam, 10) : undefined;

  // Build headers for forwarding - match the existing proxy pattern
  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  // Forward cookies and extract access_token for Authorization header
  const cookieHeader = request.headers.get("cookie");
  let accessToken: string | undefined;
  if (cookieHeader) {
    headers.set("Cookie", cookieHeader);
    const cookieStore = await cookies();
    accessToken = cookieStore.get("access_token")?.value;
  }

  // Inject Authorization header for services that require Bearer tokens
  const hasAuthHeader = headers.has("authorization") || headers.has("Authorization");
  if (!hasAuthHeader && accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  // Fan out to all sources in parallel
  const fetchPromises = sources.map((source) =>
    fetchFromSource(source, SERVICE_MAP[source], headers, fromDate, toDate)
  );

  const results = await Promise.allSettled(fetchPromises);

  const allEvents: NormalizedAuditEvent[] = [];
  const partial: { source: string; status: number; message: string }[] = [];

  for (const result of results) {
    if (result.status === "fulfilled") {
      const { source, events, error } = result.value;
      allEvents.push(...events);
      if (error) {
        partial.push(error);
      }
    } else {
      logger.error("Source fetch promise rejected", { error: result.reason });
      partial.push({ source: "unknown", status: 500, message: "Promise rejected" });
    }
  }

  // Sort by timestamp desc (stable tiebreak: source, id)
  allEvents.sort((a, b) => {
    const tsCompare = b.timestamp.localeCompare(a.timestamp);
    if (tsCompare !== 0) return tsCompare;
    const sourceCompare = a.source.localeCompare(b.source);
    if (sourceCompare !== 0) return sourceCompare;
    return a.id.localeCompare(b.id);
  });

  // Apply client-side filters
  let filteredEvents = allEvents;
  if (eventTypes && eventTypes.length > 0) {
    filteredEvents = filteredEvents.filter((e) => eventTypes.includes(e.event_type));
  }
  if (actorId !== undefined) {
    filteredEvents = filteredEvents.filter((e) => e.actor_id === actorId);
  }

  const total = filteredEvents.length;
  const offset = (page - 1) * pageSize;
  const paginatedEvents = filteredEvents.slice(offset, offset + pageSize);

  const response: {
    items: NormalizedAuditEvent[];
    total: number;
    page: number;
    page_size: number;
    partial?: { source: string; status: number; message: string }[];
  } = {
    items: paginatedEvents,
    total,
    page,
    page_size: pageSize,
  };

  if (partial.length > 0) {
    response.partial = partial;
  }

  return NextResponse.json(response);
}
