import { USER_KEY } from "@/lib/storage-keys";

function handleUnauthorized() {
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
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    const response = await fetch(endpoint, {
      ...options,
      headers,
      credentials: "include",  // Send httpOnly cookies automatically
    });
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
    const response = await fetch(endpoint, {
      method,
      body: formData,
      credentials: "include",  // Send httpOnly cookies automatically
    });
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
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    const response = await fetch(endpoint, {
      ...options,
      headers,
      credentials: "include",  // Send httpOnly cookies automatically
    });
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
