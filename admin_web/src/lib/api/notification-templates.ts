import { fetchApi } from "./client";
import type {
  NotificationTemplate,
  NotificationTemplateCreate,
  NotificationTemplateUpdate,
  NotificationTemplateRenderRequest,
  NotificationTemplateRenderResponse,
} from "@/types/notification";

export const notificationTemplatesApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    name?: string;
    channel?: string;
    language?: string;
    is_active?: boolean;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.name) searchParams.set("name", params.name);
    if (params?.channel) searchParams.set("channel", params.channel);
    if (params?.language) searchParams.set("language", params.language);
    if (params?.is_active !== undefined) searchParams.set("is_active", String(params.is_active));
    return fetchApi<{ templates: NotificationTemplate[]; total: number; page: number; size: number; pages: number }>(
      `/api/v1/notification-templates/list?${searchParams.toString()}`
    );
  },

  get: (id: number) => {
    return fetchApi<NotificationTemplate>(`/api/v1/notification-templates/${id}`);
  },

  getByName: (name: string, channel: string, language: string) => {
    return fetchApi<NotificationTemplate>(
      `/api/v1/notification-templates/by-name/${name}?channel=${channel}&language=${language}`
    );
  },

  create: (data: NotificationTemplateCreate) => {
    return fetchApi<NotificationTemplate>("/api/v1/notification-templates/create", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update: (id: number, data: NotificationTemplateUpdate) => {
    return fetchApi<NotificationTemplate>(`/api/v1/notification-templates/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  delete: (id: number) => {
    return fetchApi<{ message: string }>(`/api/v1/notification-templates/${id}`, {
      method: "DELETE",
    });
  },

  render: (data: NotificationTemplateRenderRequest) => {
    return fetchApi<NotificationTemplateRenderResponse>("/api/v1/notification-templates/render", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  preview: (data: { body_text?: string | null; body_html?: string | null; subject?: string | null; variables: Record<string, string> }) => {
    return fetchApi<NotificationTemplateRenderResponse>(
      "/api/v1/notification-templates/preview",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  },
};
