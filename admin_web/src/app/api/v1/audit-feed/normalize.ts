import type { NormalizedAuditEvent, AuditSource, AuditEventType } from "@/types/audit";

// Helper to create composite ID
function makeId(source: AuditSource, eventType: AuditEventType, rawId: number | string): string {
  return `${source}:${eventType}:${rawId}`;
}

// Auth endpoints
export function normalizeLoginHistory(item: any): NormalizedAuditEvent {
  const id = item.id || item.login_id;
  return {
    id: makeId("auth", "login", id),
    source: "auth",
    event_type: "login",
    timestamp: item.login_at || item.timestamp,
    actor_id: item.user_id,
    subject_user_id: item.user_id,
    resource_type: null,
    resource_id: null,
    summary: item.success
      ? `Login succeeded (${item.method || "web"})`
      : `Login failed (${item.method || "web"}${item.failure_reason ? ": " + item.failure_reason : ""})`,
    raw: item,
  };
}

export function normalizeRoleChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("auth", "role_change", item.id),
    source: "auth",
    event_type: "role_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: null,
    resource_id: null,
    summary: `Role ${item.old_role || "none"} → ${item.new_role}`,
    raw: item,
  };
}

export function normalizeInvitationHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("auth", "invitation_status_change", item.id),
    source: "auth",
    event_type: "invitation_status_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: null,
    resource_type: "invitation",
    resource_id: item.invitation_id,
    summary: `Invitation ${item.old_status || "pending"} → ${item.new_status}`,
    raw: item,
  };
}

export function normalizeMentorAssignmentHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("auth", "mentor_assignment", item.id),
    source: "auth",
    event_type: "mentor_assignment",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: "mentor",
    resource_id: item.mentor_id,
    summary: `Mentor ${item.action}`,
    raw: item,
  };
}

// Knowledge endpoints
export function normalizeArticleChangeHistory(item: any): NormalizedAuditEvent {
  const action = item.action || "changed";
  const titleChange = item.old_title && item.new_title
    ? `${item.old_title} → ${item.new_title}`
    : item.new_title || item.old_title || "";
  return {
    id: makeId("knowledge", "article_change", item.id),
    source: "knowledge",
    event_type: "article_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by || item.user_id,
    subject_user_id: null,
    resource_type: "article",
    resource_id: item.article_id,
    summary: `${action} ${titleChange}`,
    raw: item,
  };
}

export function normalizeArticleViewHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("knowledge", "article_view", item.id || `${item.article_id}_${item.viewed_at}`),
    source: "knowledge",
    event_type: "article_view",
    timestamp: item.viewed_at,
    actor_id: item.user_id,
    subject_user_id: item.user_id,
    resource_type: "article",
    resource_id: item.article_id,
    summary: "Article viewed",
    raw: item,
  };
}

export function normalizeCategoryChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("knowledge", "category_change", item.id),
    source: "knowledge",
    event_type: "category_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: null,
    resource_type: "category",
    resource_id: item.category_id,
    summary: `${item.action || "changed"} category ${item.new_name || ""}`,
    raw: item,
  };
}

export function normalizeDialogueScenarioChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("knowledge", "dialogue_scenario_change", item.id),
    source: "knowledge",
    event_type: "dialogue_scenario_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: null,
    resource_type: "dialogue_scenario",
    resource_id: item.scenario_id,
    summary: `${item.action || "changed"} scenario ${item.new_name || ""}`,
    raw: item,
  };
}

// Meetings endpoints
export function normalizeMeetingStatusChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("meetings", "meeting_status_change", item.id),
    source: "meetings",
    event_type: "meeting_status_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: "meeting",
    resource_id: item.meeting_id,
    summary: `Status ${item.old_status || "unknown"} → ${item.new_status}`,
    raw: item,
  };
}

export function normalizeMeetingParticipantHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("meetings", "meeting_participant_change", item.id || `${item.meeting_id}_${item.user_id}_${item.joined_at}`),
    source: "meetings",
    event_type: "meeting_participant_change",
    timestamp: item.joined_at,
    actor_id: null,
    subject_user_id: item.user_id,
    resource_type: "meeting",
    resource_id: item.meeting_id,
    summary: `Participant ${item.action || "joined"}`,
    raw: item,
  };
}

// Feedback endpoints
export function normalizeFeedbackStatusChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("feedback", "feedback_status_change", item.id),
    source: "feedback",
    event_type: "feedback_status_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: "feedback",
    resource_id: item.feedback_id,
    summary: `Status ${item.old_status || "unknown"} → ${item.new_status}`,
    raw: item,
  };
}

// Checklists endpoints
export function normalizeChecklistStatusHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("checklists", "checklist_status_change", item.id),
    source: "checklists",
    event_type: "checklist_status_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: "checklist",
    resource_id: item.checklist_id,
    summary: `Status ${item.old_status || "unknown"} → ${item.new_status}`,
    raw: item,
  };
}

export function normalizeTaskCompletionHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("checklists", "task_completion", item.id || `${item.task_id}_${item.completed_at}`),
    source: "checklists",
    event_type: "task_completion",
    timestamp: item.completed_at,
    actor_id: item.completed_by,
    subject_user_id: item.user_id,
    resource_type: "task",
    resource_id: item.task_id,
    summary: "Task completed",
    raw: item,
  };
}

export function normalizeTemplateChangeHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("checklists", "template_change", item.id),
    source: "checklists",
    event_type: "template_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: null,
    resource_type: "template",
    resource_id: item.template_id,
    summary: `${item.action || "changed"} template ${item.new_name || ""}`,
    raw: item,
  };
}

// Escalations endpoints
export function normalizeEscalationStatusHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("escalations", "escalation_status_change", item.id),
    source: "escalations",
    event_type: "escalation_status_change",
    timestamp: item.changed_at,
    actor_id: item.changed_by,
    subject_user_id: item.user_id,
    resource_type: "escalation",
    resource_id: item.escalation_id,
    summary: `Status ${item.old_status || "unknown"} → ${item.new_status}`,
    raw: item,
  };
}

export function normalizeMentorInterventionHistory(item: any): NormalizedAuditEvent {
  return {
    id: makeId("escalations", "mentor_intervention", item.id),
    source: "escalations",
    event_type: "mentor_intervention",
    timestamp: item.intervention_at,
    actor_id: item.mentor_id,
    subject_user_id: null,
    resource_type: "escalation",
    resource_id: item.escalation_id,
    summary: `Intervention: ${item.intervention_type || "unknown"}`,
    raw: item,
  };
}

// Mapping table: endpoint path -> normalize function
export const NORMALIZE_MAP: Record<string, (item: any) => NormalizedAuditEvent> = {
  "login-history": normalizeLoginHistory,
  "role-change-history": normalizeRoleChangeHistory,
  "invitation-history": normalizeInvitationHistory,
  "mentor-assignment-history": normalizeMentorAssignmentHistory,
  "article-change-history": normalizeArticleChangeHistory,
  "article-view-history": normalizeArticleViewHistory,
  "category-change-history": normalizeCategoryChangeHistory,
  "dialogue-scenario-change-history": normalizeDialogueScenarioChangeHistory,
  "meeting-status-change-history": normalizeMeetingStatusChangeHistory,
  "meeting-participant-history": normalizeMeetingParticipantHistory,
  "feedback-status-change-history": normalizeFeedbackStatusChangeHistory,
  "checklist-status-history": normalizeChecklistStatusHistory,
  "task-completion-history": normalizeTaskCompletionHistory,
  "template-change-history": normalizeTemplateChangeHistory,
  "escalation-status-history": normalizeEscalationStatusHistory,
  "mentor-intervention-history": normalizeMentorInterventionHistory,
};
