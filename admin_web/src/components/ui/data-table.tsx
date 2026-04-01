"use client";

import { useTranslations } from "next-intl";
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
  onPageChange?: (page: number) => void;
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
  onPageChange,
  header,
  children,
}: DataTableProps) {
  const t = useTranslations("common");

  return (
    <Card>
      <CardContent className="p-0">
        {header}
        {loading ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">
            {loadingMessage ?? t("loading")}
          </div>
        ) : empty ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">
            {emptyMessage ?? t("noData")}
          </div>
        ) : (
          children
        )}
        {!loading && currentPage !== undefined && totalPages !== undefined && onPageChange && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalCount={totalCount}
            onPageChange={onPageChange}
          />
        )}
      </CardContent>
    </Card>
  );
}