export { fetchApi, fetchUpload, fetchApiNew } from "./client";
export type { ApiResponse, ApiResult, ApiError } from "./client";

export { usersApi } from "./users";
export { invitationsApi } from "./invitations";
export { departmentsApi } from "./departments";
export { templatesApi } from "./templates";
export { checklistsApi } from "./checklists";
export { articlesApi, categoriesApi, attachmentsApi } from "./articles";
export { analyticsApi } from "./analytics";
export { escalationsApi } from "./escalations";
export { notificationsApi } from "./notifications";
export { notificationTemplatesApi } from "./notification-templates";
export { meetingsApi } from "./meetings";
export { userMeetingsApi } from "./user-meetings";
export { feedbackApi } from "./feedback";
export { userMentorsApi } from "./user-mentors";
export { dialoguesApi } from "./dialogues";

import { usersApi } from "./users";
import { invitationsApi } from "./invitations";
import { departmentsApi } from "./departments";
import { templatesApi } from "./templates";
import { checklistsApi } from "./checklists";
import { articlesApi, categoriesApi, attachmentsApi } from "./articles";
import { analyticsApi } from "./analytics";
import { escalationsApi } from "./escalations";
import { notificationsApi } from "./notifications";
import { meetingsApi } from "./meetings";
import { userMeetingsApi } from "./user-meetings";
import { feedbackApi } from "./feedback";
import { userMentorsApi } from "./user-mentors";
import { dialoguesApi } from "./dialogues";

export const api = {
  users: usersApi,
  invitations: invitationsApi,
  departments: departmentsApi,
  templates: templatesApi,
  checklists: checklistsApi,
  articles: articlesApi,
  categories: categoriesApi,
  attachments: attachmentsApi,
  analytics: analyticsApi,
  escalations: escalationsApi,
  notifications: notificationsApi,
  meetings: meetingsApi,
  userMeetings: userMeetingsApi,
  feedback: feedbackApi,
  userMentors: userMentorsApi,
  dialogues: dialoguesApi,
};
