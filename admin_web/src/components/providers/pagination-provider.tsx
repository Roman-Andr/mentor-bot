"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";

const STORAGE_KEY = "mentor-bot-pagination-settings";
const DEFAULT_PAGE_SIZE = 20;

interface PaginationSettings {
  pageSize: number;
}

interface PaginationContextType {
  pageSize: number;
  setPageSize: (size: number) => void;
}

const PaginationContext = createContext<PaginationContextType | undefined>(
  undefined
);

export function PaginationProvider({ children }: { children: ReactNode }) {
  const [pageSize, setPageSizeState] = useState<number>(DEFAULT_PAGE_SIZE);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const settings: PaginationSettings = JSON.parse(stored);
        if (settings.pageSize && [10, 20, 50, 100].includes(settings.pageSize)) {
          setPageSizeState(settings.pageSize);
        }
      }
    } catch {
      // Ignore localStorage errors
    }
    setIsLoaded(true);
  }, []);

  // Save settings to localStorage when changed
  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
    try {
      const settings: PaginationSettings = { pageSize: size };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  // Prevent hydration mismatch by not rendering until loaded
  if (!isLoaded) {
    return (
      <PaginationContext.Provider
        value={{ pageSize: DEFAULT_PAGE_SIZE, setPageSize: () => {} }}
      >
        {children}
      </PaginationContext.Provider>
    );
  }

  return (
    <PaginationContext.Provider value={{ pageSize, setPageSize }}>
      {children}
    </PaginationContext.Provider>
  );
}

export function usePaginationSettings() {
  const context = useContext(PaginationContext);
  if (context === undefined) {
    throw new Error(
      "usePaginationSettings must be used within a PaginationProvider"
    );
  }
  return context;
}
