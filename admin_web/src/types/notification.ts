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
