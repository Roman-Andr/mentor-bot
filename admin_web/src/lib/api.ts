const AUTH_SERVICE_URL =
  process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || "http://localhost:8001";
const CHECKLISTS_SERVICE_URL =
  process.env.NEXT_PUBLIC_CHECKLISTS_SERVICE_URL || "http://localhost:8002";
const KNOWLEDGE_SERVICE_URL =
  process.env.NEXT_PUBLIC_KNOWLEDGE_SERVICE_URL || "http://localhost:8003";

const TOKEN_KEY = "admin_token";

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token: string | null) {
  if (typeof window !== "undefined") {
    try {
      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }
    } catch {
      // ignore storage errors
    }
  }
}

function getAuthToken(): string | null {
  return getStoredToken();
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function fetchApi<T>(
  baseUrl: string,
  endpoint: string,
  options?: RequestInit,
): Promise<ApiResponse<T>> {
  try {
    const token = getAuthToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { error: errorData.detail || `HTTP ${response.status}` };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Network error" };
  }
}

export interface User {
  id: number;
  telegram_id: number | null;
  username: string | null;
  first_name: string;
  last_name: string | null;
  email: string;
  phone: string | null;
  employee_id: string;
  department: string | null;
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
  department: string | null;
  position: string | null;
  level: string | null;
  role: string;
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
  department: string | null;
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

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  category_id: number | null;
  category_name?: string;
  author_name: string;
  department: string | null;
  position: string | null;
  level: string | null;
  status: string;
  is_pinned: boolean;
  is_featured: boolean;
  view_count: number;
  keywords: string[];
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

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
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

export const api = {
  users: {
    list: (params?: {
      role?: string;
      department?: string;
      search?: string;
      skip?: number;
      limit?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.role) searchParams.set("role", params.role);
      if (params?.department) searchParams.set("department", params.department);
      if (params?.search) searchParams.set("search", params.search);
      if (params?.skip) searchParams.set("skip", String(params.skip));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<UserListResponse>(
        AUTH_SERVICE_URL,
        `/api/v1/users?${searchParams.toString()}`,
      );
    },
    get: (id: number) =>
      fetchApi<User>(AUTH_SERVICE_URL, `/api/v1/users/${id}`),
    create: (data: Partial<User> & { password?: string }) =>
      fetchApi<User>(AUTH_SERVICE_URL, "/api/v1/users", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<User>) =>
      fetchApi<User>(AUTH_SERVICE_URL, `/api/v1/users/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi<{ message: string }>(AUTH_SERVICE_URL, `/api/v1/users/${id}`, {
        method: "DELETE",
      }),
  },

  invitations: {
    list: (params?: {
      status?: string;
      email?: string;
      skip?: number;
      limit?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.status) searchParams.set("status", params.status);
      if (params?.email) searchParams.set("email", params.email);
      if (params?.skip) searchParams.set("skip", String(params.skip));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<InvitationListResponse>(
        AUTH_SERVICE_URL,
        `/api/v1/invitations?${searchParams.toString()}`,
      );
    },
    create: (data: {
      email: string;
      role: string;
      employee_id?: string;
      department?: string;
      expires_in_days?: number;
    }) =>
      fetchApi<Invitation>(AUTH_SERVICE_URL, "/api/v1/invitations", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    resend: (id: number) =>
      fetchApi<Invitation>(
        AUTH_SERVICE_URL,
        `/api/v1/invitations/${id}/resend`,
        { method: "POST" },
      ),
    revoke: (id: number) =>
      fetchApi<Invitation>(
        AUTH_SERVICE_URL,
        `/api/v1/invitations/${id}/revoke`,
        { method: "POST" },
      ),
    delete: (id: number) =>
      fetchApi<{ message: string }>(
        AUTH_SERVICE_URL,
        `/api/v1/invitations/${id}`,
        { method: "DELETE" },
      ),
  },

  templates: {
    list: (params?: {
      department?: string;
      status?: string;
      skip?: number;
      limit?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.department) searchParams.set("department", params.department);
      if (params?.status) searchParams.set("status", params.status);
      if (params?.skip) searchParams.set("skip", String(params.skip));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<Template[]>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates?${searchParams.toString()}`,
      );
    },
    get: (id: number) =>
      fetchApi<TemplateWithTasks>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates/${id}`,
      ),
    create: (data: Partial<Template>) =>
      fetchApi<Template>(CHECKLISTS_SERVICE_URL, "/api/v1/templates", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<Template>) =>
      fetchApi<Template>(CHECKLISTS_SERVICE_URL, `/api/v1/templates/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi<{ message: string }>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates/${id}`,
        { method: "DELETE" },
      ),
    publish: (id: number) =>
      fetchApi<Template>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates/${id}/publish`,
        { method: "POST" },
      ),
    clone: (id: number) =>
      fetchApi<Template>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates/${id}/clone`,
        { method: "POST" },
      ),
    addTask: (templateId: number, data: Partial<TaskTemplate>) =>
      fetchApi<TaskTemplate>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/templates/${templateId}/tasks`,
        { method: "POST", body: JSON.stringify(data) },
      ),
  },

  articles: {
    list: (params?: {
      status?: string;
      category_id?: number;
      search?: string;
      skip?: number;
      limit?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.status) searchParams.set("status", params.status);
      if (params?.category_id)
        searchParams.set("category_id", String(params.category_id));
      if (params?.search) searchParams.set("search", params.search);
      if (params?.skip) searchParams.set("skip", String(params.skip));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      return fetchApi<ArticleListResponse>(
        KNOWLEDGE_SERVICE_URL,
        `/api/v1/articles?${searchParams.toString()}`,
      );
    },
    get: (id: number) =>
      fetchApi<Article>(KNOWLEDGE_SERVICE_URL, `/api/v1/articles/${id}`),
    create: (data: Partial<Article>) =>
      fetchApi<Article>(KNOWLEDGE_SERVICE_URL, "/api/v1/articles", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<Article>) =>
      fetchApi<Article>(KNOWLEDGE_SERVICE_URL, `/api/v1/articles/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi<{ message: string }>(
        KNOWLEDGE_SERVICE_URL,
        `/api/v1/articles/${id}`,
        { method: "DELETE" },
      ),
    publish: (id: number) =>
      fetchApi<Article>(
        KNOWLEDGE_SERVICE_URL,
        `/api/v1/articles/${id}/publish`,
        { method: "POST" },
      ),
  },

  categories: {
    list: () =>
      fetchApi<CategoryListResponse>(KNOWLEDGE_SERVICE_URL, "/api/v1/categories"),
  },

  analytics: {
    dashboard: () =>
      fetchApi<DashboardStats>(
        CHECKLISTS_SERVICE_URL,
        "/api/v1/checklists/stats/summary",
      ),
    onboardingProgress: () =>
      fetchApi<OnboardingProgress[]>(
        CHECKLISTS_SERVICE_URL,
        "/api/v1/checklists?overdue_only=false",
      ),
    checklistStats: (params?: { department?: string }) => {
      const searchParams = new URLSearchParams();
      if (params?.department) searchParams.set("department", params.department);
      return fetchApi<ChecklistStats>(
        CHECKLISTS_SERVICE_URL,
        `/api/v1/checklists/stats/summary?${searchParams.toString()}`,
      );
    },
  },
};
