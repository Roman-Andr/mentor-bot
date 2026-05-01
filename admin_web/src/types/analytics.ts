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

// Search Analytics types
export interface TopQueryStats {
  query: string;
  count: number;
  avg_results_count: number;
  zero_results_count: number;
}

export interface ZeroResultQuery {
  query: string;
  count: number;
  last_searched_at: string;
}

export interface DepartmentSearchStats {
  department_id: number | null;
  department_name: string;
  search_count: number;
  unique_users: number;
}

export interface SearchTimeseriesPoint {
  bucket: string;
  search_count: number;
  unique_users: number;
}

export interface SearchSummary {
  total_searches: number;
  unique_users: number;
  unique_queries: number;
  avg_results_per_search: number;
  zero_results_percentage: number;
}

export interface DateRange {
  from_date?: string;
  to_date?: string;
}
