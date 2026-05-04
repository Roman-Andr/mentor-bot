"use client";

import { cn } from "@/lib/utils";
import { ArrowUp, ArrowDown } from "lucide-react";
import type { ReactNode } from "react";
import type { SortDirection } from "@/hooks/use-sorting";

interface SortableTableHeadProps {
  /** Column header content */
  children: ReactNode;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Current sort field */
  sortField: string | null | undefined;
  /** This column's field key */
  field: string;
  /** Current sort direction */
  sortDirection: SortDirection;
  /** Callback when header is clicked */
  onSort: (field: string) => void;
  /** Custom className */
  className?: string;
  /** Column width class (e.g., "w-24", "w-1/4") */
  width?: string;
}

export function SortableTableHead({
  children,
  sortable = false,
  sortField,
  field,
  sortDirection,
  onSort,
  className,
  width,
}: SortableTableHeadProps) {
  const isActive = sortField === field;

  return (
    <th
      className={cn(
        "h-10 px-2 text-left align-middle font-medium text-muted-foreground",
        sortable && "cursor-pointer select-none hover:text-foreground",
        width,
        className
      )}
      onClick={sortable ? () => onSort(field) : undefined}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortable && (
          <span className="flex flex-col">
            <ArrowUp
              className={cn(
                "size-3",
                isActive && sortDirection === "asc"
                  ? "text-foreground"
                  : "text-muted-foreground/30"
              )}
            />
            <ArrowDown
              className={cn(
                "size-3 -mt-1",
                isActive && sortDirection === "desc"
                  ? "text-foreground"
                  : "text-muted-foreground/30"
              )}
            />
          </span>
        )}
      </div>
    </th>
  );
}
