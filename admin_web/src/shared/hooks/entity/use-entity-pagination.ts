import { useState, useCallback } from "react";
import { usePaginationSettings } from "@/shared/providers/pagination-provider";
import { useSearchParams, useRouter } from "next/navigation";

export function useEntityPagination(initialPageSize?: number) {
  const { pageSize: globalPageSize, setPageSize: setGlobalPageSize } = usePaginationSettings();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [currentPage, setCurrentPage] = useState(() => {
    const pageParam = searchParams.get("page");
    return pageParam ? parseInt(pageParam, 10) : 1;
  });
  const [pageSizeState, setPageSizeLocal] = useState(globalPageSize);

  const setCurrentPageWithUrl = useCallback((page: number | ((prev: number) => number)) => {
    const newPage = typeof page === "function" ? page(currentPage) : page;
    setCurrentPage(newPage);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    if (newPage === 1) {
      params.delete("page");
    } else {
      params.set("page", newPage.toString());
    }
    router.push(`?${params.toString()}`, { scroll: false });
  }, [currentPage, searchParams, router]);

  const setPageSize = useCallback((size: number) => {
    setPageSizeLocal(size);
    setGlobalPageSize(size);
    setCurrentPageWithUrl(1);
  }, [setGlobalPageSize, setCurrentPageWithUrl]);

  return {
    currentPage,
    setCurrentPage: setCurrentPageWithUrl,
    pageSize: pageSizeState,
    setPageSize,
  };
}
