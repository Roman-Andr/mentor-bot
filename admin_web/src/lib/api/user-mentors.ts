import { fetchApi } from "./client";
import type { UserMentor, UserMentorListResponse } from "./types";

export const userMentorsApi = {
  list: (params?: { user_id?: number; mentor_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.user_id !== undefined) searchParams.set("user_id", String(params.user_id));
    if (params?.mentor_id !== undefined) searchParams.set("mentor_id", String(params.mentor_id));
    return fetchApi<UserMentorListResponse>(`/api/v1/user-mentors?${searchParams.toString()}`);
  },
  create: (data: { user_id: number; mentor_id: number; notes?: string }) =>
    fetchApi<UserMentor>("/api/v1/user-mentors", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: { is_active?: boolean; notes?: string }) =>
    fetchApi<UserMentor>(`/api/v1/user-mentors/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`/api/v1/user-mentors/${id}`, {
      method: "DELETE",
    }),
};
