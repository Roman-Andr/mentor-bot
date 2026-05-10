import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

type EntityOverrides = Record<string, unknown>;

const createEntity = (overrides: EntityOverrides = {}) => ({
  items: [],
  loading: false,
  totalCount: 0,
  totalPages: 0,
  currentPage: 1,
  setCurrentPage: vi.fn(),
  pageSize: 20,
  setPageSize: vi.fn(),
  searchQuery: "",
  setSearchQuery: vi.fn(),
  filterValues: {},
  setFilterValue: vi.fn(),
  isCreateDialogOpen: false,
  setIsCreateDialogOpen: vi.fn(),
  isEditDialogOpen: false,
  setIsEditDialogOpen: vi.fn(),
  selectedItem: null,
  setSelectedItem: vi.fn(),
  formData: {},
  setFormData: vi.fn(),
  createFn: vi.fn(),
  updateFn: vi.fn(),
  handleSubmit: vi.fn(),
  handleDelete: vi.fn(),
  openEditDialog: vi.fn(),
  resetForm: vi.fn(),
  resetFilters: vi.fn(),
  invalidate: vi.fn(),
  isSubmitting: false,
  isDeleting: false,
  sortField: null,
  sortDirection: null,
  toggleSort: vi.fn(),
  extendedState: {},
  setExtendedState: vi.fn(),
  ...overrides,
});

const createApi = () => ({
  users: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  departments: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  articles: {
    list: vi.fn(),
  },
  categories: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  userMentors: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
  checklists: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getTasks: vi.fn(),
    completeTask: vi.fn(),
    complete: vi.fn(),
  },
  dialogues: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
  },
  templates: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    publish: vi.fn(),
  },
});

const mockHookDeps = (
  entity: ReturnType<typeof createEntity>,
  options: {
    api?: ReturnType<typeof createApi>;
    queryData?: unknown[];
  } = {},
) => {
  const api = options.api ?? createApi();
  const toast = vi.fn();
  const invalidateQueries = vi.fn();
  const queryData = [...(options.queryData ?? [])];
  let entityConfig: Record<string, any> | undefined;

  vi.doMock("@/shared/hooks/use-entity", () => ({
    useEntity: vi.fn((config) => {
      entityConfig = config;
      return entity;
    }),
  }));
  vi.doMock("@/shared/lib/api", () => ({ api }));
  vi.doMock("@/shared/hooks/use-toast", () => ({
    useToast: () => ({ toast }),
  }));
  vi.doMock("@/shared/hooks/use-translations", () => ({
    useTranslations: () => (key: string) => `translated:${key}`,
  }));
  vi.doMock("@/shared/lib/error", () => ({
    handleError: vi.fn(() => new Error("handled error")),
  }));
  vi.doMock("@/shared/lib/logger", () => ({
    logger: { error: vi.fn() },
  }));
  vi.doMock("@tanstack/react-query", () => ({
    useQueryClient: () => ({ invalidateQueries }),
    useQuery: vi.fn((config) => {
      const data = queryData.shift();
      return { data: config?.select && data !== undefined ? config.select(data) : data };
    }),
  }));

  return {
    api,
    toast,
    invalidateQueries,
    getEntityConfig: () => {
      if (!entityConfig) {
        throw new Error("useEntity was not called");
      }
      return entityConfig;
    },
  };
};

