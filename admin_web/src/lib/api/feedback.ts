import { fetchApi } from "./client";
import type { PulseSurvey, ExperienceRating, Comment } from "./types";

export const feedbackApi = {
  submitPulse: (data: { user_id: number; rating: number }) =>
    fetchApi<PulseSurvey>("/api/v1/feedback/pulse", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  submitExperience: (data: { user_id: number; rating: number }) =>
    fetchApi<ExperienceRating>("/api/v1/feedback/experience", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  submitComment: (data: { user_id: number; comment: string }) =>
    fetchApi<Comment>("/api/v1/feedback/comments", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
