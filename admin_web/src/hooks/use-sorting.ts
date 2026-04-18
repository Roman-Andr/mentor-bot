"use client";

import { useState, useCallback } from "react";

export type SortDirection = "asc" | "desc";

export interface SortState {
  field: string | null;
  direction: SortDirection;
}

export interface UseSortingReturn {
  sortField: string | null;
  sortDirection: SortDirection;
  sortState: SortState;
  toggleSort: (field: string) => void;
  setSort: (field: string, direction: SortDirection) => void;
  clearSort: () => void;
}

export function useSorting(initialField: string | null = null): UseSortingReturn {
  const [sortField, setSortField] = useState<string | null>(initialField);
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const toggleSort = useCallback((field: string) => {
    if (sortField === field) {
      // Same column: toggle direction
      setSortDirection((currentDir) => (currentDir === "asc" ? "desc" : "asc"));
    } else {
      // Different column: reset to asc
      setSortField(field);
      setSortDirection("asc");
    }
  }, [sortField]);

  const setSort = useCallback((field: string, direction: SortDirection) => {
    setSortField(field);
    setSortDirection(direction);
  }, []);

  const clearSort = useCallback(() => {
    setSortField(null);
    setSortDirection("asc");
  }, []);

  return {
    sortField,
    sortDirection,
    sortState: { field: sortField, direction: sortDirection },
    toggleSort,
    setSort,
    clearSort,
  };
}
