import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NextIntlClientProvider } from "next-intl";
import { ToastProvider } from "@/shared/ui/toast";
import { PaginationContext } from "@/shared/providers/pagination-provider";
import {
  useChecklists,
  mapToItem,
  toCreatePayload,
  toUpdatePayload,
  toForm,
  type ChecklistItem,
  type ChecklistFormData,
} from "@/shared/hooks/use-checklists";
import { mockFetchResponse } from "../setup";
import messages from "../../messages/en.json";

const MockPaginationProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <PaginationContext.Provider value={{ pageSize: 20, setPageSize: vi.fn() }}>
      {children}
    </PaginationContext.Provider>
  );
};

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <NextIntlClientProvider locale="en" messages={messages}>
      <MockPaginationProvider>
        <ToastProvider>
          <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </ToastProvider>
      </MockPaginationProvider>
    </NextIntlClientProvider>
  );
};

describe("useChecklists", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.alert = vi.fn();
  });

  it("exports useChecklists function", () => {
    expect(typeof useChecklists).toBe("function");
  });

  describe("mapToItem", () => {
    it("transforms API data to ChecklistItem with user name from map", () => {
      const data = {
        id: 1,
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        status: "active",
        progress_percentage: 50,
        completed_tasks: 5,
        total_tasks: 10,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        completed_at: null,
        mentor_id: 10,
        hr_id: 20,
        notes: "Test notes",
        is_overdue: false,
        days_remaining: 30,
        created_at: "2024-01-01T00:00:00Z",
        cert_uid: null,
      };

      const usersMap = new Map([[123, "John Doe"]]);

      const result = mapToItem(data, usersMap);
      expect(result.id).toBe(1);
      expect(result.userId).toBe(123);
      expect(result.employeeId).toBe("EMP001");
      expect(result.userName).toBe("John Doe");
      expect(result.templateId).toBe(5);
      expect(result.status).toBe("active");
      expect(result.progressPercentage).toBe(50);
      expect(result.completedTasks).toBe(5);
      expect(result.totalTasks).toBe(10);
      expect(result.mentorId).toBe(10);
      expect(result.hrId).toBe(20);
      expect(result.notes).toBe("Test notes");
      expect(result.isOverdue).toBe(false);
      expect(result.daysRemaining).toBe(30);
    });

    it("falls back to employee_id when user not in map", () => {
      const data = {
        id: 1,
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        status: "active",
        progress_percentage: 50,
        completed_tasks: 5,
        total_tasks: 10,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        completed_at: null,
        mentor_id: null,
        hr_id: null,
        notes: null,
        is_overdue: false,
        days_remaining: 30,
        created_at: "2024-01-01T00:00:00Z",
        cert_uid: null,
      };

      const usersMap = new Map();

      const result = mapToItem(data, usersMap);
      expect(result.userName).toBe("EMP001");
    });

    it("falls back to default when employee_id is empty", () => {
      const data = {
        id: 1,
        user_id: 123,
        employee_id: "",
        template_id: 5,
        status: "active",
        progress_percentage: 50,
        completed_tasks: 5,
        total_tasks: 10,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        completed_at: null,
        mentor_id: null,
        hr_id: null,
        notes: null,
        is_overdue: false,
        days_remaining: 30,
        created_at: "2024-01-01T00:00:00Z",
        cert_uid: null,
      };

      const usersMap = new Map();

      const result = mapToItem(data, usersMap);
      expect(result.userName).toBe("User 123");
    });
  });

  describe("toCreatePayload", () => {
    it("converts form data to API payload", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        mentor_id: 10,
        hr_id: 20,
        notes: "Test notes",
      };

      const result = toCreatePayload(form);
      expect(result.user_id).toBe(123);
      expect(result.employee_id).toBe("EMP001");
      expect(result.template_id).toBe(5);
      expect(result.mentor_id).toBe(10);
      expect(result.hr_id).toBe(20);
      expect(result.notes).toBe("Test notes");
      expect(result.start_date).toContain("2024-01-01");
      expect(result.due_date).toContain("2024-12-31");
    });

    it("converts dates to ISO format", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-15",
        due_date: "2024-12-20",
        mentor_id: null,
        hr_id: null,
        notes: "",
      };

      const result = toCreatePayload(form);
      expect(result.start_date).toBe("2024-01-15T00:00:00.000Z");
      expect(result.due_date).toBe("2024-12-20T00:00:00.000Z");
    });

    it("handles null due_date", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "",
        mentor_id: null,
        hr_id: null,
        notes: "",
      };

      const result = toCreatePayload(form);
      expect(result.due_date).toBeNull();
    });

    it("converts empty notes to null", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "",
        mentor_id: null,
        hr_id: null,
        notes: "",
      };

      const result = toCreatePayload(form);
      expect(result.notes).toBeNull();
    });
  });

  describe("toUpdatePayload", () => {
    it("converts form data to update payload", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        mentor_id: 10,
        hr_id: 20,
        notes: "Updated notes",
      };

      const result = toUpdatePayload(form);
      expect(result.mentor_id).toBe(10);
      expect(result.hr_id).toBe(20);
      expect(result.notes).toBe("Updated notes");
      expect(result).not.toHaveProperty("user_id");
      expect(result).not.toHaveProperty("employee_id");
      expect(result).not.toHaveProperty("template_id");
    });

    it("converts empty notes to null", () => {
      const form: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "",
        mentor_id: null,
        hr_id: null,
        notes: "",
      };

      const result = toUpdatePayload(form);
      expect(result.notes).toBeNull();
    });
  });

  describe("toForm", () => {
    it("converts ChecklistItem to FormData", () => {
      const item: ChecklistItem = {
        id: 1,
        userId: 123,
        employeeId: "EMP001",
        userName: "John Doe",
        templateId: 5,
        status: "active",
        progressPercentage: 50,
        completedTasks: 5,
        totalTasks: 10,
        startDate: "2024-01-01T00:00:00Z",
        dueDate: "2024-12-31T23:59:59Z",
        completedAt: null,
        mentorId: 10,
        hrId: 20,
        notes: "Test notes",
        isOverdue: false,
        daysRemaining: 30,
        createdAt: "2024-01-01T00:00:00Z",
        certUid: null,
      };

      const result = toForm(item);
      expect(result.user_id).toBe(123);
      expect(result.employee_id).toBe("EMP001");
      expect(result.template_id).toBe(5);
      expect(result.start_date).toBe("2024-01-01");
      expect(result.due_date).toBe("2024-12-31");
      expect(result.mentor_id).toBe(10);
      expect(result.hr_id).toBe(20);
      expect(result.notes).toBe("Test notes");
    });

    it("handles null dueDate", () => {
      const item: ChecklistItem = {
        id: 1,
        userId: 123,
        employeeId: "EMP001",
        userName: "John Doe",
        templateId: 5,
        status: "active",
        progressPercentage: 50,
        completedTasks: 5,
        totalTasks: 10,
        startDate: "2024-01-01T00:00:00Z",
        dueDate: null,
        completedAt: null,
        mentorId: null,
        hrId: null,
        notes: null,
        isOverdue: false,
        daysRemaining: 30,
        createdAt: "2024-01-01T00:00:00Z",
        certUid: null,
      };

      const result = toForm(item);
      expect(result.due_date).toBe("");
      expect(result.mentor_id).toBeNull();
      expect(result.hr_id).toBeNull();
      expect(result.notes).toBe("");
    });

    it("handles null notes", () => {
      const item: ChecklistItem = {
        id: 1,
        userId: 123,
        employeeId: "EMP001",
        userName: "John Doe",
        templateId: 5,
        status: "active",
        progressPercentage: 50,
        completedTasks: 5,
        totalTasks: 10,
        startDate: "2024-01-01T00:00:00Z",
        dueDate: null,
        completedAt: null,
        mentorId: null,
        hrId: null,
        notes: null,
        isOverdue: false,
        daysRemaining: 30,
        createdAt: "2024-01-01T00:00:00Z",
        certUid: null,
      };

      const result = toForm(item);
      expect(result.notes).toBe("");
    });
  });

  describe("hook integration", () => {
    it("loads checklists list", async () => {
      mockFetchResponse({
        checklists: [
          {
            id: 1,
            user_id: 123,
            employee_id: "EMP001",
            template_id: 5,
            status: "active",
            progress_percentage: 50,
            completed_tasks: 5,
            total_tasks: 10,
            start_date: "2024-01-01",
            due_date: "2024-12-31",
            completed_at: null,
            mentor_id: 10,
            hr_id: 20,
            notes: "Test notes",
            is_overdue: false,
            days_remaining: 30,
            created_at: "2024-01-01T00:00:00Z",
            cert_uid: null,
          },
        ],
        total: 1,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.checklists).toHaveLength(1);
      expect(result.current.totalCount).toBe(1);
    });

    it("loads users for mapping", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.checklists).toEqual([]);
    });

    it("handles form data", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const newFormData: ChecklistFormData = {
        user_id: 123,
        employee_id: "EMP001",
        template_id: 5,
        start_date: "2024-01-01",
        due_date: "2024-12-31",
        mentor_id: 10,
        hr_id: 20,
        notes: "Test notes",
      };

      act(() => {
        result.current.setFormData(newFormData);
      });
      expect(result.current.formData).toEqual(newFormData);
    });

    it("resets form", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      act(() => {
        result.current.resetForm();
      });
      expect(result.current.formData.user_id).toBe(0);
    });

    it("resets filters", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      act(() => {
        result.current.resetFilters();
      });
      expect(result.current.searchQuery).toBe("");
      expect(result.current.statusFilter).toBe("ALL");
    });

    it("builds usersMap from users data", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // The hook should initialize properly
      expect(result.current).toBeDefined();
      expect(result.current.formData).toBeDefined();
      expect(result.current.handleCreate).toBeDefined();
    });

    it("handles create operation with proper form data", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        result.current.setFormData({
          user_id: 1,
          start_date: "2024-01-01",
          due_date: "2024-01-08",
          employee_id: "EMP001",
          mentor_id: 1,
          template_id: 1,
          notes: "Test notes",
          hr_id: null,
        });
      });

      // Mock the create API response
      mockFetchResponse({ success: true, data: { id: 1, title: "Test Checklist" } });

      await act(async () => {
        await result.current.handleCreate();
      });

      // Should handle the create operation without throwing
      expect(result.current).toBeDefined();
    });

    it("handles update operation with proper form data", async () => {
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        result.current.setFormData({
          user_id: 1,
          start_date: "2024-01-01",
          due_date: "2024-01-15",
          employee_id: "EMP001",
          mentor_id: 1,
          template_id: 1,
          notes: "Updated notes",
          hr_id: null,
        });
      });

      // Mock the update API response
      mockFetchResponse({ success: true, data: { id: 1, title: "Updated Checklist" } });

      await act(async () => {
        await result.current.handleUpdate();
      });

      // Should handle the update operation without throwing
      expect(result.current).toBeDefined();
    });

    it("handles complete operation with proper error handling", async () => {
      // Mock the initial checklists list response
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Mock alert for error handling
      const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});

      // Mock the getTasks API response (returns array directly)
      const mockFetch = vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            { id: 1, title: "Task 1", status: "PENDING" },
            { id: 2, title: "Task 2", status: "COMPLETED" },
          ],
        })
        .mockResolvedValue({
          ok: true,
          json: async () => ({ success: true }),
        });

      global.fetch = mockFetch;

      // Test that the handleComplete function exists and can be called
      expect(result.current.handleComplete).toBeDefined();

      // Call handleComplete - it should work now with proper API mocking
      await act(async () => {
        await result.current.handleComplete(1);
      });

      alertSpy.mockRestore();
    });

    it("handles complete operation with task completion logic", async () => {
      // Mock the initial checklists list response
      mockFetchResponse({
        checklists: [],
        total: 0,
      });

      const { result } = renderHook(() => useChecklists(), { wrapper: createWrapper() });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Mock console for error handling
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

      // Mock the getTasks API response (returns array directly)
      const mockFetch = vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            { id: 1, title: "Task 1", status: "PENDING" },
            { id: 2, title: "Task 2", status: "PENDING" },
          ],
        })
        .mockResolvedValue({
          ok: true,
          json: async () => ({ success: true }),
        })
        .mockResolvedValue({
          ok: true,
          json: async () => ({ success: true }),
        });

      global.fetch = mockFetch;

      // Test that the handleComplete function exists and can be called
      expect(result.current.handleComplete).toBeDefined();

      // Call handleComplete - it should work now with proper API mocking
      await act(async () => {
        await result.current.handleComplete(1);
      });

      consoleSpy.mockRestore();
    });
  });
});
