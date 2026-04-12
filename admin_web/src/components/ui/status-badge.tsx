"use client";

import { useTranslations } from "@/hooks/use-translations";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, { className: string }> = {
  ACTIVE: { className: "bg-green-100 text-green-800" },
  INACTIVE: { className: "bg-gray-100 text-gray-800" },
  DRAFT: { className: "bg-yellow-100 text-yellow-800" },
  PUBLISHED: { className: "bg-blue-100 text-blue-800" },
  ARCHIVED: { className: "bg-gray-100 text-gray-800" },
  COMPLETED: { className: "bg-green-100 text-green-800" },
  PENDING: { className: "bg-yellow-100 text-yellow-800" },
  IN_PROGRESS: { className: "bg-blue-100 text-blue-800" },
  OVERDUE: { className: "bg-red-100 text-red-800" },
  BLOCKED: { className: "bg-orange-100 text-orange-800" },
  CANCELLED: { className: "bg-gray-100 text-gray-800" },
  ACCEPTED: { className: "bg-green-100 text-green-800" },
  USED: { className: "bg-green-100 text-green-800" },
  EXPIRED: { className: "bg-red-100 text-red-800" },
  REVOKED: { className: "bg-gray-100 text-gray-800" },
  SENT: { className: "bg-blue-100 text-blue-800" },
  FAILED: { className: "bg-red-100 text-red-800" },
  RESOLVED: { className: "bg-green-100 text-green-800" },
  CLOSED: { className: "bg-gray-100 text-gray-800" },
};

const DEFAULT_STYLE = { className: "bg-gray-100 text-gray-800" };

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
  | "CLOSED";

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
