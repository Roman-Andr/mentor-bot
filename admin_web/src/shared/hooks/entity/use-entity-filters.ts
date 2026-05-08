import { useState, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import type { FilterConfig } from "./types";

export function useEntityFilters(filters: FilterConfig[] = [], setCurrentPage: (page: number) => void) {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [filterValues, setFilterValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      const paramName = filter.paramName ?? filter.name;
      const urlValue = searchParams.get(paramName);
      initial[filter.name] = urlValue ?? filter.defaultValue;
    }
    return initial;
  });

  const [sortField, setSortField] = useState<string | null>(searchParams.get("sort_by") ?? null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">((searchParams.get("sort_order") as "asc" | "desc") ?? "asc");

  const setFilterValue = useCallback((name: string, value: string) => {
    setFilterValues((prev) => ({ ...prev, [name]: value }));
    setCurrentPage(1);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    const filter = filters.find((f) => f.name === name);
    const paramName = filter?.paramName ?? name;
    if (value === "ALL" || value === "") {
      params.delete(paramName);
    } else {
      params.set(paramName, value);
    }
    router.push(`?${params.toString()}`, { scroll: false });
  }, [setCurrentPage, searchParams, router, filters]);

  const resetFilters = useCallback(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      initial[filter.name] = filter.defaultValue;
    }
    setFilterValues(initial);
    setSortField(null);
    setSortDirection("asc");

    // Clear all filter params from URL
    const params = new URLSearchParams(searchParams.toString());
    for (const filter of filters) {
      const paramName = filter.paramName ?? filter.name;
      params.delete(paramName);
    }
    params.delete("sort_by");
    params.delete("sort_order");
    router.push(`?${params.toString()}`, { scroll: false });
  }, [filters, searchParams, router]);

  const toggleSort = useCallback((field: string) => {
    const newSortField = field;
    const newSortDirection = sortField === field && sortDirection === "asc" ? "desc" : "asc";
    setSortField(newSortField);
    setSortDirection(newSortDirection);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    params.set("sort_by", newSortField);
    params.set("sort_order", newSortDirection);
    router.push(`?${params.toString()}`, { scroll: false });
  }, [sortField, sortDirection, searchParams, router]);

  const setSort = useCallback((field: string, direction: "asc" | "desc") => {
    setSortField(field);
    setSortDirection(direction);

    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    params.set("sort_by", field);
    params.set("sort_order", direction);
    router.push(`?${params.toString()}`, { scroll: false });
  }, [searchParams, router]);

  const clearSort = useCallback(() => {
    setSortField(null);
    setSortDirection("asc");

    // Clear sort params from URL
    const params = new URLSearchParams(searchParams.toString());
    params.delete("sort_by");
    params.delete("sort_order");
    router.push(`?${params.toString()}`, { scroll: false });
  }, [searchParams, router]);

  return {
    filterValues,
    setFilterValue,
    resetFilters,
    sortField,
    sortDirection,
    toggleSort,
    setSort,
    clearSort,
  };
}
