import type { Department } from "./department";

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
