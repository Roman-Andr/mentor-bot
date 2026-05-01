"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { StatusBadge } from "@/components/ui/status-badge";
import { useTranslations } from "@/hooks/use-translations";
import { formatDateTime } from "@/lib/utils";
import type { FeedbackItem } from "@/types";
import type { ReactNode } from "react";

interface FeedbackDetailsDialogProps {
  item: FeedbackItem | null;
  open: boolean;
  getUserName: (userId: number | null) => string;
  onOpenChange: (open: boolean) => void;
}

export function FeedbackDetailsDialog({ item, open, getUserName, onOpenChange }: FeedbackDetailsDialogProps) {
  const t = useTranslations();

  if (!item) {
    return null;
  }

  const canShowReplyStatus = item.type === "comment";
  const status = item.reply ? "replied" : item.is_anonymous && !item.allow_contact ? "no_reply" : "pending";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{t("feedback.detailsTitle")}</DialogTitle>
          <DialogDescription>
            {t("feedback.detailsDescription", { id: item.id, type: t(`statuses.${item.type}`) })}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Detail label="ID" value={String(item.id)} />
            <Detail label={t("feedback.type")} value={<StatusBadge status={item.type} />} />
            <Detail
              label={t("feedback.user")}
              value={item.is_anonymous ? t("feedback.anonymous") : getUserName(item.user_id)}
            />
            <Detail label={t("feedback.submittedAt")} value={formatDateTime(item.submitted_at)} />
            {canShowReplyStatus && <Detail label={t("feedback.status")} value={<StatusBadge status={status} />} />}
            {item.contact_email && <Detail label={t("feedback.contactEmail")} value={item.contact_email} />}
          </div>

          {item.rating !== undefined && (
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">{t("feedback.rating")}</div>
              <div className="mt-1 text-2xl font-semibold">{item.rating}</div>
            </div>
          )}

          {item.comment && (
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">{t("feedback.comment")}</div>
              <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{item.comment}</p>
            </div>
          )}

          {item.reply && (
            <div className="rounded-md border border-green-200 bg-green-50 p-3 dark:border-green-900/50 dark:bg-green-950/20">
              <div className="text-sm font-medium">{t("feedback.reply")}</div>
              <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{item.reply}</p>
              {item.replied_at && (
                <div className="mt-2 text-xs text-muted-foreground">
                  {t("feedback.repliedAt")}: {formatDateTime(item.replied_at)}
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Detail({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-md border p-3">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm">{value}</div>
    </div>
  );
}
