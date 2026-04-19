"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

interface TableSkeletonProps {
  columns: number;
  rows?: number;
  className?: string;
  header?: React.ReactNode;
}

function SkeletonCell({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-muted animate-pulse rounded",
        className
      )}
    />
  );
}

export function TableSkeleton({
  columns,
  rows = 5,
  className,
  header,
}: TableSkeletonProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {header}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {Array.from({ length: columns }).map((_, i) => (
                <TableHead key={i}>
                  <SkeletonCell className="h-4 w-20" />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: rows }).map((_, rowIndex) => (
              <TableRow key={rowIndex}>
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <TableCell key={colIndex}>
                    <SkeletonCell
                      className={cn(
                        "h-4",
                        colIndex === 0 ? "w-32" : "w-24"
                      )}
                    />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface DataTableSkeletonProps {
  columns: number;
  rows?: number;
  showHeader?: boolean;
  hasActions?: boolean;
}

export function DataTableSkeleton({
  columns,
  rows = 5,
  showHeader = true,
  hasActions = true,
}: DataTableSkeletonProps) {
  const actionCount = hasActions ? 1 : 0;
  const dataColumns = columns - actionCount;

  return (
    <div className="space-y-4">
      {showHeader && (
        <div className="flex items-center justify-between px-6 py-4">
          <SkeletonCell className="h-6 w-32" />
          <div className="flex gap-2">
            <SkeletonCell className="h-9 w-48" />
            <SkeletonCell className="h-9 w-24" />
            <SkeletonCell className="h-9 w-20" />
          </div>
        </div>
      )}
      <Table>
        <TableHeader>
          <TableRow>
            {Array.from({ length: dataColumns }).map((_, i) => (
              <TableHead key={i}>
                <SkeletonCell className="h-4 w-24" />
              </TableHead>
            ))}
            {hasActions && (
              <TableHead className="w-25">
                <SkeletonCell className="h-4 w-16" />
              </TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <TableRow key={rowIndex}>
              {Array.from({ length: dataColumns }).map((_, colIndex) => (
                <TableCell key={colIndex}>
                  <SkeletonCell
                    className={cn(
                      "h-4",
                      colIndex === 0 ? "w-36" : colIndex === 1 ? "w-28" : "w-20"
                    )}
                  />
                </TableCell>
              ))}
              {hasActions && (
                <TableCell>
                  <div className="flex gap-1">
                    <SkeletonCell className="h-8 w-8 rounded-md" />
                    <SkeletonCell className="h-8 w-8 rounded-md" />
                    <SkeletonCell className="h-8 w-8 rounded-md" />
                  </div>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
