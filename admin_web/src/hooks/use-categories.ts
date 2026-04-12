import { useCallback } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import type { Category } from "@/types";

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

const DEFAULT_FORM: CategoryFormData = {
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

function toCreatePayload(form: CategoryFormData) {
  return {
    name: form.name,
    slug: form.slug || slugify(form.name),
    description: form.description || null,
    parent_id: form.parent_id || null,
    order: form.order,
    department_id: form.department_id || null,
    position: form.position || null,
    level: form.level || null,
    icon: form.icon || null,
    color: form.color || null,
  };
}

function toUpdatePayload(form: CategoryFormData) {
  return {
    name: form.name,
    description: form.description || null,
    parent_id: form.parent_id || null,
    order: form.order,
    department_id: form.department_id || null,
    position: form.position || null,
    level: form.level || null,
    icon: form.icon || null,
    color: form.color || null,
  };
}

function toForm(item: CategoryRow): CategoryFormData {
  return {
    name: item.name,
    slug: item.slug,
    description: item.description,
    parent_id: item.parent_id || 0,
    order: item.order,
    department_id: item.department_id || 0,
    position: item.position,
    level: item.level,
    icon: item.icon,
    color: item.color,
  };
}

export function useCategories() {
  const entity = useEntity<CategoryRow, CategoryFormData>({
    entityName: "Категория",
    translationNamespace: "knowledge",
    queryKeyPrefix: "categories",
    listFn: (params) => api.categories.list({ ...params, include_tree: true }),
    listDataKey: "categories",
    createFn: (data) => api.categories.create(data),
    updateFn: (id, data) => api.categories.update(id, data),
    deleteFn: (id) => api.categories.delete(id),
    defaultForm: DEFAULT_FORM,
    mapItem: (item) => mapCategory(item as Category),
    toCreatePayload,
    toUpdatePayload,
    toForm,
    labels: {
      createdKey: "knowledge.categoryCreated",
      updatedKey: "knowledge.categoryUpdated",
      deletedKey: "knowledge.categoryDeleted",
      createErrorKey: "knowledge.categoryCreateError",
      updateErrorKey: "knowledge.categoryUpdateError",
      deleteErrorKey: "knowledge.categoryDeleteError",
    },
    searchable: true,
    searchParamName: "search",
    pageSize: 20,
  });

  // Custom updateFormField that auto-generates slug from name
  const updateFormField = useCallback((field: keyof CategoryFormData, value: string | number) => {
    entity.setFormData((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "name" && !prev.slug) {
        next.slug = slugify(String(value));
      }
      return next;
    });
  }, [entity]);

  return {
    ...entity,
    categories: entity.items,
    selectedCategory: entity.selectedItem,
    setSelectedCategory: entity.setSelectedItem,
    openEdit: entity.openEditDialog,
    updateFormField,
    // Ensure pagination props are available
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,
    totalCount: entity.totalCount,
    totalPages: entity.totalPages,
  };
}
