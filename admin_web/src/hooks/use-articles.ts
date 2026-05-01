import { useEffect } from "react";
import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import type { Article, Attachment } from "@/types";
import { useQuery } from "@tanstack/react-query";

export interface ArticleRow {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  category_id: number | null;
  category: string;
  category_color: string | null;
  status: string;
  isPinned: boolean;
  isFeatured: boolean;
  viewCount: number;
  author: string;
  createdAt: string;
}

export interface ArticleFormData {
  title: string;
  content: string;
  excerpt: string;
  category_id: number;
  department_id: number;
  position: string;
  level: string;
  status: string;
  is_pinned: boolean;
  is_featured: boolean;
  keywords: string;
}

interface ExtendedState {
  attachments: Attachment[];
  pendingFiles: File[];
}

const EMPTY_FORM: ArticleFormData = {
  title: "",
  content: "",
  excerpt: "",
  category_id: 0,
  department_id: 0,
  position: "",
  level: "",
  status: "DRAFT",
  is_pinned: false,
  is_featured: false,
  keywords: "",
};

const defaultExtendedState: ExtendedState = {
  attachments: [],
  pendingFiles: [],
};

function mapArticle(a: Article): ArticleRow {
  return {
    id: a.id,
    title: a.title,
    slug: a.slug,
    content: a.content,
    excerpt: a.excerpt || "",
    category_id: a.category_id,
    category: a.category?.name || "Общее",
    category_color: a.category?.color || null,
    status: a.status,
    isPinned: a.is_pinned,
    isFeatured: a.is_featured,
    viewCount: a.view_count,
    author: a.author_name,
    createdAt: a.created_at ? a.created_at.split("T")[0] : "",
  };
}

function toPayload(form: ArticleFormData) {
  const keywordsArray = form.keywords
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);

  return {
    title: form.title,
    content: form.content,
    excerpt: form.excerpt || undefined,
    category_id: form.category_id || null,
    department_id: form.department_id || null,
    position: form.position || null,
    level: form.level || null,
    status: form.status,
    is_pinned: form.is_pinned,
    is_featured: form.is_featured,
    keywords: keywordsArray,
  };
}

function toForm(article: ArticleRow): ArticleFormData {
  return {
    title: article.title,
    content: article.content,
    excerpt: article.excerpt,
    category_id: article.category_id || 0,
    department_id: 0,
    position: "",
    level: "",
    status: article.status,
    is_pinned: article.isPinned,
    is_featured: article.isFeatured,
    keywords: "",
  };
}

