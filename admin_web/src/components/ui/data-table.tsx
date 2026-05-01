"use client";

import { useTranslations } from "@/hooks/use-translations";
import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Pagination } from "@/components/ui/pagination";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";

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
}: DataTableProps) {
  const t = useTranslations();

  const hasPagination =
    currentPage !== undefined &&
    totalPages !== undefined &&
    totalCount !== undefined &&
    onPageChange !== undefined;

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
          children
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
