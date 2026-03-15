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
import { Label } from "@/components/ui/label";
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
  Mail,
  Phone,
  Building,
  UserPlus,
  Trash2,
} from "lucide-react";
import { api, User } from "@/lib/api";

const mockUsers = [
  {
    id: 1,
    name: "Иван Петров",
    email: "ivan.petrov@company.com",
    phone: "+7 (999) 123-45-67",
    department: "Разработка",
    position: "Backend Developer",
    role: "NEWBIE",
    status: "active",
    hireDate: "2026-03-01",
  },
  {
    id: 2,
    name: "Анна Сидорова",
    email: "anna.sidorova@company.com",
    phone: "+7 (999) 234-56-78",
    department: "Дизайн",
    position: "UI/UX Designer",
    role: "NEWBIE",
    status: "active",
    hireDate: "2026-02-15",
  },
  {
    id: 3,
    name: "Михаил Иванов",
    email: "mikhail.ivanov@company.com",
    phone: "+7 (999) 345-67-89",
    department: "QA",
    position: "QA Engineer",
    role: "MENTOR",
    status: "active",
    hireDate: "2025-06-10",
  },
  {
    id: 4,
    name: "Елена Козлова",
    email: "elena.kozlova@company.com",
    phone: "+7 (999) 456-78-90",
    department: "HR",
    position: "HR Manager",
    role: "HR",
    status: "active",
    hireDate: "2024-01-20",
  },
  {
    id: 5,
    name: "Сергей Смирнов",
    email: "sergey.smirnov@company.com",
    phone: null,
    department: "Разработка",
    position: "Frontend Developer",
    role: "NEWBIE",
    status: "pending",
    hireDate: "2026-03-10",
  },
];

const roles = [
  { value: "ALL", label: "Все роли" },
  { value: "ADMIN", label: "Администратор" },
  { value: "HR", label: "HR" },
  { value: "MENTOR", label: "Наставник" },
  { value: "NEWBIE", label: "Новичок" },
];

const departments = [
  { value: "ALL", label: "Все отделы" },
  { value: "Разработка", label: "Разработка" },
  { value: "Дизайн", label: "Дизайн" },
  { value: "QA", label: "QA" },
  { value: "HR", label: "HR" },
  { value: "Маркетинг", label: "Маркетинг" },
];

const roleOptions = [
  { value: "NEWBIE", label: "Новичок" },
  { value: "MENTOR", label: "Наставник" },
  { value: "HR", label: "HR" },
  { value: "ADMIN", label: "Администратор" },
];

const levelOptions = [
  { value: "", label: "Не указан" },
  { value: "Junior", label: "Junior" },
  { value: "Middle", label: "Middle" },
  { value: "Senior", label: "Senior" },
  { value: "Lead", label: "Lead" },
];

