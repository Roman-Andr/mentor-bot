import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, { label: string; className: string }> = {
  ACTIVE: { label: "Активен", className: "bg-green-100 text-green-800" },
  INACTIVE: { label: "Неактивен", className: "bg-gray-100 text-gray-800" },
  DRAFT: { label: "Черновик", className: "bg-yellow-100 text-yellow-800" },
  PUBLISHED: { label: "Опубликовано", className: "bg-blue-100 text-blue-800" },
  ARCHIVED: { label: "Архив", className: "bg-gray-100 text-gray-800" },
  COMPLETED: { label: "Завершён", className: "bg-green-100 text-green-800" },
  PENDING: { label: "Ожидает", className: "bg-yellow-100 text-yellow-800" },
  IN_PROGRESS: { label: "В работе", className: "bg-blue-100 text-blue-800" },
  OVERDUE: { label: "Просрочен", className: "bg-red-100 text-red-800" },
  BLOCKED: { label: "Заблокирован", className: "bg-orange-100 text-orange-800" },
  CANCELLED: { label: "Отменён", className: "bg-gray-100 text-gray-800" },
  ACCEPTED: { label: "Принято", className: "bg-green-100 text-green-800" },
  USED: { label: "Принято", className: "bg-green-100 text-green-800" },
  EXPIRED: { label: "Истёк", className: "bg-red-100 text-red-800" },
  REVOKED: { label: "Отозвано", className: "bg-gray-100 text-gray-800" },
  SENT: { label: "Отправлено", className: "bg-blue-100 text-blue-800" },
  FAILED: { label: "Ошибка", className: "bg-red-100 text-red-800" },
};

const DEFAULT_STYLE = { label: "", className: "bg-gray-100 text-gray-800" };

interface StatusBadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const style = STATUS_STYLES[status] ?? DEFAULT_STYLE;
  const displayLabel = label ?? style.label ?? status;

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
