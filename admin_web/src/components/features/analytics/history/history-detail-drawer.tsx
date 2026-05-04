"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { UserName } from "./user-name";
import type { NormalizedAuditEvent } from "@/types/audit";
import { formatDistanceToNow } from "date-fns";

interface HistoryDetailDrawerProps {
  event: NormalizedAuditEvent | null;
  open: boolean;
  onClose: () => void;
}

export function HistoryDetailDrawer({ event, open, onClose }: HistoryDetailDrawerProps) {
  const t = useTranslations();

  if (!event) return null;

  const timestamp = new Date(event.timestamp);
  const relativeTime = formatDistanceToNow(timestamp, { addSuffix: true });

  // Find old/new diff keys in raw
  const oldKeys = Object.keys(event.raw).filter(k => k.startsWith("old_"));
  const newKeys = Object.keys(event.raw).filter(k => k.startsWith("new_"));

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Badge variant="secondary">{event.source}</Badge>
            <Badge>{event.event_type}</Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">{t("analytics.history.columns.timestamp")}</p>
              <p className="font-medium">{timestamp.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">{relativeTime}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("analytics.history.summary")}</p>
              <p className="font-medium">{event.summary}</p>
            </div>
          </div>

          {event.actor_id !== null && (
            <div>
              <p className="text-sm text-muted-foreground">{t("analytics.history.columns.actor")}</p>
              <p className="font-medium"><UserName userId={event.actor_id} /></p>
            </div>
          )}

          {event.subject_user_id !== null && (
            <div>
              <p className="text-sm text-muted-foreground">{t("analytics.history.subject")}</p>
              <p className="font-medium"><UserName userId={event.subject_user_id} /></p>
            </div>
          )}

          {event.resource_type && event.resource_id && (
            <div>
              <p className="text-sm text-muted-foreground">{t("analytics.history.resource")}</p>
              <p className="font-medium">{event.resource_type} #{event.resource_id}</p>
            </div>
          )}

          {oldKeys.length > 0 && newKeys.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">{t("analytics.history.changes")}</p>
              <div className="border rounded-md p-3 space-y-2">
                {oldKeys.map(oldKey => {
                  const newKey = oldKey.replace("old_", "new_");
                  const label = oldKey.replace("old_", "").replace("_", " ");
                  return (
                    <div key={oldKey} className="grid grid-cols-2 gap-2 text-sm">
                      <div className="text-muted-foreground">
                        <span className="font-medium">{label}:</span> {String(event.raw[oldKey] || "—")}
                      </div>
                      <div className="text-green-600">
                        <span className="font-medium">{label}:</span> {String(event.raw[newKey] || "—")}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div>
            <p className="text-sm text-muted-foreground mb-2">{t("analytics.history.metadata")}</p>
            <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto">
              {JSON.stringify(event.raw, null, 2)}
            </pre>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
