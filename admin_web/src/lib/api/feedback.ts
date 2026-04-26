import { fetchApi } from "./client";
import type {
  PulseSurvey,
  ExperienceRating,
  Comment,
  FeedbackListResponse,
  PulseStats,
  ExperienceStats,
  AnonymityStats,
} from "@/types";

// Helper to filter out undefined values from params
function buildQueryString(params?: Record<string, unknown>): string {
  if (!params) return "";
  const filtered = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null)
  );
  return new URLSearchParams(filtered as Record<string, string>).toString();
}

export const feedbackApi = {
  // Pulse surveys
  getPulseSurveys: (params?: {
    user_id?: number;
    from_date?: string;
    to_date?: string;
    search?: string;
    skip?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: "asc" | "desc";
  }) =>
    fetchApi<FeedbackListResponse<PulseSurvey>>(
      `/api/v1/feedback/pulse?${buildQueryString(params as Record<string, unknown>)}`
    ),

  submitPulse: (data: { rating: number; is_anonymous?: boolean }) =>
    fetchApi<PulseSurvey>("/api/v1/feedback/pulse", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getPulseStats: (params?: { user_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<PulseStats>(
      `/api/v1/feedback/pulse/stats?${buildQueryString(params as Record<string, unknown>)}`
    ),

  // Experience ratings
  getExperienceRatings: (params?: {
    user_id?: number;
    from_date?: string;
    to_date?: string;
    min_rating?: number;
    max_rating?: number;
    skip?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: "asc" | "desc";
  }) =>
    fetchApi<FeedbackListResponse<ExperienceRating>>(
      `/api/v1/feedback/experience?${buildQueryString(params as Record<string, unknown>)}`
    ),

  submitExperience: (data: { rating: number; is_anonymous?: boolean }) =>
    fetchApi<ExperienceRating>("/api/v1/feedback/experience", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getExperienceStats: (params?: { user_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<ExperienceStats>(
      `/api/v1/feedback/experience/stats?${buildQueryString(params as Record<string, unknown>)}`
    ),

  // Comments
  getComments: (params?: {
    user_id?: number;
    from_date?: string;
    to_date?: string;
    search?: string;
    has_reply?: boolean;
    skip?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: "asc" | "desc";
  }) =>
    fetchApi<FeedbackListResponse<Comment>>(
      `/api/v1/feedback/comments?${buildQueryString(params as Record<string, unknown>)}`
    ),

  submitComment: (data: {
    comment: string;
    is_anonymous?: boolean;
    allow_contact?: boolean;
    contact_email?: string;
  }) =>
    fetchApi<Comment>("/api/v1/feedback/comments", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  replyToComment: (commentId: number, reply: string) =>
    fetchApi<Comment>(`/api/v1/feedback/comments/${commentId}/reply`, {
      method: "POST",
      body: JSON.stringify({ reply }),
    }),

  // Anonymity stats (admin only)
  getPulseAnonymityStats: (params?: { department_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<AnonymityStats>(
      `/api/v1/feedback/pulse/anonymity-stats?${buildQueryString(params as Record<string, unknown>)}`
    ),

  getExperienceAnonymityStats: (params?: { department_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<AnonymityStats>(
      `/api/v1/feedback/experience/anonymity-stats?${buildQueryString(params as Record<string, unknown>)}`
    ),

  getCommentAnonymityStats: (params?: { department_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<AnonymityStats>(
      `/api/v1/feedback/comments/anonymity-stats?${buildQueryString(params as Record<string, unknown>)}`
    ),
};
