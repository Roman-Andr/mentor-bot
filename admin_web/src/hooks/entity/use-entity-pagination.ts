import { useState, useCallback } from "react";
import { usePaginationSettings } from "@/components/providers/pagination-provider";

export function useEntityPagination(initialPageSize?: number) {
  const { pageSize: globalPageSize, setPageSize: setGlobalPageSize } = usePaginationSettings();

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSizeState, setPageSizeLocal] = useState(globalPageSize);

  const setPageSize = useCallback((size: number) => {
    setPageSizeLocal(size);
    setGlobalPageSize(size);
    setCurrentPage(1);
  }, [setGlobalPageSize]);

  return {
    currentPage,
    setCurrentPage,
    pageSize: initialPageSize || pageSizeState,
    setPageSize,
  };
}
