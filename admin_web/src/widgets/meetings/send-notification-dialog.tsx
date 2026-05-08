"use client";

import { useState, useCallback } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useToast } from "@/shared/hooks/use-toast";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Select } from "@/shared/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { AsyncSearchableSelect, type SelectOption } from "@/shared/ui/searchable-select";
import { notificationsApi } from "@/shared/lib/api/notifications";
import { api } from "@/shared/lib/api";
import { Send, Clock } from "lucide-react";

const NOTIFICATION_TYPES = [
  { value: "GENERAL", label: "General" },
  { value: "TASK_REMINDER", label: "Task Reminder" },
  { value: "MEETING_REMINDER", label: "Meeting Reminder" },
  { value: "ONBOARDING_EVENT", label: "Onboarding Event" },
  { value: "ESCALATION", label: "Escalation" },
];

const NOTIFICATION_CHANNELS = [
  { value: "TELEGRAM", label: "Telegram" },
  { value: "EMAIL", label: "Email" },
  { value: "BOTH", label: "Both" },
];

interface SendNotificationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SendNotificationDialog({ open, onOpenChange }: SendNotificationDialogProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const [form, setForm] = useState({
    userId: "", type: "GENERAL", channel: "TELEGRAM", subject: "", body: "", scheduledAt: "",
  });
  const [selectedUserLabel, setSelectedUserLabel] = useState("");
  const [selectedUserOption, setSelectedUserOption] = useState<SelectOption | undefined>(undefined);
  const [selectedUserTelegramId, setSelectedUserTelegramId] = useState<number | null>(null);
  const [selectedUserEmail, setSelectedUserEmail] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  // Search for users
  const searchUsers = useCallback(async (query: string): Promise<SelectOption[]> => {
    const resp = await api.users.list({ search: query, limit: 20 });
    if (!resp.success || !resp.data) return [];
    return resp.data.users.map((u) => ({
      value: String(u.id),
      label: `${u.first_name} ${u.last_name || ""}`.trim(),
      description: u.email,
      id: u.id,
      telegram_id: u.telegram_id,
      email: u.email,
    }));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.userId || !form.body) return;
    setSending(true);
    try {
      if (form.scheduledAt) {
        await notificationsApi.schedule({
          user_id: Number(form.userId),
          type: form.type,
          channel: form.channel,
          body: form.body,
          subject: form.subject || null,
          scheduled_time: new Date(form.scheduledAt).toISOString(),
          recipient_telegram_id: selectedUserTelegramId,
          recipient_email: selectedUserEmail,
        });
        toast(t("settings.notificationScheduled") || "Notification scheduled", "success");
      } else {
        await notificationsApi.send({
          user_id: Number(form.userId),
          type: form.type,
          channel: form.channel,
          body: form.body,
          subject: form.subject || null,
          recipient_telegram_id: selectedUserTelegramId,
          recipient_email: selectedUserEmail,
        });
        toast(t("settings.notificationSent") || "Notification sent", "success");
      }
      setForm((f) => ({ ...f, userId: "", body: "", subject: "", scheduledAt: "" }));
      setSelectedUserLabel("");
      setSelectedUserOption(undefined);
      setSelectedUserTelegramId(null);
      setSelectedUserEmail(null);
      onOpenChange(false);
    } catch {
      toast(t("common.error") || "Error", "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Send className="size-5" />
            {t("settings.sendNotification") || "Send Notification"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>{t("settings.recipientUserId") || "Recipient User"}</Label>
              <AsyncSearchableSelect
                value={form.userId}
                onChange={(v) => setForm((f) => ({ ...f, userId: v }))}
                onSearch={searchUsers}
                selectedLabel={selectedUserLabel}
                selectedOption={selectedUserOption}
                placeholder={t("settings.selectUser") || "Select user"}
                searchPlaceholder={t("settings.searchUser") || "Search user..."}
                minSearchLength={2}
                onOptionSelect={(opt) => {
                  setSelectedUserLabel(opt.label);
                  setSelectedUserOption(opt);
                  setSelectedUserTelegramId(opt.telegram_id || null);
                  setSelectedUserEmail(opt.email || null);
                }}
                autoFocus
              />
            </div>
            <div className="space-y-1.5">
              <Label>{t("settings.notificationType") || "Type"}</Label>
              <Select value={form.type} onChange={(v) => setForm((f) => ({ ...f, type: v }))} options={NOTIFICATION_TYPES} />
            </div>
            <div className="space-y-1.5">
              <Label>{t("settings.channel") || "Channel"}</Label>
              <Select value={form.channel} onChange={(v) => setForm((f) => ({ ...f, channel: v }))} options={NOTIFICATION_CHANNELS} />
            </div>
            <div className="space-y-1.5">
              <Label>{t("settings.subject") || "Subject (optional)"}</Label>
              <Input
                value={form.subject}
                onChange={(ev) => setForm((f) => ({ ...f, subject: ev.target.value }))}
                placeholder={t("common.optional") || "Optional"}
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>{t("settings.messageBody") || "Message"}</Label>
            <textarea
              value={form.body}
              onChange={(ev) => setForm((f) => ({ ...f, body: ev.target.value }))}
              placeholder={t("settings.messagePlaceholder") || "Enter notification message..."}
              required
              rows={3}
              className="border-input bg-background placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-1 focus-visible:outline-none"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="flex items-center gap-1.5">
              <Clock className="size-3.5" />
              {t("settings.scheduledAt") || "Schedule for (optional)"}
            </Label>
            <Input
              type="datetime-local"
              value={form.scheduledAt}
              onChange={(ev) => setForm((f) => ({ ...f, scheduledAt: ev.target.value }))}
            />
            <p className="text-muted-foreground text-xs">{t("settings.leaveBlankToSendNow") || "Leave blank to send immediately"}</p>
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={sending}>
              {t("common.cancel")}
            </Button>
            <Button type="submit" disabled={sending} className="gap-2">
              {form.scheduledAt ? <Clock className="size-4" /> : <Send className="size-4" />}
              {form.scheduledAt ? t("settings.scheduleNotification") || "Schedule" : t("settings.sendNow") || "Send Now"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
