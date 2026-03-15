"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Search,
  Plus,
  MoreHorizontal,
  BookOpen,
  Eye,
  Tag,
  Pin,
  Star,
  Trash2,
} from "lucide-react";
import { api, Article, Category } from "@/lib/api";

const mockArticles = [
  {
    id: 1,
    title: "Оформление отпуска и отгулов",
    excerpt:
      "Полная инструкция по оформлению отпуска, отгулов и больничных листов",
    category: "HR",
    author: "Елена Козлова",
    status: "PUBLISHED",
    isPinned: true,
    isFeatured: false,
    viewCount: 1250,
    createdAt: "2026-01-15",
  },
  {
    id: 2,
    title: "Получение пропуска и доступа в офис",
    excerpt: "Процедура получения пропуска, IT-доступов и оборудования",
    category: "IT",
    author: "Михаил Иванов",
    status: "PUBLISHED",
    isPinned: true,
    isFeatured: true,
    viewCount: 980,
    createdAt: "2026-01-20",
  },
  {
    id: 3,
    title: "Корпоративные льготы и бенефиты",
    excerpt: "ДМС, спортивная компенсация, питание и другие льготы",
    category: "HR",
    author: "Елена Козлова",
    status: "PUBLISHED",
    isPinned: false,
    isFeatured: true,
    viewCount: 856,
    createdAt: "2026-02-01",
  },
  {
    id: 4,
    title: "Оргструктура и контакты",
    excerpt: "Руководство компании, отделы и ключевые контакты",
    category: "Общее",
    author: "Анна Сидорова",
    status: "PUBLISHED",
    isPinned: false,
    isFeatured: false,
    viewCount: 654,
    createdAt: "2026-02-10",
  },
  {
    id: 5,
    title: "Рабочее время и отчетность",
    excerpt: "Процесс сдачи рабочих отчетов, дедлайны и система учета времени",
    category: "HR",
    author: "Елена Козлова",
    status: "DRAFT",
    isPinned: false,
    isFeatured: false,
    viewCount: 0,
    createdAt: "2026-03-01",
  },
  {
    id: 6,
    title: "Правила безопасности и эвакуации",
    excerpt: "Инструкции по пожарной безопасности и действиям при эвакуации",
    category: "Безопасность",
    author: "Иван Петров",
    status: "PUBLISHED",
    isPinned: false,
    isFeatured: false,
    viewCount: 423,
    createdAt: "2026-02-15",
  },
];

const categories = [
  { value: "ALL", label: "Все категории" },
  { value: "HR", label: "HR" },
  { value: "IT", label: "IT" },
  { value: "Общее", label: "Общее" },
  { value: "Безопасность", label: "Безопасность" },
];

const statuses = [
  { value: "ALL", label: "Все статусы" },
  { value: "PUBLISHED", label: "Опубликовано" },
  { value: "DRAFT", label: "Черновик" },
];

