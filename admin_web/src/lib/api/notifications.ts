import { fetchApi } from "./client";
import type { Notification } from "@/types";

export const notificationsApi = {
  history: (params?: { skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchApi<Notification[]>(`/api/v1/notifications/history?${searchParams.toString()}`);
  },
  send: (data: {
    user_id: number;
    type: string;
    channel: string;
    body: string;
    subject?: string | null;
  }) =>
    fetchApi<Notification>("/api/v1/notifications/send", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
