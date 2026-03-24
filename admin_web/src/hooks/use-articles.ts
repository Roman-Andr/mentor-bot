import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { api, attachmentsApi, type Article, type Category, type Attachment } from "@/lib/api";

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
    category: a.category_name || "Общее",
    status: a.status,
    isPinned: a.is_pinned,
    isFeatured: a.is_featured,
    viewCount: a.view_count,
    author: a.author_name,
    createdAt: a.created_at ? a.created_at.split("T")[0] : "",
  };
}

export function useArticles() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [articles, setArticles] = useState<ArticleRow[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
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
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const debouncedSearch = useDebounce(searchQuery);
  const pageSize = 20;

  const loadCategories = useCallback(async () => {
    try {
      const response = await api.categories.list();
      if (response.data?.categories) setCategories(response.data.categories);
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  }, []);

  const loadArticles = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (categoryFilter !== "ALL") params.category_id = parseInt(categoryFilter);
      if (debouncedSearch) params.search = debouncedSearch;
      params.skip = (currentPage - 1) * pageSize;
      params.limit = pageSize;

      const response = await api.articles.list(params);
      if (response.data) {
        setArticles(response.data.articles.map(mapArticle));
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages || 1);
      }
    } catch (err) {
      console.error("Failed to load articles:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, categoryFilter, debouncedSearch, currentPage]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

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

    try {
      if (selectedArticle) {
        const response = await api.articles.update(selectedArticle.id, payload);
        if (response.data) {
          setArticles(
            articles.map((a) => (a.id === selectedArticle.id ? mapArticle(response.data!) : a)),
          );

          if (pendingFiles.length > 0) {
            const attResponse = await attachmentsApi.uploadMultiple(response.data.id, pendingFiles);
            if (attResponse.data) {
              setAttachments(attResponse.data.attachments);
            }
            setPendingFiles([]);
          }

          setIsEditDialogOpen(false);
          setSelectedArticle(null);
          toast("Статья обновлена", "success");
        } else {
          toast(response.error || "Ошибка обновления", "error");
        }
      } else {
        const response = await api.articles.create(payload);
        if (response.data) {
          const newRow = mapArticle(response.data);
          setArticles([newRow, ...articles]);

          if (pendingFiles.length > 0) {
            const attResponse = await attachmentsApi.uploadMultiple(response.data.id, pendingFiles);
            if (attResponse.data) {
              setAttachments(attResponse.data.attachments);
            }
            setPendingFiles([]);
          } else {
            setAttachments([]);
          }

          setIsCreateDialogOpen(false);
          resetForm();
          toast("Статья создана", "success");
        } else {
          toast(response.error || "Ошибка создания", "error");
        }
      }
    } catch (err) {
      console.error("Failed to save article:", err);
      toast("Ошибка сохранения статьи", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление статьи", description: "Вы уверены, что хотите удалить эту статью?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.articles.delete(id);
      setArticles(articles.filter((a) => a.id !== id));
      toast("Статья удалена", "success");
    } catch (err) {
      console.error("Failed to delete article:", err);
      toast("Ошибка удаления статьи", "error");
    }
  };

  const handlePublish = async (id: number) => {
    try {
      const response = await api.articles.publish(id);
      if (response.data) {
        setArticles(articles.map((a) => (a.id === id ? { ...a, status: "PUBLISHED" } : a)));
        toast("Статья опубликована", "success");
      } else {
        toast(response.error || "Ошибка публикации", "error");
      }
    } catch (err) {
      console.error("Failed to publish article:", err);
      toast("Ошибка публикации статьи", "error");
    }
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
    loadArticles,
    loadCategories,
    handleSubmit,
    handleDelete,
    handlePublish,
    openEdit,
    resetForm,
  };
}
