import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "./use-debounce";
import { useConfirm } from "@/hooks/use-confirm";
import { useTranslations } from "@/hooks/use-translations";

interface CrudOptions<TItem, TForm> {
  defaultForm: TForm;
  mapItem: (apiItem: unknown) => TItem;
  api: {
    list: (params?: Record<string, unknown>) => Promise<{
      data?: { total?: number; pages?: number; [key: string]: unknown } | null;
      error?: string;
    }>;
    create?: (data: unknown) => Promise<{ data?: unknown; error?: string }>;
    update?: (id: number, data: unknown) => Promise<{ data?: unknown; error?: string }>;
    delete?: (id: number) => Promise<{ data?: unknown; error?: string }>;
  };
  listKey?: string;
  pageSize?: number;
  confirmDelete?: string;
}

interface UseCrudResult<TItem, TForm> {
  items: TItem[];
  loading: boolean;
  currentPage: number;
  setCurrentPage: (page: number | ((prev: number) => number)) => void;
  totalPages: number;
  totalCount: number;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  debouncedSearch: string;
  statusFilter: string;
  setStatusFilter: (status: string) => void;
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;
  selectedItem: TItem | null;
  setSelectedItem: (item: TItem | null) => void;
  formData: TForm;
  setFormData: (data: TForm) => void;
  loadItems: () => Promise<void>;
  handleCreate: (toPayload: (form: TForm) => unknown) => Promise<void>;
  handleUpdate: (toPayload: (form: TForm) => unknown) => Promise<void>;
  handleDelete: (id: number) => Promise<void>;
  openEditDialog: (item: TItem, toForm: (item: TItem) => TForm) => void;
  resetForm: () => void;
}

export function useCrud<TItem, TForm>(
  options: CrudOptions<TItem, TForm>,
): UseCrudResult<TItem, TForm> {
  const confirm = useConfirm();
  const t = useTranslations("common");
  const {
    defaultForm,
    mapItem,
    api: apiObj,
    listKey = "items",
    pageSize = 20,
    confirmDelete,
  } = options;

  const [items, setItems] = useState<TItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<TItem | null>(null);
  const [formData, setFormData] = useState<TForm>({ ...defaultForm });

  const debouncedSearch = useDebounce(searchQuery);

  const resetForm = useCallback(() => {
    setFormData({ ...defaultForm });
    setSelectedItem(null);
  }, [defaultForm]);

  const loadItems = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (debouncedSearch) params.search = debouncedSearch;
      if (pageSize > 0) {
        params.skip = (currentPage - 1) * pageSize;
        params.limit = pageSize;
      }

      const response = await apiObj.list(params);
      if (response.data) {
        const rawItems = (response.data as Record<string, unknown>)[listKey];
        if (Array.isArray(rawItems)) {
          setItems(rawItems.map(mapItem));
        }
        setTotalCount(response.data.total ?? 0);
        setTotalPages(response.data.pages ?? 1);
      }
    } catch (err) {
      console.error("Failed to load items:", err);
    } finally {
      setLoading(false);
    }
  }, [apiObj, listKey, mapItem, currentPage, statusFilter, debouncedSearch, pageSize]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const handleCreate = useCallback(
    async (toPayload: (form: TForm) => unknown) => {
      if (!apiObj.create) return;
      try {
        const response = await apiObj.create(toPayload(formData));
        if (response.data) {
          setItems((prev) => [mapItem(response.data), ...prev]);
          setTotalCount((c) => c + 1);
          setIsCreateDialogOpen(false);
          resetForm();
        }
      } catch (err) {
        console.error("Failed to create:", err);
      }
    },
    [apiObj, formData, mapItem, resetForm],
  );

  const handleUpdate = useCallback(
    async (toPayload: (form: TForm) => unknown) => {
      if (!selectedItem || !apiObj.update) return;
      try {
        const id = (selectedItem as Record<string, unknown>).id as number;
        const response = await apiObj.update(id, toPayload(formData));
        if (response.data) {
          setItems((prev) =>
            prev.map((item) => {
              const itemId = (item as Record<string, unknown>).id as number;
              return itemId === id ? mapItem(response.data) : item;
            }),
          );
          setIsEditDialogOpen(false);
          resetForm();
        }
      } catch (err) {
        console.error("Failed to update:", err);
      }
    },
    [apiObj, selectedItem, formData, mapItem, resetForm],
  );

  const handleDelete = useCallback(
    async (id: number) => {
      if (!apiObj.delete) return;
      if (
        !(await confirm({
          title: t("deleteTitle"),
          description: confirmDelete || t("confirmDelete"),
          variant: "destructive",
          confirmText: t("delete"),
        }))
      )
        return;
      try {
        await apiObj.delete(id);
        setItems((prev) => prev.filter((item) => (item as Record<string, unknown>).id !== id));
        setTotalCount((c) => c - 1);
      } catch (err) {
        console.error("Failed to delete:", err);
      }
    },
    [apiObj, confirm, confirmDelete, t],
  );

  const openEditDialog = useCallback((item: TItem, toForm: (item: TItem) => TForm) => {
    setSelectedItem(item);
    setFormData(toForm(item));
    setIsEditDialogOpen(true);
  }, []);

  return {
    items,
    loading,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    searchQuery,
    setSearchQuery,
    debouncedSearch,
    statusFilter,
    setStatusFilter,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedItem,
    setSelectedItem,
    formData,
    setFormData,
    loadItems,
    handleCreate,
    handleUpdate,
    handleDelete,
    openEditDialog,
    resetForm,
  };
}
