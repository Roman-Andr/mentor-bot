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

export interface Task {
  id: number;
  checklist_id: number;
  template_task_id: number | null;
  title: string;
  description: string | null;
  category: string;
  order: number;
  assignee_id: number | null;
  assignee_role: string | null;
  due_date: string;
  depends_on: number[];
  status: string;
  started_at: string | null;
  completed_at: string | null;
  completed_by: number | null;
  completion_notes: string | null;
  attachments: any[];
  blocks: number[];
  created_at: string;
  updated_at: string | null;
  is_overdue: boolean;
  can_start: boolean;
  can_complete: boolean;
}

export interface ChecklistListResponse {
  total: number;
  checklists: Checklist[];
  page: number;
  size: number;
  pages: number;
  stats: ChecklistStats;
}
