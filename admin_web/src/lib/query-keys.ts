// Centralized query key factory for consistent cache management
// Following pattern: [entity, operation, params]

export const queryKeys = {
  // Departments
  departments: {
    all: ["departments"] as const,
    list: (params: unknown) => [...queryKeys.departments.all, "list", params] as const,
  },

  // Users
  users: {
    all: ["users"] as const,
    list: (params: unknown) => [...queryKeys.users.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.users.all, "detail", id] as const,
    mentors: (userId: number) => [...queryKeys.users.all, "mentors", userId] as const,
  },

  // Categories (Knowledge)
  categories: {
    all: ["categories"] as const,
    list: (params?: unknown) => [...queryKeys.categories.all, "list", params] as const,
    tree: () => [...queryKeys.categories.all, "tree"] as const,
  },

  // Articles (Knowledge)
  articles: {
    all: ["articles"] as const,
    list: (params: unknown) => [...queryKeys.articles.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.articles.all, "detail", id] as const,
  },

  // Attachments
  attachments: {
    all: ["attachments"] as const,
    byArticle: (articleId: number) => [...queryKeys.attachments.all, "article", articleId] as const,
  },

  // Templates
  templates: {
    all: ["templates"] as const,
    list: (params: unknown) => [...queryKeys.templates.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.templates.all, "detail", id] as const,
    tasks: (templateId: number) => [...queryKeys.templates.all, "tasks", templateId] as const,
  },

  // Checklists
  checklists: {
    all: ["checklists"] as const,
    list: (params: unknown) => [...queryKeys.checklists.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.checklists.all, "detail", id] as const,
  },

  // Dialogues
  dialogues: {
    all: ["dialogues"] as const,
    list: (params: unknown) => [...queryKeys.dialogues.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.dialogues.all, "detail", id] as const,
    steps: (dialogueId: number) => [...queryKeys.dialogues.all, "steps", dialogueId] as const,
  },

  // Meetings
  meetings: {
    all: ["meetings"] as const,
    list: (params: unknown) => [...queryKeys.meetings.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.meetings.all, "detail", id] as const,
  },

  // User Meetings (assignments)
  userMeetings: {
    all: ["user-meetings"] as const,
    byMeeting: (meetingId: number) => [...queryKeys.userMeetings.all, "by-meeting", meetingId] as const,
    byUser: (userId: number) => [...queryKeys.userMeetings.all, "by-user", userId] as const,
  },

  // User Mentors
  userMentors: {
    all: ["user-mentors"] as const,
    list: (params?: unknown) => [...queryKeys.userMentors.all, "list", params] as const,
    byUser: (userId: number) => [...queryKeys.userMentors.all, "by-user", userId] as const,
    byMentor: (mentorId: number) => [...queryKeys.userMentors.all, "by-mentor", mentorId] as const,
  },

  // Invitations
  invitations: {
    all: ["invitations"] as const,
    list: (params: unknown) => [...queryKeys.invitations.all, "list", params] as const,
  },

  // Escalations
  escalations: {
    all: ["escalations"] as const,
    list: (params: unknown) => [...queryKeys.escalations.all, "list", params] as const,
    detail: (id: number) => [...queryKeys.escalations.all, "detail", id] as const,
  },

  // Notifications
  notifications: {
    all: ["notifications"] as const,
    list: (params?: unknown) => [...queryKeys.notifications.all, "list", params] as const,
  },

  // Analytics
  analytics: {
    all: ["analytics"] as const,
    overview: () => [...queryKeys.analytics.all, "overview"] as const,
    department: (deptId: number) => [...queryKeys.analytics.all, "department", deptId] as const,
    checklist: (checklistId: number) => [...queryKeys.analytics.all, "checklist", checklistId] as const,
  },

  // Dashboard
  dashboard: {
    all: ["dashboard"] as const,
    stats: () => [...queryKeys.dashboard.all, "stats"] as const,
    activity: () => [...queryKeys.dashboard.all, "activity"] as const,
    departments: () => [...queryKeys.dashboard.all, "departments"] as const,
  },

  // Feedback
  feedback: {
    all: ["feedback"] as const,
    pulse: (params: unknown) => [...queryKeys.feedback.all, "pulse", params] as const,
    pulseStats: () => [...queryKeys.feedback.all, "pulse", "stats"] as const,
    pulseAnonymityStats: () => [...queryKeys.feedback.all, "pulse", "anonymity-stats"] as const,
    experience: (params: unknown) => [...queryKeys.feedback.all, "experience", params] as const,
    experienceStats: () => [...queryKeys.feedback.all, "experience", "stats"] as const,
    experienceAnonymityStats: () => [...queryKeys.feedback.all, "experience", "anonymity-stats"] as const,
    comments: (params: unknown) => [...queryKeys.feedback.all, "comments", params] as const,
    commentAnonymityStats: () => [...queryKeys.feedback.all, "comments", "anonymity-stats"] as const,
  },
} as const;

// Helper to invalidate all list queries for an entity
export function getEntityListKey(entity: keyof typeof queryKeys) {
  return queryKeys[entity]?.all ?? [entity];
}
