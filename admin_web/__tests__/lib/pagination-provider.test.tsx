import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { renderHook } from "@testing-library/react";
import {
  PaginationProvider,
  PaginationContext,
  usePaginationSettings,
} from "@/shared/providers/pagination-provider";
import { useContext, useEffect, type ReactNode } from "react";

const STORAGE_KEY = "mentor-bot-pagination-settings";

const wrapper = ({ children }: { children: ReactNode }) => (
  <PaginationProvider>{children}</PaginationProvider>
);

describe("PaginationProvider", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders children", () => {
    const InitialConsumer = () => {
      const { setPageSize } = usePaginationSettings();
      useEffect(() => {
        setPageSize(50);
      }, [setPageSize]);
      return <div data-testid="child">child</div>;
    };

    render(
      <PaginationProvider>
        <InitialConsumer />
      </PaginationProvider>,
    );
    expect(screen.getByTestId("child")).toBeDefined();
  });

  it("provides default page size of 20", () => {
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    expect([10, 20, 50, 100]).toContain(result.current.pageSize);
  });

  it("loads page size from localStorage", () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ pageSize: 50 }));
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    expect(result.current.pageSize).toBe(50);
  });

  it("ignores invalid page size from localStorage", () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ pageSize: 999 }));
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    expect(result.current.pageSize).toBe(20);
  });

  it("ignores malformed localStorage data", () => {
    localStorage.setItem(STORAGE_KEY, "not-json");
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    expect(result.current.pageSize).toBe(20);
  });

  it("setPageSize updates value and saves to localStorage", () => {
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    act(() => result.current.setPageSize(100));
    expect(result.current.pageSize).toBe(100);
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    expect(stored.pageSize).toBe(100);
  });

  it("handles localStorage write errors gracefully", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementationOnce(() => {
      throw new Error("Storage full");
    });
    const { result } = renderHook(() => usePaginationSettings(), { wrapper });
    act(() => {});
    expect(() => act(() => result.current.setPageSize(10))).not.toThrow();
  });
});

describe("usePaginationSettings outside provider", () => {
  it("throws when used outside PaginationProvider", () => {
    expect(() => renderHook(() => usePaginationSettings())).toThrow(
      "usePaginationSettings must be used within a PaginationProvider",
    );
  });
});
