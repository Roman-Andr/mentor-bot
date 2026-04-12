import type { Department } from "./department";

export interface Meeting {
  id: number;
  title: string;
  description: string | null;
  type: string;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  deadline_days: number;
  is_mandatory: boolean;
  order: number;
  created_at: string;
  updated_at: string | null;
}

export interface MeetingListResponse {
  total: number;
  meetings: Meeting[];
  page: number;
  size: number;
  pages: number;
}

export interface UserMeeting {
  id: number;
  user_id: number;
  meeting_id: number;
  status: string;
  scheduled_at: string | null;
  completed_at: string | null;
  feedback: string | null;
  rating: number | null;
  created_at: string;
}

export interface UserMeetingListResponse {
  total: number;
  items: UserMeeting[];
  page: number;
  size: number;
  pages: number;
}
