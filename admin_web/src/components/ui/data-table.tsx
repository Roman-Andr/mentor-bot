"use client";

import { useTranslations } from "@/hooks/use-translations";
import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Pagination } from "@/components/ui/pagination";

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
  children: ReactNode;
}

export function DataTable({
  loading,
  empty,
  emptyMessage,
  loadingMessage,
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
  children,
}: DataTableProps) {
  const t = useTranslations();

  const hasPagination =
    currentPage !== undefined &&
    totalPages !== undefined &&
    totalCount !== undefined &&
    onPageChange !== undefined;

  return (
    <Card>
      <CardContent className="p-0">
        {header}
        {loading ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">
            {loadingMessage ?? t("common.loading")}
          </div>
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
