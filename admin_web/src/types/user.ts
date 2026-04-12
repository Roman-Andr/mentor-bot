import type { Department } from "./department";

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
