export interface EscalationRequest {
  id: number;
  user_id: number;
  type: string;
  source: string;
  status: string;
  reason: string | null;
  context: Record<string, unknown>;
  assigned_to: number | null;
  related_entity_type: string | null;
  related_entity_id: number | null;
  created_at: string;
  updated_at: string | null;
  resolved_at: string | null;
}

export interface EscalationListResponse {
  total: number;
  requests: EscalationRequest[];
  page: number;
  size: number;
  pages: number;
}
