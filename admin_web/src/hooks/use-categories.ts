import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
import { useToast } from "@/components/ui/toast";
import { api, type Category } from "@/lib/api";

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[а-яё]/g, (ch) => {
      const map: Record<string, string> = {
        а: "a",
        б: "b",
        в: "v",
        г: "g",
        д: "d",
        е: "e",
        ё: "e",
        ж: "zh",
        з: "z",
        и: "i",
        й: "y",
        к: "k",
        л: "l",
        м: "m",
        н: "n",
        о: "o",
        п: "p",
        р: "r",
        с: "s",
        т: "t",
        у: "u",
        ф: "f",
        х: "h",
        ц: "c",
        ч: "ch",
        ш: "sh",
        щ: "shch",
        ъ: "",
        ы: "y",
        э: "e",
        ю: "yu",
        я: "ya",
      };
      return map[ch] || ch;
    })
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export interface CategoryRow {
  id: number;
  name: string;
  slug: string;
  description: string;
  parent_id: number | null;
  parent_name: string;
  order: number;
  department_id: number | null;
  department: string;
  position: string;
  level: string;
  icon: string;
  color: string;
  children_count: number;
  articles_count: number;
  createdAt: string;
}

export interface CategoryFormData {
  name: string;
  slug: string;
  description: string;
  parent_id: number;
  order: number;
  department_id: number;
  position: string;
  level: string;
  icon: string;
  color: string;
}

const EMPTY_FORM: CategoryFormData = {
  name: "",
  slug: "",
  description: "",
  parent_id: 0,
  order: 0,
  department_id: 0,
  position: "",
  level: "",
  icon: "",
  color: "",
};

function mapCategory(c: Category): CategoryRow {
  return {
    id: c.id,
    name: c.name,
    slug: c.slug,
    description: c.description || "",
    parent_id: c.parent_id,
    parent_name: c.parent_name || "",
    order: c.order,
    department_id: c.department_id,
    department: c.department?.name || "",
    position: c.position || "",
    level: c.level || "",
    icon: c.icon || "",
    color: c.color || "",
    children_count: c.children_count,
    articles_count: c.articles_count,
    createdAt: c.created_at ? c.created_at.split("T")[0] : "",
  };
}

const CATEGORIES_KEY = ["categories"] as const;

export function useCategories() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<CategoryRow | null>(null);
  const [formData, setFormData] = useState<CategoryFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  const debouncedSearch = useDebounce(searchQuery);

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(debouncedSearch && { search: debouncedSearch }),
  };

  const { data: categoriesData, isLoading: loading } = useQuery({
    queryKey: [...CATEGORIES_KEY, queryParams],
    queryFn: () => api.categories.list({ ...queryParams, include_tree: true }),
    select: (result) =>
      result.data
        ? {
            categories: result.data.categories.map(mapCategory),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.categories.create>[0]) => api.categories.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY });
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Категория создана", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения категории", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.categories.update>[1] }) =>
      api.categories.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY });
        setIsEditDialogOpen(false);
        setSelectedCategory(null);
        toast("Категория обновлена", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения категории", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.categories.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY });
        toast("Категория удалена", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления категории", "error"),
  });

  const handleSubmit = () => {
    const payload = {
      name: formData.name,
      slug: formData.slug || slugify(formData.name),
      description: formData.description || null,
      parent_id: formData.parent_id || null,
      order: formData.order,
      department_id: formData.department_id || null,
      position: formData.position || null,
      level: formData.level || null,
      icon: formData.icon || null,
      color: formData.color || null,
    };

    if (selectedCategory) {
      updateMutation.mutate({ id: selectedCategory.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const openEdit = (category: CategoryRow) => {
    setSelectedCategory(category);
    setFormData({
      name: category.name,
      slug: category.slug,
      description: category.description,
      parent_id: category.parent_id || 0,
      order: category.order,
      department_id: category.department_id || 0,
      position: category.position,
      level: category.level,
      icon: category.icon,
      color: category.color,
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setSelectedCategory(null);
  };

  const updateFormField = (field: keyof CategoryFormData, value: string | number) => {
    setFormData((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "name" && !prev.slug) {
        next.slug = slugify(String(value));
      }
      return next;
    });
  };

  const categories = categoriesData?.categories || [];
  const totalCount = categoriesData?.total || 0;
  const totalPages = categoriesData?.pages || 1;

  return {
    categories,
    loading,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedCategory,
    setSelectedCategory,
    formData,
    setFormData,
    updateFormField,
    searchQuery,
    setSearchQuery,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    pageSize,
    handleSubmit,
    handleDelete,
    openEdit,
    resetForm,
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
