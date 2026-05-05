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
