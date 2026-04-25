import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Eye, MessageSquare, UserX, User, Star } from "lucide-react";
import { formatDateTime } from "@/lib/utils";
import type { FeedbackItem } from "@/types";

interface FeedbackTableProps {
  items: FeedbackItem[];
  getUserName: (userId: number | null) => string;
  onViewDetails: (item: FeedbackItem) => void;
  onReply: (id: number) => void;
}

export function FeedbackTable({ items, getUserName, onViewDetails, onReply }: FeedbackTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead className="w-16">ID</TableHead>
          <TableHead className="w-32">Type</TableHead>
          <TableHead className="w-48">User</TableHead>
          <TableHead>Content</TableHead>
          <TableHead className="w-40">Submitted At</TableHead>
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
                  <div className="flex items-center gap-2 px-2 py-1 bg-muted rounded-md">
                    <UserX className="w-3.5 h-3.5 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Anonymous</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 px-2 py-1 bg-primary/10 rounded-md">
                    <User className="w-3.5 h-3.5 text-primary" />
                    <span className="text-sm font-medium">{getUserName(item.user_id)}</span>
                  </div>
                )}
              </div>
            </TableCell>
            <TableCell>
              {item.type === "pulse" && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-500/10 text-blue-500 rounded-md">
                    <span className="font-bold text-lg">{item.rating}</span>
                    <span className="text-sm">/10</span>
                  </div>
                </div>
              )}
              {item.type === "experience" && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-3 py-1.5 bg-green-500/10 text-green-500 rounded-md">
                    <span className="font-bold text-lg">{item.rating}</span>
                    <span className="text-sm">/5</span>
                    <Star className="w-4 h-4 fill-current" />
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
            <TableCell className="text-right">
              <div className="flex items-center justify-end gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onViewDetails(item)}
                  title="View Details"
                  className="hover:bg-primary/10 hover:text-primary"
                >
                  <Eye className="size-4" />
                </Button>
                {item.type === "comment" && (!item.is_anonymous || item.allow_contact) && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onReply(item.id)}
                    title="Reply"
                    className="hover:bg-primary/10 hover:text-primary"
                  >
                    <MessageSquare className="size-4" />
                  </Button>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
