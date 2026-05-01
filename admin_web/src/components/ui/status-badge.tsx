"use client";

import { useTranslations } from "@/hooks/use-translations";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, { className: string }> = {
  ACTIVE: { className: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
  INACTIVE: { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" },
  DRAFT: { className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400" },
  PUBLISHED: { className: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400" },
  ARCHIVED: { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" },
  COMPLETED: { className: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
  PENDING: { className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400" },
  IN_PROGRESS: { className: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400" },
  OVERDUE: { className: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400" },
  BLOCKED: { className: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400" },
  CANCELLED: { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" },
  ACCEPTED: { className: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
  USED: { className: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
  EXPIRED: { className: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400" },
  REVOKED: { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" },
  SENT: { className: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400" },
  FAILED: { className: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400" },
  RESOLVED: { className: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
  CLOSED: { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" },
};

const DEFAULT_STYLE = { className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400" };

type StatusKey =
  | "ACTIVE"
  | "INACTIVE"
  | "DRAFT"
  | "PUBLISHED"
  | "ARCHIVED"
  | "COMPLETED"
  | "PENDING"
  | "IN_PROGRESS"
  | "OVERDUE"
  | "BLOCKED"
  | "CANCELLED"
  | "ACCEPTED"
  | "USED"
  | "EXPIRED"
  | "REVOKED"
  | "SENT"
  | "FAILED"
  | "RESOLVED"
  | "CLOSED"
  | "SCHEDULED"
  | "MISSED";

interface StatusBadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const t = useTranslations("statuses");
  const style = STATUS_STYLES[status] ?? DEFAULT_STYLE;
  const displayLabel = label ?? t(status as StatusKey) ?? status;

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        style.className,
        className,
      )}
    >
      {displayLabel}
    </span>
  );
}
