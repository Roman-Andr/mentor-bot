import { useState, useCallback, useMemo } from "react";
import type { FilterConfig } from "./types";

export function useEntityFilters(filters: FilterConfig[] = [], setCurrentPage: (page: number) => void) {
  const [filterValues, setFilterValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      initial[filter.name] = filter.defaultValue;
    }
    return initial;
  });

  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const setFilterValue = useCallback((name: string, value: string) => {
    setFilterValues((prev) => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  }, [setCurrentPage]);

  const resetFilters = useCallback(() => {
    const initial: Record<string, string> = {};
    for (const filter of filters) {
      initial[filter.name] = filter.defaultValue;
    }
    setFilterValues(initial);
    setSortField(null);
    setSortDirection("asc");
  }, [filters]);

  const toggleSort = useCallback((field: string) => {
    if (sortField === field) {
      setSortDirection((currentDir) => (currentDir === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  }, [sortField]);

  const setSort = useCallback((field: string, direction: "asc" | "desc") => {
    setSortField(field);
    setSortDirection(direction);
  }, []);

  const clearSort = useCallback(() => {
    setSortField(null);
    setSortDirection("asc");
  }, []);

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
