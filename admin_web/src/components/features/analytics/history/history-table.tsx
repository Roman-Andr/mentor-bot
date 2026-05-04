"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { UserName } from "./user-name";
import type { NormalizedAuditEvent, AuditSource } from "@/types/audit";
import { formatDistanceToNow } from "date-fns";

interface HistoryTableProps {
  events: NormalizedAuditEvent[];
  onRowClick: (event: NormalizedAuditEvent) => void;
}

const SOURCE_COLORS: Record<AuditSource, string> = {
  auth: "bg-blue-500",
  knowledge: "bg-green-500",
  meetings: "bg-purple-500",
  feedback: "bg-orange-500",
  checklists: "bg-cyan-500",
  escalations: "bg-red-500",
};

export function HistoryTable({ events, onRowClick }: HistoryTableProps) {
  const t = useTranslations();

  if (events.length === 0) {
    return null;
  }

  return (
    <div className="border rounded-md">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-48">{t("analytics.history.columns.timestamp")}</TableHead>
            <TableHead className="w-32">{t("analytics.history.columns.source")}</TableHead>
            <TableHead className="w-48">{t("analytics.history.columns.event")}</TableHead>
            <TableHead className="w-48">{t("analytics.history.columns.actor")}</TableHead>
            <TableHead>{t("analytics.history.columns.summary")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.map((event) => (
            <TableRow
              key={event.id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onRowClick(event)}
            >
              <TableCell className="text-sm">
                <div>
                  <div className="font-medium">{new Date(event.timestamp).toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <Badge className={`${SOURCE_COLORS[event.source]} text-white`}>
                  {event.source}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant="outline">{event.event_type}</Badge>
              </TableCell>
              <TableCell>
                <UserName userId={event.actor_id} />
              </TableCell>
              <TableCell className="text-sm">{event.summary}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