export default function KnowledgePage() {
  const [articles, setArticles] = useState<typeof mockArticles>([]);
  const [categoriesList, setCategoriesList] = useState<Category[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<
    (typeof mockArticles)[0] | null
  >(null);
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    excerpt: "",
    category_id: 0,
    department: "",
    position: "",
    level: "",
    status: "DRAFT",
    is_pinned: false,
    is_featured: false,
    keywords: "",
  });

  useEffect(() => {
    loadCategories();
    loadArticles();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery || categoryFilter !== "ALL" || statusFilter !== "ALL") {
        loadArticles();
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, categoryFilter, statusFilter]);

  async function loadCategories() {
    try {
      const response = await api.categories.list();
      if (response.data?.categories) {
        setCategoriesList(response.data.categories);
      }
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  }

  async function loadArticles() {
    setLoading(true);
    try {
      const params: { status?: string; category_id?: number; search?: string } =
        {};
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (categoryFilter !== "ALL")
        params.category_id = parseInt(categoryFilter);
      if (searchQuery) params.search = searchQuery;

      const response = await api.articles.list(params);
      if (response.data) {
        setArticles(
          response.data.articles.map((a) => ({
            id: a.id,
            title: a.title,
            excerpt: a.excerpt || "",
            category: a.category_name || "Общее",
            author: a.author_name,
            status: a.status,
            isPinned: a.is_pinned,
            isFeatured: a.is_featured,
            viewCount: a.view_count,
            createdAt: a.created_at ? a.created_at.split("T")[0] : "",
          })),
        );
      }
    } catch (err) {
      console.error("Failed to load articles:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleCreateArticle = async () => {
    try {
      const keywordsArray = formData.keywords
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean);
      const response = await api.articles.create({
        title: formData.title,
        content: formData.content,
        excerpt: formData.excerpt || undefined,
        category_id: formData.category_id || null,
        department: formData.department || null,
        position: formData.position || null,
        level: formData.level || null,
        status: formData.status,
        is_pinned: formData.is_pinned,
        is_featured: formData.is_featured,
        keywords: keywordsArray,
      });

      if (response.data) {
        setArticles([
          {
            id: response.data.id,
            title: response.data.title,
            excerpt: response.data.excerpt || "",
            category: response.data.category_name || "Общее",
            author: response.data.author_name,
            status: response.data.status,
            isPinned: response.data.is_pinned,
            isFeatured: response.data.is_featured,
            viewCount: 0,
            createdAt: response.data.created_at.split("T")[0],
          },
          ...articles,
        ]);
        setIsCreateDialogOpen(false);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to create article:", err);
    }
  };

  const handleUpdateArticle = async () => {
    if (!selectedArticle) return;
    try {
      const keywordsArray = formData.keywords
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean);
      const response = await api.articles.update(selectedArticle.id, {
        title: formData.title,
        content: formData.content,
        excerpt: formData.excerpt || undefined,
        category_id: formData.category_id || null,
        department: formData.department || null,
        position: formData.position || null,
        level: formData.level || null,
        status: formData.status,
        is_pinned: formData.is_pinned,
        is_featured: formData.is_featured,
        keywords: keywordsArray,
      });

      if (response.data) {
        setArticles(
          articles.map((a) => {
            if (a.id === selectedArticle.id) {
              return {
                id: response.data!.id,
                title: response.data!.title,
                excerpt: response.data!.excerpt || "",
                category: response.data!.category_name || "Общее",
                author: response.data!.author_name,
                status: response.data!.status,
                isPinned: response.data!.is_pinned,
                isFeatured: response.data!.is_featured,
                viewCount: a.viewCount,
                createdAt: a.createdAt,
              };
            }
            return a;
          }),
        );
        setIsEditDialogOpen(false);
        setSelectedArticle(null);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to update article:", err);
    }
  };

  const handleDeleteArticle = async (id: number) => {
    if (!confirm("Вы уверены, что хотите удалить эту статью?")) return;
    try {
      await api.articles.delete(id);
      setArticles(articles.filter((a) => a.id !== id));
    } catch (err) {
      console.error("Failed to delete article:", err);
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      content: "",
      excerpt: "",
      category_id: 0,
      department: "",
      position: "",
      level: "",
      status: "DRAFT",
      is_pinned: false,
      is_featured: false,
      keywords: "",
    });
  };

  const openEditDialog = (article: (typeof mockArticles)[0]) => {
    setSelectedArticle(article);
    setFormData({
      title: article.title,
      content: "",
      excerpt: article.excerpt,
      category_id: 0,
      department: "",
      position: "",
      level: "",
      status: article.status,
      is_pinned: article.isPinned,
      is_featured: article.isFeatured,
      keywords: "",
    });
    setIsEditDialogOpen(true);
  };

  const filteredArticles = articles.filter((article) => {
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      categoryFilter === "ALL" || article.category === categoryFilter;
    const matchesStatus =
      statusFilter === "ALL" || article.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PUBLISHED":
        return "bg-green-100 text-green-800";
      case "DRAFT":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const renderArticleDialog = (isEdit: boolean) => (
    <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>
          {isEdit ? "Редактирование статьи" : "Создание статьи"}
        </DialogTitle>
        <DialogDescription>
          {isEdit
            ? "Измените статью в базе знаний"
            : "Создайте новую статью в базе знаний"}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">Заголовок *</label>
          <Input
            placeholder="Заголовок статьи"
            value={formData.title}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Краткое описание</label>
          <Textarea
            placeholder="Краткое описание для списка статей"
            value={formData.excerpt}
            onChange={(e) =>
              setFormData({ ...formData, excerpt: e.target.value })
            }
          />
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Содержание</label>
          <Textarea
            placeholder="Полный текст статьи (поддерживается Markdown)"
            value={formData.content}
            onChange={(e) =>
              setFormData({ ...formData, content: e.target.value })
            }
            className="min-h-[200px]"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Категория</label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.category_id}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  category_id: parseInt(e.target.value),
                })
              }
            >
              <option value={0}>Выберите категорию</option>
              {categoriesList.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
              {categories
                .filter((c) => c.value !== "ALL")
                .map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Статус</label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.status}
              onChange={(e) =>
                setFormData({ ...formData, status: e.target.value })
              }
            >
              <option value="DRAFT">Черновик</option>
              <option value="PUBLISHED">Опубликовано</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Отдел</label>
            <Input
              placeholder="Например: Разработка"
              value={formData.department}
              onChange={(e) =>
                setFormData({ ...formData, department: e.target.value })
              }
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Должность</label>
            <Input
              placeholder="Например: Developer"
              value={formData.position}
              onChange={(e) =>
                setFormData({ ...formData, position: e.target.value })
              }
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Уровень</label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.level}
              onChange={(e) =>
                setFormData({ ...formData, level: e.target.value })
              }
            >
              <option value="">Любой</option>
              <option value="Junior">Junior</option>
              <option value="Middle">Middle</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option>
            </select>
          </div>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium">Ключевые слова</label>
          <Input
            placeholder="Ключевые слова через запятую"
            value={formData.keywords}
            onChange={(e) =>
              setFormData({ ...formData, keywords: e.target.value })
            }
          />
        </div>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_pinned}
              onChange={(e) =>
                setFormData({ ...formData, is_pinned: e.target.checked })
              }
              className="rounded border-gray-300"
            />
            <span className="text-sm">Закрепить</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) =>
                setFormData({ ...formData, is_featured: e.target.checked })
              }
              className="rounded border-gray-300"
            />
            <span className="text-sm">Избранное</span>
          </label>
        </div>
      </div>
      <DialogFooter>
        <Button
          variant="outline"
          onClick={() => {
            setIsCreateDialogOpen(false);
            setIsEditDialogOpen(false);
            setSelectedArticle(null);
          }}
        >
          Отмена
        </Button>
        <Button
          onClick={isEdit ? handleUpdateArticle : handleCreateArticle}
          disabled={!formData.title}
        >
          {isEdit ? "Сохранить" : "Создать"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">База знаний</h1>
          <p className="text-gray-500">Управление статьями и FAQ</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button
              className="gap-2"
              onClick={() => {
                resetForm();
                setIsCreateDialogOpen(true);
              }}
            >
              <Plus className="w-4 h-4" />
              Создать статью
            </Button>
          </DialogTrigger>
          {renderArticleDialog(false)}
        </Dialog>

        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          {renderArticleDialog(true)}
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Всего статей</p>
                <p className="text-2xl font-bold">{mockArticles.length}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Опубликовано</p>
                <p className="text-2xl font-bold">
                  {mockArticles.filter((a) => a.status === "PUBLISHED").length}
                </p>
              </div>
              <Eye className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Закреплённых</p>
                <p className="text-2xl font-bold">
                  {mockArticles.filter((a) => a.isPinned).length}
                </p>
              </div>
              <Pin className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Избранных</p>
                <p className="text-2xl font-bold">
                  {mockArticles.filter((a) => a.isFeatured).length}
                </p>
              </div>
              <Star className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Статьи</CardTitle>
            <div className="flex gap-2">
              <div className="relative w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Поиск..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                {statuses.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Статья</TableHead>
                  <TableHead>Категория</TableHead>
                  <TableHead>Автор</TableHead>
                  <TableHead>Просмотры</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Дата</TableHead>
                  <TableHead className="w-[100px]">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredArticles.map((article) => (
                  <TableRow
                    key={article.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => openEditDialog(article)}
                  >
                    <TableCell>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{article.title}</p>
                          {article.isPinned && (
                            <Pin className="w-3 h-3 text-purple-500" />
                          )}
                          {article.isFeatured && (
                            <Star className="w-3 h-3 text-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-gray-500">
                          {article.excerpt}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{article.category}</Badge>
                    </TableCell>
                    <TableCell>{article.author}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4 text-gray-400" />
                        {article.viewCount}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                          article.status,
                        )}`}
                      >
                        {statuses.find((s) => s.value === article.status)
                          ?.label || article.status}
                      </span>
                    </TableCell>
                    <TableCell>
                      {new Date(article.createdAt).toLocaleDateString("ru-RU")}
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openEditDialog(article)}
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500"
                          onClick={() => handleDeleteArticle(article.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
