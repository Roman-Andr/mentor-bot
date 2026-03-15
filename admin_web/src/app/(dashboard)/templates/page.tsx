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
  FileText,
  Calendar,
  Users,
  CheckCircle,
  Trash2,
  GripVertical,
} from "lucide-react";
import { api, Template } from "@/lib/api";

interface Task {
  id: number;
  name: string;
  description: string;
  category: string;
  deadline_days: number;
  order: number;
}

interface TemplateFormData {
  name: string;
  description: string;
  department: string;
  position: string;
  duration_days: number;
  status: string;
  is_default: boolean;
}

interface TemplateItem {
  id: number;
  name: string;
  description: string;
  department: string;
  position: string;
  durationDays: number;
  taskCount: number;
  status: string;
  isDefault: boolean;
}

const mockTemplates: TemplateItem[] = [
  {
    id: 1,
    name: "Базовый онбординг разработчика",
    description: "Стандартный набор задач для новых разработчиков",
    department: "Разработка",
    position: "Developer",
    durationDays: 30,
    taskCount: 15,
    status: "ACTIVE",
    isDefault: true,
  },
  {
    id: 2,
    name: "Онбординг дизайнера",
    description: "Процесс адаптации для дизайнеров всех уровней",
    department: "Дизайн",
    position: "Designer",
    durationDays: 21,
    taskCount: 12,
    status: "ACTIVE",
    isDefault: false,
  },
  {
    id: 3,
    name: "Онбординг QA инженера",
    description: "Процесс адаптации для специалистов по тестированию",
    department: "QA",
    position: "QA Engineer",
    durationDays: 14,
    taskCount: 10,
    status: "ACTIVE",
    isDefault: false,
  },
  {
    id: 4,
    name: "Онбординг менеджера",
    description: "Процесс адаптации для менеджеров проектов",
    department: "Менеджмент",
    position: "Manager",
    durationDays: 14,
    taskCount: 8,
    status: "DRAFT",
    isDefault: false,
  },
  {
    id: 5,
    name: "Онбординг маркетолога",
    description: "Процесс адаптации для специалистов маркетинга",
    department: "Маркетинг",
    position: "Marketing",
    durationDays: 10,
    taskCount: 8,
    status: "INACTIVE",
    isDefault: false,
  },
];

const statuses = [
  { value: "ALL", label: "Все статусы" },
  { value: "ACTIVE", label: "Активен" },
  { value: "DRAFT", label: "Черновик" },
  { value: "INACTIVE", label: "Неактивен" },
];

const taskCategories = [
  "Документы",
  "Знакомство с командой",
  "Техническая настройка",
  "Обучение",
  "Безопасность",
  "Прочее",
];

