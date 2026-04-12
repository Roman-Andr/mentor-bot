import { TOKEN_KEY, USER_KEY } from "@/lib/storage-keys";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token: string | null) {
  if (typeof window === "undefined") return;
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

function handleUnauthorized() {
  const hadToken = !!getAuthToken();
  if (!hadToken) return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

export type ApiError = {
  message: string;
  status?: number;
  code?: string;
};

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };

async function handleResponse<T>(response: Response): Promise<ApiResult<T>> {
  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized();
      return {
        success: false,
        error: { message: "Unauthorized", status: 401 },
      };
    }
    const errorData = await response.json().catch(() => ({}));
    return {
      success: false,
      error: {
        message: errorData.detail || `HTTP ${response.status}`,
        status: response.status,
      },
    };
  }

  if (response.status === 204) {
    return { success: true, data: undefined as T };
  }

  const data = await response.json();
  return { success: true, data };
}

export async function fetchApi<T>(
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

    const response = await fetch(endpoint, { ...options, headers });
    const result = await handleResponse<T>(response);

    if (result.success) {
      return { data: result.data };
    }
    return { error: result.error.message };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Network error" };
  }
}

export async function fetchUpload<T>(
  endpoint: string,
  formData: FormData,
  method: string = "POST",
): Promise<ApiResponse<T>> {
  try {
    const token = getAuthToken();
    const headers: Record<string, string> = {};

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, { method, headers, body: formData });
    const result = await handleResponse<T>(response);

    if (result.success) {
      return { data: result.data };
    }
    return { error: result.error.message };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Network error" };
  }
}

export async function fetchApiNew<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<ApiResult<T>> {
  try {
    const token = getAuthToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, { ...options, headers });
    return handleResponse<T>(response);
  } catch (error) {
    return {
      success: false,
      error: {
        message: error instanceof Error ? error.message : "Network error",
      },
    };
  }
}
