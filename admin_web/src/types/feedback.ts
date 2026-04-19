/** Feedback types for admin web. */

export interface PulseSurvey {
  id: number;
  user_id: number | null;
  is_anonymous: boolean;
  rating: number;
  submitted_at: string;
  department_id: number | null;
  position_level: string | null;
}

export interface ExperienceRating {
  id: number;
  user_id: number | null;
  is_anonymous: boolean;
  rating: number;
  submitted_at: string;
  department_id: number | null;
}

export interface Comment {
  id: number;
  user_id: number | null;
  is_anonymous: boolean;
  comment: string;
  submitted_at: string;
  department_id: number | null;
  allow_contact: boolean;
  contact_email: string | null;
  reply: string | null;
  replied_at: string | null;
  replied_by: number | null;
}

export interface FeedbackListResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface PulseStats {
  average_rating: number | null;
  total_responses: number;
  min_rating: number | null;
  max_rating: number | null;
  rating_distribution: Record<number, number>;
}

export interface ExperienceStats {
  average_rating: number | null;
  total_ratings: number;
  min_rating: number | null;
  max_rating: number | null;
  rating_distribution: Record<number, number>;
}

export interface AnonymityStats {
  anonymous: {
    average_rating?: number | null;
    count: number;
    with_contact?: number;
  };
  attributed: {
    average_rating?: number | null;
    count: number;
  };
}

export type FeedbackType = "pulse" | "experience" | "comment";

export interface FeedbackItem {
  id: number;
  type: FeedbackType;
  user_id: number | null;
  is_anonymous: boolean;
  rating?: number;
  comment?: string;
  submitted_at: string;
  department_id: number | null;
  allow_contact?: boolean;
  contact_email?: string | null;
  reply?: string | null;
  replied_at?: string | null;
  replied_by?: number | null;
}
