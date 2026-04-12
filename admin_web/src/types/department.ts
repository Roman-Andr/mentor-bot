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
