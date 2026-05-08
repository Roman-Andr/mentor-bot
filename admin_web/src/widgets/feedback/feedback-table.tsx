import { StatusBadge } from "@/shared/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { UserX, Star, TrendingUp, MessageSquare } from "lucide-react";
import { UserAvatar } from "@/shared/ui/user-avatar";
import { TableActions, buildViewAction, buildReplyAction } from "@/shared/components";
import { formatDateTime } from "@/shared/lib/utils";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import type { FeedbackItem } from "@/shared/types";
import { cn } from "@/shared/lib/utils";

const TYPE_BADGE: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  pulse: {
    label: "Pulse",
    icon: <TrendingUp className="size-3" />,
    cls: "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
  },
  experience: {
    label: "Experience",
    icon: <Star className="size-3" />,
    cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300",
  },
  comment: {
    label: "Comment",
    icon: <MessageSquare className="size-3" />,
    cls: "bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300",
  },
};

interface FeedbackTableProps {
  items: FeedbackItem[];
  getUserName: (userId: number | null) => string;
  onViewDetails: (item: FeedbackItem) => void;
  onReply: (id: number) => void;
  sortField: string;
  sortDirection: "asc" | "desc";
  onSort: (field: string) => void;
  t: (key: string) => string;
}

export function FeedbackTable({ items, getUserName, onViewDetails, onReply, sortField, sortDirection, onSort, t }: FeedbackTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <SortableTableHead
            field="id"
            sortable
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={onSort}
            className="w-16"
          >
            ID
          </SortableTableHead>
          <SortableTableHead
            field="type"
            sortable
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={onSort}
            className="w-32"
          >
            {t("feedback.type")}
          </SortableTableHead>
          <TableHead className="w-48">{t("feedback.user")}</TableHead>
          <TableHead>{t("feedback.content")}</TableHead>
          <SortableTableHead
            field="submitted_at"
            sortable
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={onSort}
            className="w-40"
          >
            {t("feedback.submittedAt")}
          </SortableTableHead>
          <TableHead className="w-32">{t("feedback.status")}</TableHead>
          <TableHead className="w-32 text-right">{t("common.actions")}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) => {
          const typeBadge = TYPE_BADGE[item.type];
          return (
          <TableRow key={`${item.type}-${item.id}`} className="hover:bg-muted/50 cursor-pointer" onClick={() => onViewDetails(item)}>
            <TableCell className="text-muted-foreground font-mono text-xs">#{item.id}</TableCell>
            <TableCell>
              {typeBadge ? (
                <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", typeBadge.cls)}>
                  {typeBadge.icon}
                  {typeBadge.label}
                </span>
              ) : (
                <StatusBadge status={item.type} />
              )}
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                {item.is_anonymous ? (
                  <div className="bg-muted flex items-center gap-1.5 rounded-full px-2.5 py-1">
                    <UserX className="text-muted-foreground size-3.5" />
                    <span className="text-muted-foreground text-xs">{t("feedback.anonymous")}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1.5">
                    <UserAvatar name={getUserName(item.user_id)} id={item.user_id ?? 0} size="sm" />
                    <span className="text-sm font-medium">{getUserName(item.user_id)}</span>
                  </div>
                )}
              </div>
            </TableCell>
            <TableCell>
              {item.type === "pulse" && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 rounded-md bg-blue-500/10 px-3 py-1.5 text-blue-500 dark:bg-blue-500/20 dark:text-blue-400">
                    <span className="text-lg font-bold">{item.rating}</span>
                    <span className="text-sm">/10</span>
                  </div>
                </div>
              )}
              {item.type === "experience" && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 rounded-md bg-green-500/10 px-3 py-1.5 text-green-500 dark:bg-green-500/20 dark:text-green-400">
                    <span className="text-lg font-bold">{item.rating}</span>
                    <span className="text-sm">/5</span>
                    <Star className="h-4 w-4 fill-current" />
                  </div>
                </div>
              )}
              {item.type === "comment" && (
                <span className="line-clamp-2 max-w-64 text-sm">{item.comment || "-"}</span>
              )}
            </TableCell>
            <TableCell className="text-muted-foreground text-sm">
              {formatDateTime(item.submitted_at)}
            </TableCell>
            <TableCell>
              {item.type === "comment" && item.reply ? (
                <StatusBadge status="replied" />
              ) : item.type === "comment" && item.is_anonymous && !item.allow_contact ? (
                <StatusBadge status="no_reply" />
              ) : (
                <StatusBadge status="pending" />
              )}
            </TableCell>
            <TableCell className="text-right">
              <TableActions
                actions={[
                  buildViewAction(() => onViewDetails(item), t("feedback.viewDetails")),
                  buildReplyAction(
                    () => onReply(item.id),
                    t("feedback.reply"),
                    item.type === "comment" && (!item.is_anonymous || item.allow_contact),
                  ),
                ]}
              />
            </TableCell>
          </TableRow>
        );
        })}
      </TableBody>
    </Table>
  );
}
