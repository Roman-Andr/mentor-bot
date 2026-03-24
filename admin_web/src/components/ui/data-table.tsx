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
  emptyMessage = "Ничего не найдено",
  loadingMessage = "Загрузка...",
  currentPage,
  totalPages,
  totalCount,
  onPageChange,
  header,
  children,
}: DataTableProps) {
  return (
    <Card>
      <CardContent className="p-0">
        {header}
        {loading ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">
            {loadingMessage}
          </div>
        ) : empty ? (
          <div className="text-muted-foreground flex items-center justify-center py-12">{emptyMessage}</div>
        ) : (
          children
        )}
        {!loading &&
          !empty &&
          currentPage !== undefined &&
          totalPages !== undefined &&
          onPageChange && (
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
