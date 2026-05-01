export interface DepartmentDocument {
  id: number;
  department_id: number;
  title: string;
  description: string | null;
  category: string;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  is_public: boolean;
  uploaded_by: number;
  created_at: string;
  updated_at: string | null;
}

export interface DepartmentDocumentCreate {
  department_id: number;
  title: string;
  description?: string;
  category: string;
  is_public?: boolean;
  file: File;
}

export interface DepartmentDocumentUpdate {
  title?: string;
  description?: string;
  category?: string;
  is_public?: boolean;
}

export interface DepartmentDocumentListResponse {
  total: number;
  documents: DepartmentDocument[];
}
