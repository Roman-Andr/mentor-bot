export interface User {
  id: number;
  telegram_id: number | null;
  username: string | null;
  first_name: string;
  last_name: string | null;
  email: string;
  phone: string | null;
  employee_id: string;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  hire_date: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface UserListResponse {
  total: number;
  users: User[];
  page: number;
  size: number;
  pages: number;
}

export interface Invitation {
  id: number;
  token: string;
  user_id: number | null;
  email: string;
  employee_id: string;
  first_name: string | null;
  last_name: string | null;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  role: string;
  mentor_id: number | null;
  status: string;
  expires_at: string;
  created_at: string;
  invitation_url: string;
  is_expired: boolean;
}

export interface InvitationListResponse {
  total: number;
  invitations: Invitation[];
  page: number;
  size: number;
  pages: number;
  stats: {
    total: number;
    pending: number;
    used: number;
    revoked: number;
    expired: number;
    conversion_rate: number;
  };
}

export interface Template {
  id: number;
  name: string;
  description: string | null;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  duration_days: number;
  status: string;
  is_default: boolean;
  created_at: string;
  task_categories: string[];
}

export interface TaskTemplate {
  id: number;
  template_id: number;
  title: string;
  description: string | null;
  instructions: string | null;
  category: string;
  order: number;
  due_days: number;
  estimated_minutes: number | null;
}

export interface TemplateWithTasks extends Template {
  tasks: TaskTemplate[];
}

export interface ChecklistStats {
  total: number;
  completed: number;
  in_progress: number;
  overdue: number;
  not_started: number;
  avg_completion_days: number;
  completion_rate: number;
  by_department: Record<string, number>;
}

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  category_id: number | null;
  category: Category | null;
  author_name: string;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  status: string;
  is_pinned: boolean;
  is_featured: boolean;
  view_count: number;
  keywords: string[];
  attachments?: Attachment[];
  created_at: string;
  updated_at: string | null;
}

export interface ArticleListResponse {
  total: number;
  articles: Article[];
  page: number;
  size: number;
  pages: number;
}

export interface Attachment {
  id: number;
  article_id: number;
  name: string;
  type: string;
  url: string;
  file_size: number | null;
  mime_type: string | null;
  description: string | null;
  order: number;
  is_downloadable: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface AttachmentListResponse {
  total: number;
  attachments: Attachment[];
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  parent_id: number | null;
  parent_name?: string | null;
  order: number;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  icon: string | null;
  color: string | null;
  children_count: number;
  articles_count: number;
  created_at: string;
  updated_at: string | null;
  article_count: number;
}

export interface CategoryListResponse {
  total: number;
  categories: Category[];
  page: number;
  size: number;
  pages: number;
}

export interface DashboardStats {
  total_users: number;
  active_newbies: number;
  completed_onboarding: number;
  pending_tasks: number;
  overdue_tasks: number;
  average_completion_days: number;
}

export interface OnboardingProgress {
  user_id: number;
  user_name: string;
  department: string;
  start_date: string;
  completion_percentage: number;
  days_remaining: number;
  status: string;
}

export interface EscalationRequest {
  id: number;
  user_id: number;
  type: string;
  source: string;
  status: string;
  reason: string | null;
  context: Record<string, unknown>;
  assigned_to: number | null;
  related_entity_type: string | null;
  related_entity_id: number | null;
  created_at: string;
  updated_at: string | null;
  resolved_at: string | null;
}

export interface EscalationListResponse {
  total: number;
  requests: EscalationRequest[];
  page: number;
  size: number;
  pages: number;
}

export interface Notification {
  id: number;
  user_id: number;
  recipient_telegram_id: number | null;
  recipient_email: string | null;
  type: string;
  channel: string;
  subject: string | null;
  body: string;
  status: string;
  error_message: string | null;
  created_at: string;
  scheduled_for: string | null;
  sent_at: string | null;
}

export interface Meeting {
  id: number;
  title: string;
  description: string | null;
  type: string;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  deadline_days: number;
  is_mandatory: boolean;
  order: number;
  created_at: string;
  updated_at: string | null;
}

export interface MeetingListResponse {
  total: number;
  meetings: Meeting[];
  page: number;
  size: number;
  pages: number;
}

export interface UserMeeting {
  id: number;
  user_id: number;
  meeting_id: number;
  status: string;
  scheduled_at: string | null;
  completed_at: string | null;
  feedback: string | null;
  rating: number | null;
  created_at: string;
}

export interface UserMeetingListResponse {
  total: number;
  items: UserMeeting[];
  page: number;
  size: number;
  pages: number;
}

export interface PulseSurvey {
  id: number;
  user_id: number;
  rating: number;
  submitted_at: string;
}

export interface ExperienceRating {
  id: number;
  user_id: number;
  rating: number;
  submitted_at: string;
}

export interface Comment {
  id: number;
  user_id: number;
  comment: string;
  submitted_at: string;
}

export interface Checklist {
  id: number;
  user_id: number;
  employee_id: string;
  template_id: number;
  status: string;
  progress_percentage: number;
  completed_tasks: number;
  total_tasks: number;
  start_date: string;
  due_date: string | null;
  completed_at: string | null;
  mentor_id: number | null;
  hr_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  is_overdue: boolean;
  days_remaining: number | null;
}

export interface ChecklistListResponse {
  total: number;
  checklists: Checklist[];
  page: number;
  size: number;
  pages: number;
  stats: ChecklistStats;
}

export interface Department {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface DepartmentListResponse {
  total: number;
  departments: Department[];
  page: number;
  size: number;
  pages: number;
}

export interface UserMentor {
  id: number;
  user_id: number;
  mentor_id: number;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface UserMentorListResponse {
  total: number;
  relations: UserMentor[];
}

export type DialogueCategory = "VACATION" | "ACCESS" | "BENEFITS" | "CONTACTS" | "WORKTIME";

export type DialogueAnswerType = "TEXT" | "CHOICE" | "LINK";

export interface DialogueStep {
  id: number;
  scenario_id: number;
  step_number: number;
  question: string;
  answer_type: DialogueAnswerType;
  options: { label: string; next_step: number }[] | null;
  answer_content: string | null;
  next_step_id: number | null;
  parent_step_id: number | null;
  is_final: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface DialogueScenario {
  id: number;
  title: string;
  description: string | null;
  keywords: string[];
  category: DialogueCategory;
  is_active: boolean;
  display_order: number;
  steps: DialogueStep[];
  created_at: string;
  updated_at: string | null;
}

export interface DialogueScenarioListResponse {
  total: number;
  scenarios: DialogueScenario[];
  page: number;
  size: number;
  pages: number;
}
