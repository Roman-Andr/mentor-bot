export type AuditSource =
  | "auth"
  | "knowledge"
  | "meetings"
  | "feedback"
  | "checklists"
  | "escalations";

export type AuditEventType =
  // auth
  | "login"
  | "logout"
  | "role_change"
  | "invitation_status_change"
  | "mentor_assignment"
  // knowledge
  | "article_change"
  | "article_view"
  | "category_change"
  | "dialogue_scenario_change"
  // meetings
  | "meeting_status_change"
  | "meeting_participant_change"
  // feedback
  | "feedback_status_change"
  // checklists
  | "checklist_status_change"
  | "task_completion"
  | "template_change"
  // escalations
  | "escalation_status_change"
  | "mentor_intervention";

export interface NormalizedAuditEvent {
  // Composite key — `${source}:${eventType}:${rawId}` (stable across re-fetches)
  id: string;
  source: AuditSource;
  event_type: AuditEventType;
  timestamp: string; // ISO 8601, always populated
  actor_id: number | null; // who performed the action (changed_by, etc.)
  subject_user_id: number | null; // user the action was about (user_id when applicable)
  resource_type: string | null; // "article" | "meeting" | "checklist" | ...
  resource_id: number | null;
  summary: string; // short human-readable line for the table
  // Full upstream payload preserved for the detail drawer
  raw: Record<string, unknown>;
}

export interface AuditFeedResponse {
  items: NormalizedAuditEvent[];
  total: number;
  page: number;
  page_size: number;
  // diagnostic — populated when one or more upstreams failed:
  partial?: { source: string; status: number; message: string }[];
}

export interface HistoryFilters {
  from_date?: string;
  to_date?: string;
  sources?: AuditSource[];
  event_types?: AuditEventType[];
  actor_id?: number;
}

export interface AuditFeedParams extends HistoryFilters {
  page: number;
  page_size: number;
}
