import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, type Category } from "@/lib/api";

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[а-яё]/g, (ch) => {
      const map: Record<string, string> = {
        а: "a", б: "b", в: "v", г: "g", д: "d", е: "e",ё: "e",
        ж: "zh", з: "z", и: "i", й: "y", к: "k", л: "l", м: "m",
        н: "n", о: "o", п: "p", р: "r", с: "s", т: "t", у: "u",
        ф: "f", х: "h", ц: "c", ч: "ch", ш: "sh", щ: "shch",
        ъ: "", ы: "y", э: "e", ю: "yu", я: "ya",
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

export function useCategories() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [categories, setCategories] = useState<CategoryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<CategoryRow | null>(null);
  const [formData, setFormData] = useState<CategoryFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  const debouncedSearch = useDebounce(searchQuery);

  const loadCategories = useCallback(async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * pageSize;
      const response = await api.categories.list({ skip, limit: pageSize });
      if (response.data) {
        let items = response.data.categories.map(mapCategory);
        if (debouncedSearch) {
          const q = debouncedSearch.toLowerCase();
          items = items.filter(
            (c) =>
              c.name.toLowerCase().includes(q) ||
              c.slug.toLowerCase().includes(q) ||
              c.description.toLowerCase().includes(q),
          );
        }
        setCategories(items);
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages || 1);
      }
    } catch (err) {
      console.error("Failed to load categories:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  const handleSubmit = async () => {
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

    try {
      if (selectedCategory) {
        const response = await api.categories.update(selectedCategory.id, payload);
        if (response.data) {
          setCategories(
            categories.map((c) =>
              c.id === selectedCategory.id ? mapCategory(response.data!) : c,
            ),
          );
          setIsEditDialogOpen(false);
          setSelectedCategory(null);
          toast("Категория обновлена", "success");
        } else {
          toast(response.error || "Ошибка обновления", "error");
        }
      } else {
        const response = await api.categories.create(payload);
        if (response.data) {
          setCategories([mapCategory(response.data), ...categories]);
          setIsCreateDialogOpen(false);
          resetForm();
          toast("Категория создана", "success");
        } else {
          toast(response.error || "Ошибка создания", "error");
        }
      }
    } catch (err) {
      console.error("Failed to save category:", err);
      toast("Ошибка сохранения категории", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление категории", description: "Вы уверены, что хотите удалить эту категорию?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.categories.delete(id);
      setCategories(categories.filter((c) => c.id !== id));
      setTotalCount((prev) => prev - 1);
      toast("Категория удалена", "success");
    } catch (err) {
      console.error("Failed to delete category:", err);
      toast("Ошибка удаления категории", "error");
    }
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
    loadCategories,
    handleSubmit,
    handleDelete,
    openEdit,
    resetForm,
  };
}
