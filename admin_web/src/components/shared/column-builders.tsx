import { StatusBadge } from "@/components/ui/status-badge";
import { formatDate, formatDateTime } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import { Calendar, Clock } from "lucide-react";

export interface ColumnDefinition<T = unknown> {
  key: string;
  header: string;
  cell: (item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
  className?: string;
}

// Common column builders
export const buildTextColumn = <T,>(
  key: string,
  header: string,
  getValue: (item: T) => string,
  options?: { sortable?: boolean; width?: string; className?: string }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => <span className="font-medium">{getValue(item)}</span>,
  sortable: options?.sortable ?? true,
  width: options?.width,
  className: options?.className,
});

export const buildDateColumn = <T,>(
  key: string,
  header: string,
  getValue: (item: T) => string | Date,
  options?: { sortable?: boolean; width?: string; format?: "date" | "datetime" }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => {
    const date = getValue(item);
    const formatted = options?.format === "datetime" 
      ? formatDateTime(date) 
      : formatDate(date);
    return <span className="text-muted-foreground text-sm">{formatted}</span>;
  },
  sortable: options?.sortable ?? true,
  width: options?.width || "w-32",
});

export const buildIconTextColumn = <T,>(
  key: string,
  header: string,
  getValue: (item: T) => string,
  Icon: LucideIcon,
  options?: { sortable?: boolean; width?: string }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => (
    <div className="flex items-center gap-1">
      <Icon className="text-muted-foreground size-4" />
      <span>{getValue(item)}</span>
    </div>
  ),
  sortable: options?.sortable ?? true,
  width: options?.width,
});

export const buildStatusColumn = <T,>(
  key: string,
  header: string,
  getStatus: (item: T) => string,
  options?: { sortable?: boolean; width?: string }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => <StatusBadge status={getStatus(item)} />,
  sortable: options?.sortable ?? true,
  width: options?.width,
});

export const buildSelectColumn = <T,>(
  key: string,
  header: string,
  getValue: (item: T) => string,
  options: { label: string; value: string }[],
  defaultValue?: string,
  config?: { sortable?: boolean; width?: string }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => {
    const value = getValue(item);
    const option = options.find((opt) => opt.value === value);
    return option?.label || defaultValue || value;
  },
  sortable: config?.sortable ?? true,
  width: config?.width,
});

export const buildYesNoColumn = <T,>(
  key: string,
  header: string,
  getValue: (item: T) => boolean,
  config?: { sortable?: boolean; width?: string }
): ColumnDefinition<T> => ({
  key,
  header,
  cell: (item) => (
    getValue(item) ? (
      <span className="text-green-600">Yes</span>
    ) : (
      <span className="text-muted-foreground">No</span>
    )
  ),
  sortable: config?.sortable ?? true,
  width: config?.width,
});

export const buildActionsColumn = <T,>(
  key: string = "actions",
  renderActions: (item: T) => React.ReactNode,
  width = "w-40"
): ColumnDefinition<T> => ({
  key,
  header: "",
  cell: renderActions,
  width,
});

// Predefined common columns
export const buildDeadlineDaysColumn = <T,>(
  getValue: (item: T) => number
): ColumnDefinition<T> => ({
  key: "deadlineDays",
  header: "Deadline Days",
  cell: (item) => (
    <div className="flex items-center gap-1">
      <Calendar className="text-muted-foreground size-4" />
      {getValue(item)} days
    </div>
  ),
  sortable: true,
});

export const buildDurationMinutesColumn = <T,>(
  getValue: (item: T) => number
): ColumnDefinition<T> => ({
  key: "durationMinutes",
  header: "Duration",
  cell: (item) => (
    <div className="flex items-center gap-1">
      <Clock className="text-muted-foreground size-4" />
      {getValue(item)} min
    </div>
  ),
  sortable: true,
  width: "w-32",
});