const departments = [
  "Разработка",
  "Дизайн",
  "QA",
  "Менеджмент",
  "Маркетинг",
  "HR",
  "Бухгалтерия",
];

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(
    null,
  );
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    department: "",
    position: "",
    duration_days: 30,
    status: "DRAFT",
    is_default: false,
  });
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTask, setNewTask] = useState({
    name: "",
    description: "",
    category: "Документы",
    deadline_days: 3,
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  async function loadTemplates() {
    setLoading(true);
    try {
      const response = await api.templates.list();
      if (response.data) {
        setTemplates(
          response.data.map((t) => ({
            id: t.id,
            name: t.name,
            description: t.description || "",
            department: t.department || "",
            position: t.position || "",
            durationDays: t.duration_days,
            taskCount: 0,
            status: t.status,
            isDefault: t.is_default,
          })),
        );
      }
    } catch (err) {
      console.error("Failed to load templates:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleCreateTemplate = async () => {
    try {
      const response = await api.templates.create({
        name: formData.name,
        description: formData.description,
        department: formData.department || null,
        position: formData.position || null,
        level: null,
        duration_days: formData.duration_days,
        task_categories: [],
        status: (formData.status || "DRAFT") as "DRAFT" | "ACTIVE" | "INACTIVE",
      });

      if (response.data) {
        setTemplates([
          ...templates,
          {
            id: response.data.id,
            name: response.data.name,
            description: response.data.description || "",
            department: response.data.department || "",
            position: response.data.position || "",
            durationDays: response.data.duration_days,
            taskCount: tasks.length,
            status: response.data.status,
            isDefault: response.data.is_default,
          },
        ]);
        setIsCreateDialogOpen(false);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to create template:", err);
    }
  };

  const handleUpdateTemplate = async () => {
    if (!selectedTemplate) return;
    try {
      const response = await api.templates.update(selectedTemplate.id, {
        name: formData.name,
        description: formData.description,
        status: (formData.status || "DRAFT") as "DRAFT" | "ACTIVE" | "INACTIVE",
        is_default: formData.is_default,
      });

      if (response.data) {
        setTemplates(
          templates.map((t) => {
            if (t.id === selectedTemplate.id) {
              return {
                id: response.data!.id,
                name: response.data!.name,
                description: response.data!.description || "",
                department: response.data!.department || "",
                position: response.data!.position || "",
                durationDays: response.data!.duration_days,
                taskCount: tasks.length,
                status: response.data!.status,
                isDefault: response.data!.is_default,
              };
            }
            return t;
          }),
        );
        setIsEditDialogOpen(false);
        setSelectedTemplate(null);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to update template:", err);
    }
  };

  const handleDeleteTemplate = async (id: number) => {
    if (!confirm("Вы уверены, что хотите удалить этот шаблон?")) return;
    try {
      await api.templates.delete(id);
      setTemplates(templates.filter((t) => t.id !== id));
    } catch (err) {
      console.error("Failed to delete template:", err);
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      department: "",
      position: "",
      duration_days: 30,
      status: "DRAFT",
      is_default: false,
    });
    setTasks([]);
    setNewTask({
      name: "",
      description: "",
      category: "Документы",
      deadline_days: 3,
    });
  };

  const openEditDialog = (template: TemplateItem) => {
    setSelectedTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      department: template.department,
      position: template.position,
      duration_days: template.durationDays,
      status: template.status,
      is_default: template.isDefault,
    });
    setTasks([
      {
        id: 1,
        name: "Оформить документы",
        description: "Подписать трудовой договор",
        category: "Документы",
        deadline_days: 1,
        order: 1,
      },
      {
        id: 2,
        name: "Получить пропуск",
        description: "Оформить пропуск в офис",
        category: "Документы",
        deadline_days: 2,
        order: 2,
      },
    ]);
    setIsEditDialogOpen(true);
  };

  const addTask = () => {
    if (!newTask.name.trim()) return;
    const task: Task = {
      id: Date.now(),
      ...newTask,
      order: tasks.length + 1,
    };
    setTasks([...tasks, task]);
    setNewTask({
      name: "",
      description: "",
      category: "Документы",
      deadline_days: 3,
    });
  };

  const removeTask = (id: number) => {
    setTasks(tasks.filter((t) => t.id !== id));
  };

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (template.description || "")
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "ALL" || template.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return "bg-green-100 text-green-800";
      case "DRAFT":
        return "bg-yellow-100 text-yellow-800";
      case "INACTIVE":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Шаблоны чек-листов
          </h1>
          <p className="text-gray-500">Управление шаблонами онбординга</p>
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
              Создать шаблон
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Создание шаблона</DialogTitle>
              <DialogDescription>
                Создайте новый шаблон чек-листа для онбординга
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Название *</label>
                <Input
                  placeholder="Например: Базовый онбординг разработчика"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Описание</label>
                <Textarea
                  placeholder="Краткое описание шаблона"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium">Отдел</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                    value={formData.department}
                    onChange={(e) =>
                      setFormData({ ...formData, department: e.target.value })
                    }
                  >
                    <option value="">Выберите отдел</option>
                    {departments.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </select>
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
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium">
                    Длительность (дней)
                  </label>
                  <Input
                    type="number"
                    min={1}
                    value={formData.duration_days}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        duration_days: parseInt(e.target.value) || 30,
                      })
                    }
                  />
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
                    <option value="ACTIVE">Активен</option>
                    <option value="INACTIVE">Неактивен</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isDefault"
                  checked={formData.is_default}
                  onChange={(e) =>
                    setFormData({ ...formData, is_default: e.target.checked })
                  }
                  className="rounded border-gray-300"
                />
                <label htmlFor="isDefault" className="text-sm">
                  По умолчанию
                </label>
              </div>

              <div className="border-t pt-4 mt-4">
                <h3 className="font-medium mb-3">Задачи шаблона</h3>
                <div className="grid gap-3 mb-4">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
                    >
                      <GripVertical className="w-4 h-4 text-gray-400 mt-1" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">{task.name}</p>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => removeTask(task.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                        <p className="text-xs text-gray-500">
                          {task.description}
                        </p>
                        <div className="flex gap-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            {task.category}
                          </Badge>
                          <span className="text-xs text-gray-400">
                            {task.deadline_days} дн.
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-4 gap-2">
                  <Input
                    placeholder="Название задачи"
                    value={newTask.name}
                    onChange={(e) =>
                      setNewTask({ ...newTask, name: e.target.value })
                    }
                    className="col-span-2"
                  />
                  <select
                    className="flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                    value={newTask.category}
                    onChange={(e) =>
                      setNewTask({ ...newTask, category: e.target.value })
                    }
                  >
                    {taskCategories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                  <div className="flex gap-1">
                    <Input
                      type="number"
                      min={1}
                      placeholder="Дней"
                      value={newTask.deadline_days}
                      onChange={(e) =>
                        setNewTask({
                          ...newTask,
                          deadline_days: parseInt(e.target.value) || 1,
                        })
                      }
                      className="w-16"
                    />
                    <Button size="sm" onClick={addTask}>
                      +
                    </Button>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                Отмена
              </Button>
              <Button onClick={handleCreateTemplate} disabled={!formData.name}>
                Создать
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Редактирование шаблона</DialogTitle>
              <DialogDescription>Измените шаблон чек-листа</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Название *</label>
                <Input
                  placeholder="Название шаблона"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Описание</label>
                <Textarea
                  placeholder="Описание шаблона"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium">Отдел</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                    value={formData.department}
                    onChange={(e) =>
                      setFormData({ ...formData, department: e.target.value })
                    }
                  >
                    <option value="">Выберите отдел</option>
                    {departments.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium">Должность</label>
                  <Input
                    placeholder="Должность"
                    value={formData.position}
                    onChange={(e) =>
                      setFormData({ ...formData, position: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium">
                    Длительность (дней)
                  </label>
                  <Input
                    type="number"
                    min={1}
                    value={formData.duration_days}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        duration_days: parseInt(e.target.value) || 30,
                      })
                    }
                  />
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
                    <option value="ACTIVE">Активен</option>
                    <option value="INACTIVE">Неактивен</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isDefaultEdit"
                  checked={formData.is_default}
                  onChange={(e) =>
                    setFormData({ ...formData, is_default: e.target.checked })
                  }
                  className="rounded border-gray-300"
                />
                <label htmlFor="isDefaultEdit" className="text-sm">
                  По умолчанию
                </label>
              </div>

              <div className="border-t pt-4 mt-4">
                <h3 className="font-medium mb-3">Задачи шаблона</h3>
                <div className="grid gap-3 mb-4">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
                    >
                      <GripVertical className="w-4 h-4 text-gray-400 mt-1" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">{task.name}</p>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => removeTask(task.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                        <p className="text-xs text-gray-500">
                          {task.description}
                        </p>
                        <div className="flex gap-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            {task.category}
                          </Badge>
                          <span className="text-xs text-gray-400">
                            {task.deadline_days} дн.
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-4 gap-2">
                  <Input
                    placeholder="Название задачи"
                    value={newTask.name}
                    onChange={(e) =>
                      setNewTask({ ...newTask, name: e.target.value })
                    }
                    className="col-span-2"
                  />
                  <select
                    className="flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                    value={newTask.category}
                    onChange={(e) =>
                      setNewTask({ ...newTask, category: e.target.value })
                    }
                  >
                    {taskCategories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                  <div className="flex gap-1">
                    <Input
                      type="number"
                      min={1}
                      placeholder="Дней"
                      value={newTask.deadline_days}
                      onChange={(e) =>
                        setNewTask({
                          ...newTask,
                          deadline_days: parseInt(e.target.value) || 1,
                        })
                      }
                      className="w-16"
                    />
                    <Button size="sm" onClick={addTask}>
                      +
                    </Button>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditDialogOpen(false);
                  setSelectedTemplate(null);
                }}
              >
                Отмена
              </Button>
              <Button onClick={handleUpdateTemplate} disabled={!formData.name}>
                Сохранить
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Всего шаблонов</p>
                <p className="text-2xl font-bold">{mockTemplates.length}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Активных</p>
                <p className="text-2xl font-bold">
                  {mockTemplates.filter((t) => t.status === "ACTIVE").length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Черновиков</p>
                <p className="text-2xl font-bold">
                  {mockTemplates.filter((t) => t.status === "DRAFT").length}
                </p>
              </div>
              <FileText className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">По умолчанию</p>
                <p className="text-2xl font-bold">
                  {mockTemplates.filter((t) => t.isDefault).length}
                </p>
              </div>
              <Users className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Шаблоны</CardTitle>
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Отдел</TableHead>
                <TableHead>Должность</TableHead>
                <TableHead>Дней</TableHead>
                <TableHead>Задач</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead className="w-[100px]">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTemplates.map((template) => (
                <TableRow
                  key={template.id}
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => openEditDialog(template)}
                >
                  <TableCell>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{template.name}</p>
                        {template.isDefault && (
                          <Badge variant="secondary" className="text-xs">
                            По умолч.
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">
                        {template.description}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>{template.department}</TableCell>
                  <TableCell>{template.position}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      {template.durationDays}
                    </div>
                  </TableCell>
                  <TableCell>{template.taskCount}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        template.status,
                      )}`}
                    >
                      {statuses.find((s) => s.value === template.status)
                        ?.label || template.status}
                    </span>
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEditDialog(template)}
                      >
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-500"
                        onClick={() => handleDeleteTemplate(template.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