export default function UsersPage() {
  const [users, setUsers] = useState<typeof mockUsers>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<
    (typeof mockUsers)[0] | null
  >(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    employee_id: "",
    department: "",
    position: "",
    level: "",
    role: "NEWBIE",
    is_active: true,
    password: "",
  });

  useEffect(() => {
    loadUsers();
  }, [roleFilter, departmentFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        loadUsers();
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  async function loadUsers() {
    setLoading(true);
    try {
      const params: {
        role?: string;
        department?: string;
        search?: string;
        skip?: number;
        limit?: number;
      } = {};
      if (roleFilter !== "ALL") params.role = roleFilter;
      if (departmentFilter !== "ALL") params.department = departmentFilter;
      if (searchQuery) params.search = searchQuery;

      const response = await api.users.list(params);
      if (response.data) {
        setUsers(
          response.data.users.map((u) => ({
            id: u.id,
            name: `${u.first_name} ${u.last_name || ""}`.trim(),
            email: u.email,
            phone: u.phone,
            department: u.department || "",
            position: u.position || "",
            role: u.role,
            status: u.is_active ? "active" : "inactive",
            hireDate: u.hire_date || "",
          })),
        );
        setTotalUsers(response.data.total);
      }
    } catch (err) {
      console.error("Failed to load users:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleCreateUser = async () => {
    try {
      const response = await api.users.create({
        first_name: formData.first_name,
        last_name: formData.last_name || null,
        email: formData.email,
        phone: formData.phone || null,
        employee_id: formData.employee_id,
        department: formData.department || null,
        position: formData.position || null,
        level: formData.level || null,
        role: formData.role,
        is_active: formData.is_active,
        password: formData.password,
      });

      if (response.data) {
        setUsers([
          {
            id: response.data.id,
            name: `${response.data.first_name} ${response.data.last_name || ""}`.trim(),
            email: response.data.email,
            phone: response.data.phone,
            department: response.data.department || "",
            position: response.data.position || "",
            role: response.data.role,
            status: response.data.is_active ? "active" : "inactive",
            hireDate: response.data.hire_date || "",
          },
          ...users,
        ]);
        setIsCreateDialogOpen(false);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to create user:", err);
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    try {
      const nameParts = formData.first_name.split(" ");
      const response = await api.users.update(selectedUser.id, {
        first_name: formData.first_name,
        last_name: formData.last_name || null,
        email: formData.email,
        phone: formData.phone || null,
        employee_id: formData.employee_id,
        department: formData.department || null,
        position: formData.position || null,
        level: formData.level || null,
        role: formData.role,
        is_active: formData.is_active,
      });

      if (response.data) {
        setUsers(
          users.map((u) => {
            if (u.id === selectedUser.id) {
              return {
                id: response.data!.id,
                name: `${response.data!.first_name} ${response.data!.last_name || ""}`.trim(),
                email: response.data!.email,
                phone: response.data!.phone,
                department: response.data!.department || "",
                position: response.data!.position || "",
                role: response.data!.role,
                status: response.data!.is_active ? "active" : "inactive",
                hireDate: u.hireDate,
              };
            }
            return u;
          }),
        );
        setIsEditDialogOpen(false);
        setSelectedUser(null);
        resetForm();
      }
    } catch (err) {
      console.error("Failed to update user:", err);
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (!confirm("Вы уверены, что хотите удалить этого пользователя?")) return;
    try {
      await api.users.delete(id);
      setUsers(users.filter((u) => u.id !== id));
    } catch (err) {
      console.error("Failed to delete user:", err);
    }
  };

  const resetForm = () => {
    setFormData({
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      employee_id: "",
      department: "",
      position: "",
      level: "",
      role: "NEWBIE",
      is_active: true,
      password: "",
    });
  };

  const openEditDialog = (user: (typeof mockUsers)[0]) => {
    const nameParts = user.name.split(" ");
    setSelectedUser(user);
    setFormData({
      first_name: nameParts[0] || "",
      last_name: nameParts.slice(1).join(" ") || "",
      email: user.email,
      phone: user.phone || "",
      employee_id: "",
      department: user.department,
      position: user.position,
      level: "",
      role: user.role,
      is_active: user.status === "active",
      password: "",
    });
    setIsEditDialogOpen(true);
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === "ALL" || user.role === roleFilter;
    const matchesDept =
      departmentFilter === "ALL" || user.department === departmentFilter;
    return matchesSearch && matchesRole && matchesDept;
  });

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "ADMIN":
        return "default";
      case "HR":
        return "secondary";
      case "MENTOR":
        return "default";
      default:
        return "outline";
    }
  };

  const renderUserDialog = (isEdit: boolean) => (
    <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>
          {isEdit ? "Редактирование пользователя" : "Добавление пользователя"}
        </DialogTitle>
        <DialogDescription>
          {isEdit
            ? "Измените данные пользователя"
            : "Добавьте нового пользователя в систему"}
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="firstName">Имя *</Label>
            <Input
              id="firstName"
              placeholder="Иван"
              value={formData.first_name}
              onChange={(e) =>
                setFormData({ ...formData, first_name: e.target.value })
              }
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="lastName">Фамилия</Label>
            <Input
              id="lastName"
              placeholder="Петров"
              value={formData.last_name}
              onChange={(e) =>
                setFormData({ ...formData, last_name: e.target.value })
              }
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            placeholder="ivan.petrov@company.com"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="phone">Телефон</Label>
          <Input
            id="phone"
            placeholder="+7 (999) 123-45-67"
            value={formData.phone}
            onChange={(e) =>
              setFormData({ ...formData, phone: e.target.value })
            }
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="employeeId">Табельный номер *</Label>
          <Input
            id="employeeId"
            placeholder="EMP-001"
            value={formData.employee_id}
            onChange={(e) =>
              setFormData({ ...formData, employee_id: e.target.value })
            }
          />
        </div>
        {!isEdit && (
          <div className="grid gap-2">
            <Label htmlFor="password">Пароль *</Label>
            <Input
              id="password"
              type="password"
              placeholder="Минимум 8 символов"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
            />
          </div>
        )}
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="department">Отдел</Label>
            <select
              id="department"
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.department}
              onChange={(e) =>
                setFormData({ ...formData, department: e.target.value })
              }
            >
              <option value="">Выберите отдел</option>
              {departments
                .filter((d) => d.value !== "ALL")
                .map((dept) => (
                  <option key={dept.value} value={dept.value}>
                    {dept.label}
                  </option>
                ))}
            </select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="position">Должность</Label>
            <Input
              id="position"
              placeholder="Backend Developer"
              value={formData.position}
              onChange={(e) =>
                setFormData({ ...formData, position: e.target.value })
              }
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="role">Роль</Label>
            <select
              id="role"
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.role}
              onChange={(e) =>
                setFormData({ ...formData, role: e.target.value })
              }
            >
              {roleOptions.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="level">Уровень</Label>
            <select
              id="level"
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={formData.level}
              onChange={(e) =>
                setFormData({ ...formData, level: e.target.value })
              }
            >
              {levelOptions.map((level) => (
                <option key={level.value} value={level.value}>
                  {level.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isActive"
            checked={formData.is_active}
            onChange={(e) =>
              setFormData({ ...formData, is_active: e.target.checked })
            }
            className="rounded border-gray-300"
          />
          <Label htmlFor="isActive">Активен</Label>
        </div>
      </div>
      <DialogFooter>
        <Button
          variant="outline"
          onClick={() => {
            setIsCreateDialogOpen(false);
            setIsEditDialogOpen(false);
            setSelectedUser(null);
          }}
        >
          Отмена
        </Button>
        <Button
          onClick={isEdit ? handleUpdateUser : handleCreateUser}
          disabled={
            !formData.first_name ||
            !formData.email ||
            (!isEdit && !formData.password)
          }
        >
          {isEdit ? "Сохранить" : "Добавить"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Пользователи</h1>
          <p className="text-gray-500">Управление пользователями системы</p>
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
              <UserPlus className="w-4 h-4" />
              Добавить пользователя
            </Button>
          </DialogTrigger>
          {renderUserDialog(false)}
        </Dialog>

        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          {renderUserDialog(true)}
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Поиск по имени или email..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              {roles.map((role) => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
            >
              {departments.map((dept) => (
                <option key={dept.value} value={dept.value}>
                  {dept.label}
                </option>
              ))}
            </select>
            <Button variant="outline">Сбросить</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Пользователь</TableHead>
                  <TableHead>Отдел</TableHead>
                  <TableHead>Должность</TableHead>
                  <TableHead>Роль</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Дата приёма</TableHead>
                  <TableHead className="w-[100px]">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow
                    key={user.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => openEditDialog(user)}
                  >
                    <TableCell>
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Building className="w-4 h-4 text-gray-400" />
                        {user.department}
                      </div>
                    </TableCell>
                    <TableCell>{user.position}</TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)}>
                        {roles.find((r) => r.value === user.role)?.label ||
                          user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          user.status === "active" ? "default" : "secondary"
                        }
                      >
                        {user.status === "active" ? "Активен" : "Ожидает"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {user.hireDate
                        ? new Date(user.hireDate).toLocaleDateString("ru-RU")
                        : "-"}
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openEditDialog(user)}
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500"
                          onClick={() => handleDeleteUser(user.id)}
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

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Показано {filteredUsers.length} из {totalUsers} пользователей
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Предыдущая
          </Button>
          <Button variant="outline" size="sm">
            Следующая
          </Button>
        </div>
      </div>
    </div>
  );
}
