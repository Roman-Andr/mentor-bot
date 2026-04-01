import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "@/hooks/useDebounce";
import { useToast } from "@/components/ui/toast";
import { api, attachmentsApi, type Article, type Attachment } from "@/lib/api";

export interface ArticleRow {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  category_id: number | null;
  category: string;
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

function mapArticle(a: Article): ArticleRow {
  return {
    id: a.id,
    title: a.title,
    slug: a.slug,
    content: a.content,
    excerpt: a.excerpt || "",
    category_id: a.category_id,
    category: a.category?.name || "Общее",
    status: a.status,
    isPinned: a.is_pinned,
    isFeatured: a.is_featured,
    viewCount: a.view_count,
    author: a.author_name,
    createdAt: a.created_at ? a.created_at.split("T")[0] : "",
  };
}

const ARTICLES_KEY = ["articles"] as const;
const CATEGORIES_KEY = ["categories"] as const;

export function useArticles() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<ArticleRow | null>(null);
  const [formData, setFormData] = useState<ArticleFormData>(EMPTY_FORM);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  const debouncedSearch = useDebounce(searchQuery);
  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(statusFilter !== "ALL" && { status: statusFilter }),
    ...(categoryFilter !== "ALL" && { category_id: parseInt(categoryFilter) }),
    ...(debouncedSearch && { search: debouncedSearch }),
  };

  const { data: articlesData, isLoading: loading } = useQuery({
    queryKey: [...ARTICLES_KEY, queryParams],
    queryFn: () => api.articles.list(queryParams),
    select: (result) =>
      result.data
        ? {
            articles: result.data.articles.map(mapArticle),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const { data: categoriesData } = useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: () => api.categories.list({ limit: 1000, include_tree: true }),
    select: (result) => result.data?.categories || [],
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.articles.create>[0]) => api.articles.create(data),
    onSuccess: async (result) => {
      if (result.data) {
        if (pendingFiles.length > 0) {
          await attachmentsApi.uploadMultiple(result.data.id, pendingFiles);
        }
        queryClient.invalidateQueries({ queryKey: ARTICLES_KEY });
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Статья создана", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения статьи", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.articles.update>[1] }) =>
      api.articles.update(id, data),
    onSuccess: async (result) => {
      if (result.data) {
        if (pendingFiles.length > 0) {
          await attachmentsApi.uploadMultiple(result.data.id, pendingFiles);
        }
        queryClient.invalidateQueries({ queryKey: ARTICLES_KEY });
        setIsEditDialogOpen(false);
        setSelectedArticle(null);
        toast("Статья обновлена", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка сохранения статьи", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.articles.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: ARTICLES_KEY });
        toast("Статья удалена", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления статьи", "error"),
  });

  const publishMutation = useMutation({
    mutationFn: (id: number) => api.articles.publish(id),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: ARTICLES_KEY });
        toast("Статья опубликована", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка публикации статьи", "error"),
  });

  const handleSubmit = async () => {
    const keywordsArray = formData.keywords
      .split(",")
      .map((k) => k.trim())
      .filter(Boolean);
    const payload = {
      title: formData.title,
      content: formData.content,
      excerpt: formData.excerpt || undefined,
      category_id: formData.category_id || null,
      department_id: formData.department_id || null,
      position: formData.position || null,
      level: formData.level || null,
      status: formData.status,
      is_pinned: formData.is_pinned,
      is_featured: formData.is_featured,
      keywords: keywordsArray,
    };

    if (selectedArticle) {
      updateMutation.mutate({ id: selectedArticle.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const handlePublish = (id: number) => {
    publishMutation.mutate(id);
  };

  const openEdit = async (article: ArticleRow) => {
    setSelectedArticle(article);
    setFormData({
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
    });
    setAttachments([]);
    setPendingFiles([]);
    const attResponse = await api.attachments.listByArticle(article.id);
    if (attResponse.data) {
      setAttachments(attResponse.data.attachments);
    }
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setSelectedArticle(null);
    setAttachments([]);
    setPendingFiles([]);
  };

  const articles = articlesData?.articles || [];
  const categories = categoriesData || [];
  const totalCount = articlesData?.total || 0;
  const totalPages = articlesData?.pages || 1;

  return {
    articles,
    categories,
    loading,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedArticle,
    setSelectedArticle,
    formData,
    setFormData,
    attachments,
    setAttachments,
    pendingFiles,
    setPendingFiles,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    categoryFilter,
    setCategoryFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    loadCategories: () => queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY }),
    handleSubmit,
    handleDelete,
    handlePublish,
    openEdit,
    resetForm,
    resetFilters: () => {
      setSearchQuery("");
      setStatusFilter("ALL");
      setCategoryFilter("ALL");
      setCurrentPage(1);
    },
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
