"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useToast } from "@/shared/hooks/use-toast";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Select } from "@/shared/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { notificationsApi } from "@/shared/lib/api/notifications";
import { Send, Clock } from "lucide-react";

const NOTIFICATION_TYPES = [
  { value: "SYSTEM", label: "System" },
  { value: "REMINDER", label: "Reminder" },
  { value: "INFO", label: "Info" },
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
    userId: "", type: "SYSTEM", channel: "TELEGRAM", subject: "", body: "", scheduledAt: "",
  });
  const [sending, setSending] = useState(false);

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
        });
        toast(t("settings.notificationScheduled") || "Notification scheduled", "success");
      } else {
        await notificationsApi.send({
          user_id: Number(form.userId),
          type: form.type,
          channel: form.channel,
          body: form.body,
          subject: form.subject || null,
        });
        toast(t("settings.notificationSent") || "Notification sent", "success");
      }
      setForm((f) => ({ ...f, userId: "", body: "", subject: "", scheduledAt: "" }));
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
              <Label>{t("settings.recipientUserId") || "Recipient User ID"}</Label>
              <Input
                type="number"
                value={form.userId}
                onChange={(ev) => setForm((f) => ({ ...f, userId: ev.target.value }))}
                placeholder="User ID"
                required
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
