import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { UserX, User, Star } from "lucide-react";
import { TableActions, buildViewAction, buildReplyAction } from "@/components/shared";
import { formatDateTime } from "@/lib/utils";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import type { FeedbackItem } from "@/types";

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
            Type
          </SortableTableHead>
          <TableHead className="w-48">User</TableHead>
          <TableHead>Content</TableHead>
          <SortableTableHead
            field="submitted_at"
            sortable
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={onSort}
            className="w-40"
          >
            Submitted At
          </SortableTableHead>
          <TableHead className="w-32">Status</TableHead>
          <TableHead className="w-32 text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) => (
          <TableRow key={`${item.type}-${item.id}`} className="hover:bg-muted/50">
            <TableCell className="font-mono text-sm">{item.id}</TableCell>
            <TableCell>
              <StatusBadge status={item.type} />
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                {item.is_anonymous ? (
                  <div className="bg-muted flex items-center gap-2 rounded-md px-2 py-1">
                    <UserX className="text-muted-foreground h-3.5 w-3.5" />
                    <span className="text-muted-foreground text-sm">Anonymous</span>
                  </div>
                ) : (
                  <div className="bg-primary/10 dark:bg-primary/20 flex items-center gap-2 rounded-md px-2 py-1">
                    <User className="text-primary h-3.5 w-3.5" />
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
        ))}
      </TableBody>
    </Table>
  );
}