export function useArticles() {
  const entity = useEntity<ArticleRow, ArticleFormData, ReturnType<typeof toPayload>, ReturnType<typeof toPayload>, ExtendedState>({
    entityName: "Статья",
    translationNamespace: "knowledge",
    queryKeyPrefix: "articles",
    listFn: (params) => api.articles.list(params),
    listDataKey: "articles",
    createFn: async (data) => {
      const result = await api.articles.create(data);
      return result;
    },
    updateFn: (id, data) => api.articles.update(id, data),
    deleteFn: (id) => api.articles.delete(id),
    defaultForm: EMPTY_FORM,
    mapItem: (item: unknown) => mapArticle(item as Article),
    toCreatePayload: toPayload,
    toUpdatePayload: toPayload,
    toForm,
    searchable: true,
    searchParamName: "search",
    filters: [
      { name: "status", defaultValue: "ALL" },
      { name: "category", defaultValue: "ALL", paramName: "category_id", transform: (v) => parseInt(v) },
      { name: "pinned", defaultValue: "ALL", paramName: "pinned_only", transform: (v) => v === "true" },
    ],
    sortable: true,
    labels: {
      createdKey: "knowledge.articleCreated",
      updatedKey: "knowledge.articleUpdated",
      deletedKey: "knowledge.articleDeleted",
      createErrorKey: "knowledge.articleCreateError",
      updateErrorKey: "knowledge.articleUpdateError",
      deleteErrorKey: "knowledge.articleDeleteError",
    },
  });

  // Initialize attachments and pendingFiles state
  useEffect(() => {
    if (entity.extendedState.attachments === undefined) {
      entity.setExtendedState(() => ({ attachments: [], pendingFiles: [] }));
    }
  }, [entity]);

  // Fetch categories
  const { data: categoriesData, refetch: refetchCategories } = useQuery({
    queryKey: queryKeys.categories.all,
    queryFn: () => api.categories.list({ limit: 100, include_tree: true }),
    select: (result) => result.success ? result.data?.categories || [] : [],
  });

  // Custom openEdit that loads attachments
  const openEdit = async (article: ArticleRow) => {
    entity.setSelectedItem(article);
    entity.setFormData(toForm(article));

    // Load attachments
    const attResponse = await api.attachments.listByArticle(article.id);
    entity.setExtendedState((prev) => ({
      ...prev,
      attachments: (attResponse.success && attResponse.data?.attachments) || [],
      pendingFiles: [],
    }));

    entity.setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    entity.resetForm();
    entity.setExtendedState(() => defaultExtendedState);
  };

  const handleSubmit = async () => {
    const pendingFiles = entity.extendedState.pendingFiles ?? [];
    const articleId = entity.selectedItem?.id;

    // Call the original handleSubmit to create/update the article
    await entity.handleSubmit();

    // If there are pending files, upload them after the article is saved
    if (pendingFiles.length > 0) {
      const currentArticleId = articleId || entity.selectedItem?.id;
      if (currentArticleId) {
        const uploadResult = await api.attachments.uploadMultiple(currentArticleId, pendingFiles);
        if (uploadResult.success && uploadResult.data) {
          const { attachments: newAttachments } = uploadResult.data;
          entity.setExtendedState((prev) => ({
            ...prev,
            attachments: [...(prev.attachments || []), ...newAttachments],
            pendingFiles: [],
          }));
        }
      }
    }
  };

  return {
    // Data
    articles: entity.items,
    categories: categoriesData || [],
    loading: entity.loading,
    totalCount: entity.totalCount,
    totalPages: entity.totalPages,

    // Pagination
    currentPage: entity.currentPage,
    setCurrentPage: entity.setCurrentPage,
    pageSize: entity.pageSize,
    setPageSize: entity.setPageSize,

    // Search & Filters
    searchQuery: entity.searchQuery,
    setSearchQuery: entity.setSearchQuery,
    statusFilter: entity.filterValues.status ?? "ALL",
    setStatusFilter: (value: string) => entity.setFilterValue("status", value),
    categoryFilter: entity.filterValues.category ?? "ALL",
    setCategoryFilter: (value: string) => entity.setFilterValue("category", value),
    pinnedFilter: entity.filterValues.pinned ?? "ALL",
    setPinnedFilter: (value: string) => entity.setFilterValue("pinned", value),

    // Dialogs
    isCreateDialogOpen: entity.isCreateDialogOpen,
    setIsCreateDialogOpen: entity.setIsCreateDialogOpen,
    isEditDialogOpen: entity.isEditDialogOpen,
    setIsEditDialogOpen: entity.setIsEditDialogOpen,

    // Selection
    selectedArticle: entity.selectedItem,
    setSelectedArticle: entity.setSelectedItem,

    // Form
    formData: entity.formData,
    setFormData: entity.setFormData,

    // Attachments
    attachments: entity.extendedState.attachments ?? [],
    setAttachments: (attachments: Attachment[]) =>
      entity.setExtendedState((prev) => ({ ...prev, attachments })),
    pendingFiles: entity.extendedState.pendingFiles ?? [],
    setPendingFiles: (files: File[]) =>
      entity.setExtendedState((prev) => ({ ...prev, pendingFiles: files })),

    // Handlers
    handleSubmit,
    handleDelete: entity.handleDelete,
    handlePublish: (id: number) => api.articles.publish(id),
    openEdit,
    resetForm,
    resetFilters: entity.resetFilters,
    loadCategories: refetchCategories,

    // Loading states
    isSubmitting: entity.isSubmitting,
    isDeleting: entity.isDeleting,

    // Sorting
    sortField: entity.sortField,
    sortDirection: entity.sortDirection,
    toggleSort: entity.toggleSort,
  };
}

