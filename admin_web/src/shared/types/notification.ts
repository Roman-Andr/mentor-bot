export interface Notification {
  id: number;
  user_id: number;
  recipient_telegram_id: number | null;
  recipient_email: string | null;
  type: string;
  channel: string;
  subject: string | null;
  body: string;
  status: string;
  error_message: string | null;
  created_at: string;
  scheduled_for: string | null;
  sent_at: string | null;
}

export interface NotificationTemplate {
  id: number;
  name: string;
  channel: string;
  language: string;
  subject: string | null;
  body_html: string | null;
  body_text: string | null;
  variables: string[];
  version: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface NotificationTemplateCreate {
  name: string;
  channel: string;
  language: string;
  subject: string | null;
  body_html: string | null;
  body_text: string | null;
  variables: string[];
}

export interface NotificationTemplateUpdate {
  subject: string | null;
  body_html: string | null;
  body_text: string | null;
  variables: string[] | null;
  is_active: boolean | null;
}

export interface NotificationTemplateRenderRequest {
  template_name: string;
  channel: string;
  language: string;
  variables: Record<string, string>;
}

export interface NotificationTemplateRenderResponse {
  template_name: string;
  channel: string;
  language: string;
  subject: string | null;
  body: string;
  variables_used: string[];
}
