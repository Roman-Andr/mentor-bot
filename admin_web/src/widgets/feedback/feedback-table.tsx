import { StatusBadge } from "@/shared/ui/status-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { UserX, Star, TrendingUp, MessageSquare } from "lucide-react";
import { UserAvatar } from "@/shared/ui/user-avatar";
import {
  TableActions,
  buildViewAction,
  buildReplyAction,
  buildDeleteAction,
} from "@/shared/components";
import { formatDateTime } from "@/shared/lib/utils";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { Card, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
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
  onDelete: (item: FeedbackItem) => void;
  sortField: string;
  sortDirection: "asc" | "desc";
  onSort: (field: string) => void;
  t: (key: string) => string;
}

function FeedbackCard({
  item,
  getUserName,
  onViewDetails,
  onReply,
  onDelete,
  t,
}: {
  item: FeedbackItem;
  getUserName: (userId: number | null) => string;
  onViewDetails: (item: FeedbackItem) => void;
  onReply: (id: number) => void;
  onDelete: (item: FeedbackItem) => void;
  t: (key: string) => string;
}) {
  const typeBadge = TYPE_BADGE[item.type];

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-muted/50"
      onClick={() => onViewDetails(item)}
    >
      <CardContent className="p-4">
        {/* Header: Type Badge + User */}
        <div className="mb-3 flex items-start gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            {typeBadge?.icon || <MessageSquare className="size-4 text-primary" />}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              {typeBadge ? (
                <span
                  className={cn(
                    "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                    typeBadge.cls,
                  )}
                >
                  {typeBadge.icon}
                  {typeBadge.label}
                </span>
              ) : (
                <StatusBadge status={item.type} />
              )}
              <span className="text-xs text-muted-foreground">#{item.id}</span>
            </div>
            <div className="mt-1 flex items-center gap-2">
              {item.is_anonymous ? (
                <div className="flex items-center gap-1.5 rounded-full bg-muted px-2 py-0.5">
                  <UserX className="size-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">{t("feedback.anonymous")}</span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <UserAvatar name={getUserName(item.user_id)} id={item.user_id ?? 0} size="sm" />
                  <span className="truncate text-sm font-medium">{getUserName(item.user_id)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="mb-3">
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
          {item.type === "comment" && <p className="line-clamp-2 text-sm">{item.comment || "-"}</p>}
        </div>

        {/* Metadata */}
        <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-muted-foreground">{t("feedback.submittedAt")}: </span>
            <span>{formatDateTime(item.submitted_at)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("feedback.status")}: </span>
            {item.type === "comment" && item.reply ? (
              <StatusBadge status="replied" />
            ) : item.type === "comment" && item.is_anonymous && !item.allow_contact ? (
              <StatusBadge status="no_reply" />
            ) : (
              <StatusBadge status="pending" />
            )}
          </div>
        </div>

        {/* Footer: Actions */}
        <div
          className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
          onClick={(e) => e.stopPropagation()}
        >
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onViewDetails(item)}
          >
            {t("feedback.viewDetails")}
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onReply(item.id)}
            disabled={!(item.type === "comment" && (!item.is_anonymous || item.allow_contact))}
          >
            {t("feedback.reply")}
          </Button>
          <Button size="sm" variant="destructive" className="flex-1" onClick={() => onDelete(item)}>
            {t("common.delete")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function FeedbackTable({
  items,
  getUserName,
  onViewDetails,
  onReply,
  onDelete,
  sortField,
  sortDirection,
  onSort,
  t,
}: FeedbackTableProps) {
  const mobileView = (
    <div className="space-y-3 p-4">
      {items.map((item) => (
        <FeedbackCard
          key={`${item.type}-${item.id}`}
          item={item}
          getUserName={getUserName}
          onViewDetails={onViewDetails}
          onReply={onReply}
          onDelete={onDelete}
          t={t}
        />
      ))}
    </div>
  );

  return {
    table: (
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
              <TableRow
                key={`${item.type}-${item.id}`}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => onViewDetails(item)}
              >
                <TableCell className="font-mono text-xs text-muted-foreground">
                  #{item.id}
                </TableCell>
                <TableCell>
                  {typeBadge ? (
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
                        typeBadge.cls,
                      )}
                    >
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
                      <div className="flex items-center gap-1.5 rounded-full bg-muted px-2.5 py-1">
                        <UserX className="size-3.5 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {t("feedback.anonymous")}
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <UserAvatar
                          name={getUserName(item.user_id)}
                          id={item.user_id ?? 0}
                          size="sm"
                        />
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
                <TableCell className="text-sm text-muted-foreground">
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
                <TableCell className="text-right" onClick={(event) => event.stopPropagation()}>
                  <TableActions
                    actions={[
                      buildViewAction(() => onViewDetails(item), t("feedback.viewDetails")),
                      buildReplyAction(
                        () => onReply(item.id),
                        t("feedback.reply"),
                        item.type === "comment" && (!item.is_anonymous || item.allow_contact),
                      ),
                      buildDeleteAction(() => onDelete(item), t("common.delete")),
                    ]}
                  />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    ),
    mobileView,
  };
}
