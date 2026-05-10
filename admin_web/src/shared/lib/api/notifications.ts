import { fetchApi } from "./client";
import type { Notification } from "@/shared/types";

export const notificationsApi = {
  history: (params?: { skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<Notification[]>(`/api/v1/notifications/history?${searchParams.toString()}`);
  },
  send: (data: {
    user_id: number;
    recipient_telegram_id?: number | null;
    recipient_email?: string | null;
    type: string;
    channel: string;
    body: string;
    subject?: string | null;
  }) =>
    fetchApi<Notification>("/api/v1/notifications/send", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  schedule: (data: {
    user_id: number;
    recipient_telegram_id?: number | null;
    recipient_email?: string | null;
    type: string;
    channel: string;
    body: string;
    subject?: string | null;
    scheduled_time: string;
  }) =>
    fetchApi<{ id: number; processed: boolean }>("/api/v1/notifications/schedule", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
