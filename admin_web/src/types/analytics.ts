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
