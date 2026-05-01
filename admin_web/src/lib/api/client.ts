let onUnauthorizedCallback: (() => void) | null = null;

export function setUnauthorizedCallback(callback: () => void) {
  onUnauthorizedCallback = callback;
}

function handleUnauthorized() {
  if (onUnauthorizedCallback) {
    onUnauthorizedCallback();
  }
}

export type ApiError = {
  message: string;
  status?: number;
  code?: string;
};

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
): Promise<ApiResult<T>> {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    const response = await fetch(endpoint, {
      ...options,
      headers,
      credentials: "include",
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

export async function fetchUpload<T>(
  endpoint: string,
  formData: FormData,
): Promise<ApiResult<T>> {
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
      credentials: "include",
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
