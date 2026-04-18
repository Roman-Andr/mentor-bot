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

export const feedbackApi = {
  // Pulse surveys
  getPulseSurveys: (params?: {
    user_id?: number;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) =>
    fetchApi<FeedbackListResponse<PulseSurvey>>(
      `/api/v1/feedback/pulse?${new URLSearchParams(params as Record<string, string>).toString()}`
    ),

  submitPulse: (data: { rating: number; is_anonymous?: boolean }) =>
    fetchApi<PulseSurvey>("/api/v1/feedback/pulse", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getPulseStats: (params?: { user_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<PulseStats>(
      `/api/v1/feedback/pulse/stats?${new URLSearchParams(params as Record<string, string>).toString()}`
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
  }) =>
    fetchApi<FeedbackListResponse<ExperienceRating>>(
      `/api/v1/feedback/experience?${new URLSearchParams(params as Record<string, string>).toString()}`
    ),

  submitExperience: (data: { rating: number; is_anonymous?: boolean }) =>
    fetchApi<ExperienceRating>("/api/v1/feedback/experience", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getExperienceStats: (params?: { user_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<ExperienceStats>(
      `/api/v1/feedback/experience/stats?${new URLSearchParams(params as Record<string, string>).toString()}`
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
  }) =>
    fetchApi<FeedbackListResponse<Comment>>(
      `/api/v1/feedback/comments?${new URLSearchParams(params as Record<string, string>).toString()}`
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
      `/api/v1/feedback/pulse/anonymity-stats?${new URLSearchParams(params as Record<string, string>).toString()}`
    ),

  getExperienceAnonymityStats: (params?: { department_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<AnonymityStats>(
      `/api/v1/feedback/experience/anonymity-stats?${new URLSearchParams(params as Record<string, string>).toString()}`
    ),

  getCommentAnonymityStats: (params?: { department_id?: number; from_date?: string; to_date?: string }) =>
    fetchApi<AnonymityStats>(
      `/api/v1/feedback/comments/anonymity-stats?${new URLSearchParams(params as Record<string, string>).toString()}`
    ),
};