describe("entity hook action branches", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    global.alert = vi.fn();
  });

  it("creates checklists through the custom create handler", async () => {
    const entity = createEntity({
      formData: {
        user_id: 7,
        employee_id: "EMP-7",
        template_id: 3,
        start_date: "2024-01-01",
        due_date: "",
        mentor_id: null,
        hr_id: 2,
        notes: "",
      },
      createFn: vi.fn().mockResolvedValue({ success: true }),
    });
    const deps = mockHookDeps(entity, {
      queryData: [
        {
          success: true,
          data: {
            users: [
              { id: 7, first_name: "Ada", last_name: "Lovelace" },
              { id: 8, first_name: "Grace", last_name: null },
            ],
          },
        },
      ],
    });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    const config = deps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ user_id: 1 });
    config.updateFn(1, { notes: null });
    config.deleteFn(1);
    config.mapItem({
      id: 1,
      user_id: 7,
      employee_id: "EMP-7",
      template_id: 3,
      status: "ACTIVE",
      progress_percentage: 0,
      completed_tasks: 0,
      total_tasks: 1,
      start_date: "2024-01-01",
      due_date: null,
      completed_at: null,
      mentor_id: null,
      hr_id: null,
      notes: null,
      is_overdue: false,
      days_remaining: null,
      created_at: "2024-01-01T00:00:00Z",
      cert_uid: null,
    });
    expect(config.filters[1].transform("12")).toBe(12);
    await act(async () => {
      result.current.handleCreate();
    });
    act(() => {
      result.current.setStatusFilter("ACTIVE");
      result.current.setDepartmentFilter("12");
    });

    expect(entity.createFn).toHaveBeenCalledWith(
      expect.objectContaining({
        user_id: 7,
        due_date: null,
        notes: null,
      }),
    );
    expect(entity.invalidate).toHaveBeenCalled();
    expect(entity.setIsCreateDialogOpen).toHaveBeenCalledWith(false);
    expect(entity.resetForm).toHaveBeenCalled();
    expect(entity.setFilterValue).toHaveBeenCalledWith("status", "ACTIVE");
    expect(entity.setFilterValue).toHaveBeenCalledWith("department", "12");
  });

  it("leaves checklist create dialog open when create fails", async () => {
    const entity = createEntity({
      formData: {
        user_id: 7,
        employee_id: "EMP-7",
        template_id: 3,
        start_date: "2024-01-01",
        due_date: "2024-02-01",
        mentor_id: null,
        hr_id: null,
        notes: "Needs review",
      },
      createFn: vi.fn().mockResolvedValue({ success: false }),
    });
    mockHookDeps(entity);
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      result.current.handleCreate();
    });

    expect(entity.invalidate).not.toHaveBeenCalled();
    expect(entity.setIsCreateDialogOpen).not.toHaveBeenCalled();
    expect(entity.resetForm).not.toHaveBeenCalled();
  });

  it("updates checklists and reports task completion failures", async () => {
    const entity = createEntity({
      selectedItem: { id: 10 },
      formData: { mentor_id: 1, hr_id: null, notes: "" },
      updateFn: vi.fn().mockResolvedValue({ success: true }),
    });
    const api = createApi();
    api.checklists.completeTask
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: false, error: { message: "locked" } })
      .mockRejectedValueOnce(new Error("network down"));
    mockHookDeps(entity, { api });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      await result.current.handleUpdate(new Set([1, 2, 3]));
    });

    expect(entity.updateFn).toHaveBeenCalledWith(10, { mentor_id: 1, hr_id: null, notes: null });
    expect(api.checklists.completeTask).toHaveBeenCalledTimes(3);
    expect(global.alert).toHaveBeenCalledWith(expect.stringContaining("Task ID 2"));
    expect(entity.setIsEditDialogOpen).toHaveBeenCalledWith(false);
    expect(entity.setSelectedItem).toHaveBeenCalledWith(null);
  });

  it("skips checklist update when nothing is selected or update fails", async () => {
    const updateFn = vi.fn().mockResolvedValue({ success: false });
    let entity = createEntity({ selectedItem: null, updateFn });
    mockHookDeps(entity);
    let imported = await import("@/shared/hooks/use-checklists");
    let rendered = renderHook(() => imported.useChecklists());

    await act(async () => {
      await rendered.result.current.handleUpdate();
    });

    expect(updateFn).not.toHaveBeenCalled();

    vi.resetModules();
    entity = createEntity({
      selectedItem: { id: 10 },
      formData: { mentor_id: null, hr_id: null, notes: "" },
      updateFn,
    });
    mockHookDeps(entity);
    imported = await import("@/shared/hooks/use-checklists");
    rendered = renderHook(() => imported.useChecklists());

    await act(async () => {
      await rendered.result.current.handleUpdate();
    });

    expect(updateFn).toHaveBeenCalledWith(10, { mentor_id: null, hr_id: null, notes: null });
    expect(entity.invalidate).not.toHaveBeenCalled();
    expect(entity.setIsEditDialogOpen).not.toHaveBeenCalled();
  });

  it("completes checklists only after pending tasks complete", async () => {
    const entity = createEntity();
    const api = createApi();
    api.checklists.getTasks.mockResolvedValue({
      success: true,
      data: [
        { id: 1, title: "Done", status: "COMPLETED" },
        { id: 2, title: "Pending", status: "PENDING" },
      ],
    });
    api.checklists.completeTask.mockResolvedValue({ success: true });
    api.checklists.complete.mockResolvedValue({ success: true });
    mockHookDeps(entity, { api });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      await result.current.handleComplete(5);
    });

    expect(api.checklists.completeTask).toHaveBeenCalledWith(2);
    expect(api.checklists.complete).toHaveBeenCalledWith(5);
    expect(entity.invalidate).toHaveBeenCalled();
  });

  it("alerts when checklist completion cannot finish", async () => {
    const entity = createEntity();
    const api = createApi();
    api.checklists.getTasks.mockResolvedValue({
      success: true,
      data: [{ id: 4, title: "Pending", status: "PENDING" }],
    });
    api.checklists.completeTask.mockResolvedValue({ success: false, error: { message: "denied" } });
    mockHookDeps(entity, { api });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      await result.current.handleComplete(5);
    });

    expect(global.alert).toHaveBeenCalledWith(expect.stringContaining("Pending: denied"));
    expect(api.checklists.complete).not.toHaveBeenCalled();
  });

  it("handles checklist completion early returns and thrown errors", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    const entity = createEntity();
    const api = createApi();
    api.checklists.getTasks
      .mockResolvedValueOnce({ success: false })
      .mockResolvedValueOnce({ success: true, data: [{ id: 4, title: "Pending", status: "PENDING" }] })
      .mockRejectedValueOnce(new Error("tasks unavailable"));
    api.checklists.completeTask.mockRejectedValueOnce(new Error("task offline"));
    mockHookDeps(entity, { api });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      await result.current.handleComplete(5);
      await result.current.handleComplete(5);
      await result.current.handleComplete(5);
    });

    expect(global.alert).toHaveBeenCalledWith(expect.stringContaining("Pending: task offline"));
    expect(global.alert).toHaveBeenCalledWith(expect.stringContaining("tasks unavailable"));
    expect(consoleError).toHaveBeenCalledWith(
      "Failed to complete checklist:",
      expect.any(Error),
    );
    expect(api.checklists.complete).not.toHaveBeenCalled();
    consoleError.mockRestore();
  });

  it("alerts when checklist completion endpoint fails", async () => {
    const entity = createEntity();
    const api = createApi();
    api.checklists.getTasks.mockResolvedValue({ success: true, data: [] });
    api.checklists.complete.mockResolvedValue({ success: false, error: "blocked" });
    mockHookDeps(entity, { api });
    const { useChecklists } = await import("@/shared/hooks/use-checklists");

    const { result } = renderHook(() => useChecklists());
    await act(async () => {
      await result.current.handleComplete(5);
    });

    expect(global.alert).toHaveBeenCalledWith("Failed to complete checklist: blocked");
    expect(entity.invalidate).not.toHaveBeenCalled();
  });

  it("handles user mentor assignment success and errors", async () => {
    const entity = createEntity();
    const api = createApi();
    api.userMentors.create
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: false, error: { message: "already assigned" } });
    api.userMentors.delete
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: false, error: { message: "missing relation" } });
    const deps = mockHookDeps(entity, {
      api,
      queryData: [
        { success: true, data: { departments: [{ id: 1, name: "Engineering" }] } },
        { success: true, data: { relations: [{ id: 9, is_active: true }] } },
      ],
    });
    const { toast, invalidateQueries } = deps;
    const { useUsers } = await import("@/shared/hooks/use-users");

    const { result } = renderHook(() => useUsers());
    const config = deps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ first_name: "Ada" });
    config.updateFn(1, { first_name: "Ada" });
    config.deleteFn(1);
    config.mapItem({
      id: 1,
      first_name: "Ada",
      last_name: null,
      email: "ada@example.com",
      employee_id: "EMP-1",
      role: "MENTOR",
      department_id: null,
      department: null,
      position: null,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    });
    expect(config.filters[1].transform("4")).toBe(4);
    act(() => {
      result.current.openAssignMentorDialog({ id: 7, name: "User" } as never);
      result.current.setRoleFilter("MENTOR");
      result.current.setDepartmentFilter("4");
      result.current.loadDepartments();
    });
    await act(async () => {
      await result.current.handleAssignMentor(7, 3);
      await result.current.handleAssignMentor(7, 3);
      await result.current.handleUnassignMentor(9);
      await result.current.handleUnassignMentor(9);
    });

    expect(result.current.assignMentorDialogOpen).toBe(true);
    expect(result.current.selectedUserForMentor).toEqual({ id: 7, name: "User" });
    expect(toast).toHaveBeenCalledWith("translated:mentorAssigned", "success");
    expect(toast).toHaveBeenCalledWith("already assigned", "error");
    expect(toast).toHaveBeenCalledWith("translated:mentorUnassigned", "success");
    expect(toast).toHaveBeenCalledWith("missing relation", "error");
    expect(invalidateQueries).toHaveBeenCalledTimes(2);
    expect(entity.setFilterValue).toHaveBeenCalledWith("role", "MENTOR");
    expect(entity.setFilterValue).toHaveBeenCalledWith("department", "4");
  });

  it("wires category and department entity actions", async () => {
    const entity = createEntity();
    const api = createApi();
    const deps = mockHookDeps(entity, {
      api,
      queryData: [{ success: true, data: { departments: [{ id: 5, name: "Engineering" }] } }],
    });
    const { useCategories } = await import("@/shared/hooks/use-categories");

    renderHook(() => useCategories());
    let config = deps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ name: "Docs" });
    config.updateFn(1, { name: "Docs" });
    config.deleteFn(1);
    config.onAfterUpdate();
    config.mapItem({
      id: 1,
      name: "Docs",
      slug: "docs",
      description: null,
      parent_id: null,
      parent_name: null,
      order: 0,
      department_id: 5,
      position: null,
      level: null,
      icon: null,
      color: null,
      children_count: 0,
      articles_count: 0,
      created_at: null,
    });

    expect(api.categories.delete).toHaveBeenCalledWith(1);
    expect(deps.invalidateQueries).toHaveBeenCalledWith({ queryKey: ["articles"] });

    vi.resetModules();
    const departmentEntity = createEntity();
    const departmentApi = createApi();
    const departmentDeps = mockHookDeps(departmentEntity, { api: departmentApi });
    const { useDepartments } = await import("@/shared/hooks/use-departments");

    renderHook(() => useDepartments());
    config = departmentDeps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ name: "HR" });
    config.updateFn(2, { name: "People" });
    config.deleteFn(2);

    expect(departmentApi.departments.delete).toHaveBeenCalledWith(2);
  });

  it("toggles dialogues and resets edit state", async () => {
    const entity = createEntity({ selectedItem: { id: 2 } });
    const api = createApi();
    api.dialogues.update
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: false, error: { message: "failed" } });
    const deps = mockHookDeps(entity, {
      api,
      queryData: [
        {
          success: true,
          data: {
            steps: [
              {
                id: 1,
                scenario_id: 2,
                step_number: 1,
                question: "Question",
                answer_type: "TEXT",
                options: null,
                answer_content: null,
                is_final: false,
              },
            ],
          },
        },
      ],
    });
    const { toast, invalidateQueries } = deps;
    const { useDialogues } = await import("@/shared/hooks/use-dialogues");

    const dialogue = {
      id: 2,
      title: "Scenario",
      description: "",
      keywords: ["hr"],
      category: "VACATION",
      isActive: true,
      displayOrder: 1,
      stepsCount: 0,
      createdAt: "2024-01-01",
    };
    const { result } = renderHook(() => useDialogues());
    const config = deps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ title: "Scenario" });
    config.updateFn(2, { title: "Scenario" });
    config.deleteFn(2);
    config.mapItem({
      id: 2,
      title: "Scenario",
      description: null,
      keywords: [],
      category: "VACATION",
      is_active: true,
      display_order: 1,
      steps: [],
      created_at: null,
    });
    await act(async () => {
      await result.current.handleToggleActive(2, false);
      await result.current.handleToggleActive(2, true);
    });
    act(() => {
      result.current.setCategoryFilter("VACATION");
      result.current.openEdit(dialogue as never);
      result.current.resetForm();
    });

    expect(api.dialogues.update).toHaveBeenCalledWith(2, { is_active: false });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["dialogues"] });
    expect(toast).toHaveBeenCalledWith("dialogues.updateError", "error");
    expect(entity.setFilterValue).toHaveBeenCalledWith("category", "VACATION");
    expect(entity.setFormData).toHaveBeenCalledWith(expect.objectContaining({ title: "Scenario" }));
    for (const [updater] of entity.setExtendedState.mock.calls) {
      updater({ selectedSteps: [{ id: 99 }] });
    }
    expect(entity.setIsEditDialogOpen).toHaveBeenCalledWith(true);
    expect(entity.resetForm).toHaveBeenCalled();
    expect(result.current.selectedSteps).toEqual([
      expect.objectContaining({ id: 1, scenario_id: 2, question: "Question" }),
    ]);
  });

  it("publishes templates and opens edit dialog with fetched tasks", async () => {
    const entity = createEntity({ extendedState: { tasks: undefined } });
    const api = createApi();
    api.templates.publish
      .mockResolvedValueOnce({ success: true })
      .mockResolvedValueOnce({ success: false });
    api.templates.get.mockResolvedValue({
      success: true,
      data: { tasks: [{ id: 1, title: "Read handbook" }] },
    });
    const deps = mockHookDeps(entity, { api, queryData: [[{ id: 5, name: "Engineering" }]] });
    const { useTemplates } = await import("@/shared/hooks/use-templates");

    const template = {
      id: 6,
      name: "Template",
      description: "",
      department_id: 5,
      department: "Engineering",
      position: "",
      durationDays: 30,
      taskCount: 1,
      status: "DRAFT",
      isDefault: false,
    };
    const { result } = renderHook(() => useTemplates());
    const config = deps.getEntityConfig();
    config.listFn({ page: 1 });
    config.createFn({ name: "Template" });
    config.updateFn(6, { name: "Template" });
    config.deleteFn(6);
    config.mapItem({
      id: 6,
      name: "Template",
      description: null,
      department_id: 5,
      department: null,
      position: null,
      duration_days: 30,
      status: "DRAFT",
      is_default: false,
      task_categories: [],
    });
    await act(async () => {
      await result.current.handlePublish(6);
      await result.current.handlePublish(6);
      await result.current.handleDelete(6);
      await result.current.openEditDialog(template);
    });
    act(() => {
      result.current.setTasks([{ id: 2, title: "Meet mentor" } as never]);
      result.current.resetForm();
    });

    expect(api.templates.publish).toHaveBeenCalledWith(6);
    expect(entity.invalidate).toHaveBeenCalledTimes(1);
    expect(api.templates.get).toHaveBeenCalledWith(6);
    expect(entity.setSelectedItem).toHaveBeenCalledWith(template);
    expect(entity.setExtendedState).toHaveBeenCalledWith(expect.any(Function));
    for (const [updater] of entity.setExtendedState.mock.calls) {
      updater({ tasks: [] });
    }
    expect(entity.setIsEditDialogOpen).toHaveBeenCalledWith(true);
    expect(entity.resetForm).toHaveBeenCalled();
  });

  it("opens template edit dialog when task fetch fails", async () => {
    const entity = createEntity({ extendedState: { tasks: [] } });
    const api = createApi();
    api.templates.get.mockRejectedValue(new Error("offline"));
    mockHookDeps(entity, { api, queryData: [[]] });
    const { useTemplates } = await import("@/shared/hooks/use-templates");

    const { result } = renderHook(() => useTemplates());
    await act(async () => {
      await result.current.openEditDialog({
        id: 6,
        name: "Template",
        description: "",
        department_id: null,
        department: "",
        position: "",
        durationDays: 30,
        taskCount: 0,
        status: "DRAFT",
        isDefault: false,
      });
    });

    expect(api.templates.get).toHaveBeenCalledWith(6);
    for (const [updater] of entity.setExtendedState.mock.calls) {
      updater({ tasks: [] });
    }
    expect(entity.setIsEditDialogOpen).toHaveBeenCalledWith(true);
  });
});
