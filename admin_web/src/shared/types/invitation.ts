import type { Department } from "./department";

export interface Invitation {
  id: number;
  token: string;
  user_id: number | null;
  email: string;
  employee_id: string;
  first_name: string | null;
  last_name: string | null;
  department_id: number | null;
  department: Department | null;
  position: string | null;
  level: string | null;
  role: string;
  mentor_id: number | null;
  status: string;
  expires_at: string;
  created_at: string;
  invitation_url: string;
  is_expired: boolean;
}

export interface InvitationListResponse {
  total: number;
  invitations: Invitation[];
  page: number;
  size: number;
  pages: number;
  stats: {
    total: number;
    pending: number;
    used: number;
    revoked: number;
    expired: number;
    conversion_rate: number;
  };
}
