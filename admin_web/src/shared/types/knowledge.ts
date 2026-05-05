import type { Department } from "./department";

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

export interface FileUploadError {
  filename: string | null;
  error: string;
}

export interface BatchUploadResponse {
  total_uploaded: number;
  total_failed: number;
  attachments: Attachment[];
  errors: FileUploadError[];
}
