"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useTranslations } from "@/hooks/use-translations";
import type { FeedbackItem } from "@/types";

interface FeedbackReplyDialogProps {
  item: FeedbackItem | null;
  open: boolean;
  submitting: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (reply: string) => Promise<void>;
}

export function FeedbackReplyDialog({
  item,
  open,
  submitting,
  onOpenChange,
  onSubmit,
}: FeedbackReplyDialogProps) {
  const t = useTranslations();
  const [reply, setReply] = useState("");
  const trimmedReply = reply.trim();

  useEffect(() => {
    if (open) {
      setReply(item?.reply ?? "");
    }
  }, [item?.reply, open]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!trimmedReply || submitting) return;
    await onSubmit(trimmedReply);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <DialogHeader>
            <DialogTitle>{t("feedback.replyTitle")}</DialogTitle>
            <DialogDescription>{t("feedback.replyDescription")}</DialogDescription>
          </DialogHeader>

          {item?.comment && (
            <div className="rounded-md border bg-muted/40 p-3 text-sm">
              <div className="mb-1 font-medium">{t("feedback.originalComment")}</div>
              <p className="whitespace-pre-wrap text-muted-foreground">{item.comment}</p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="feedback-reply">{t("feedback.replyText")}</Label>
            <Textarea
              id="feedback-reply"
              value={reply}
              onChange={(event) => setReply(event.target.value)}
              placeholder={t("feedback.replyPlaceholder")}
              rows={6}
              disabled={submitting}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
              {t("common.cancel")}
            </Button>
            <Button type="submit" disabled={!trimmedReply || submitting}>
              {submitting ? t("feedback.sendingReply") : t("feedback.sendReply")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
