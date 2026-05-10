"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import type { ReactNode } from "react";
import { Card, CardContent } from "@/shared/ui/card";
import { Pagination } from "@/shared/ui/pagination";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";

interface DataTableProps {
  loading: boolean;
  empty?: boolean;
  emptyMessage?: string;
  loadingMessage?: string;
  currentPage?: number;
  totalPages?: number;
  totalCount?: number;
  pageSize?: number;
  pageSizeOptions?: number[];
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  showPageSizeSelector?: boolean;
  showPageInput?: boolean;
  header?: ReactNode;
  skeleton?: ReactNode;
  children: ReactNode;
  showLoadingSkeleton?: boolean;
  mobileView?: ReactNode;
  mobileBreakpoint?: "sm" | "md" | "lg" | "xl";
}

export function DataTable({
  loading,
  empty,
  emptyMessage,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  pageSizeOptions,
  onPageChange,
  onPageSizeChange,
  showPageSizeSelector = true,
  showPageInput = true,
  header,
  skeleton,
  children,
  showLoadingSkeleton = true,
  mobileView,
  mobileBreakpoint = "md",
}: DataTableProps) {
  const t = useTranslations();

  const hasPagination =
    currentPage !== undefined &&
    totalPages !== undefined &&
    totalCount !== undefined &&
    onPageChange !== undefined;

  const breakpointClasses = {
    sm: "hidden sm:block",
    md: "hidden md:block",
    lg: "hidden lg:block",
    xl: "hidden xl:block",
  };

  const mobileBreakpointClasses = {
    sm: "block sm:hidden",
    md: "block md:hidden",
    lg: "block lg:hidden",
    xl: "block xl:hidden",
  };

  return (
    <Card>
      <CardContent className="p-0 transition-none">
        {header}
        {loading && showLoadingSkeleton ? (
          skeleton ?? <DataTableSkeleton columns={5} rows={5} showHeader={false} />
        ) : empty ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">
            {emptyMessage ?? t("common.noData")}
          </div>
        ) : (
          <>
            {/* Desktop/Table View */}
            <div className={breakpointClasses[mobileBreakpoint]}>{children}</div>
            {/* Mobile Card View */}
            {mobileView && <div className={mobileBreakpointClasses[mobileBreakpoint]}>{mobileView}</div>}
          </>
        )}
        {!loading && hasPagination && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalCount={totalCount}
            pageSize={pageSize}
            pageSizeOptions={pageSizeOptions}
            onPageChange={onPageChange}
            onPageSizeChange={onPageSizeChange}
            showPageSizeSelector={showPageSizeSelector && !!onPageSizeChange && !!pageSize}
            showPageInput={showPageInput}
          />
        )}
      </CardContent>
    </Card>
  );
}
