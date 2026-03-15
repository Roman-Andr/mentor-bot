"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  Copy,
  CheckCircle,
  Clock,
  XCircle,
  Send,
  Trash2,
} from "lucide-react";
import { api, Invitation } from "@/lib/api";

const mockInvitations = [
  {
    id: 1,
    email: "alexey.volkov@company.com",
    role: "NEWBIE",
    department: "Разработка",
    status: "PENDING",
    createdAt: "2026-03-15",
    expiresAt: "2026-03-22",
    invitedBy: "Елена Козлова",
  },
  {
    id: 2,
    email: "olga.nikolaeva@company.com",
    role: "NEWBIE",
    department: "Дизайн",
    status: "ACCEPTED",
    createdAt: "2026-03-10",
    expiresAt: "2026-03-17",
    invitedBy: "Елена Козлова",
  },
  {
    id: 3,
    email: "dmitry.kuznetsov@company.com",
    role: "MENTOR",
    department: "Разработка",
    status: "PENDING",
    createdAt: "2026-03-14",
    expiresAt: "2026-03-21",
    invitedBy: "Анна Сидорова",
  },
  {
    id: 4,
    email: "natalia.sokolova@company.com",
    role: "NEWBIE",
    department: "QA",
    status: "EXPIRED",
    createdAt: "2026-03-01",
    expiresAt: "2026-03-08",
    invitedBy: "Елена Козлова",
  },
  {
    id: 5,
    email: "andrey.morozov@company.com",
    role: "NEWBIE",
    department: "Маркетинг",
    status: "PENDING",
    createdAt: "2026-03-16",
    expiresAt: "2026-03-23",
    invitedBy: "Михаил Иванов",
  },
];

const roles = [
  { value: "NEWBIE", label: "Новичок" },
  { value: "MENTOR", label: "Наставник" },
  { value: "HR", label: "HR" },
];

const departments = [
  { value: "ALL", label: "Все отделы" },
  { value: "Разработка", label: "Разработка" },
  { value: "Дизайн", label: "Дизайн" },
  { value: "QA", label: "QA" },
  { value: "Маркетинг", label: "Маркетинг" },
];

export default function InvitationsPage() {
  const [invitations, setInvitations] = useState<typeof mockInvitations>([]);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    accepted: 0,
    expired: 0,
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    role: "NEWBIE",
    employee_id: "",
    department: "",
    expires_in_days: 7,
  });

  useEffect(() => {
    loadInvitations();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        loadInvitations();
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  async function loadInvitations() {
    setLoading(true);
    try {
      const response = await api.invitations.list();
      if (response.data) {
        setInvitations(
          response.data.invitations.map((i) => ({
            id: i.id,
            email: i.email,
            role: i.role,
            department: i.department || "",
            status: i.status,
            createdAt: i.created_at ? i.created_at.split("T")[0] : "",
            expiresAt: i.expires_at ? i.expires_at.split("T")[0] : "",
            invitedBy: "Администратор",
          })),
        );
        if (response.data.stats) {
          setStats({
            total: response.data.stats.total,
            pending: response.data.stats.pending,
            accepted: response.data.stats.used || 0,
            expired: response.data.stats.expired,
          });
        }
      }
    } catch (err) {
      console.error("Failed to load invitations:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleCreateInvitation = async () => {
    try {
      const response = await api.invitations.create({
        email: formData.email,
        role: formData.role,
        employee_id: formData.employee_id || undefined,
        department: formData.department || undefined,
        expires_in_days: formData.expires_in_days,
      });

      if (response.data) {
        setInvitations([
          {
            id: response.data.id,
            email: response.data.email,
            role: response.data.role,
            department: response.data.department || "",
            status: response.data.status,
            createdAt: response.data.created_at
              ? response.data.created_at.split("T")[0]
              : "",
            expiresAt: response.data.expires_at
              ? response.data.expires_at.split("T")[0]
              : "",
            invitedBy: "Администратор",
          },
          ...invitations,
        ]);
        setIsCreateDialogOpen(false);
        setFormData({
          email: "",
          role: "NEWBIE",
          employee_id: "",
          department: "",
          expires_in_days: 7,
        });
      }
    } catch (err) {
      console.error("Failed to create invitation:", err);
    }
  };

  const handleDeleteInvitation = async (id: number) => {
    if (!confirm("Вы уверены, что хотите удалить это приглашение?")) return;
    try {
      await api.invitations.delete(id);
      setInvitations(invitations.filter((i) => i.id !== id));
    } catch (err) {
      console.error("Failed to delete invitation:", err);
    }
  };

  const filteredInvitations = invitations.filter((inv) =>
    inv.email.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "PENDING":
        return (
          <Badge className="gap-1 bg-yellow-100 text-yellow-700 hover:bg-yellow-100">
            <Clock className="w-3 h-3" />
            Ожидает
          </Badge>
        );
      case "ACCEPTED":
        return (
          <Badge className="gap-1 bg-green-100 text-green-700 hover:bg-green-100">
            <CheckCircle className="w-3 h-3" />
            Принято
          </Badge>
        );
      case "EXPIRED":
        return (
          <Badge className="gap-1 bg-red-100 text-red-700 hover:bg-red-100">
            <XCircle className="w-3 h-3" />
            Истёк
          </Badge>
        );
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const copyInviteLink = (token: string) => {
    navigator.clipboard.writeText(`https://bot.company.com/start/${token}`);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Приглашения</h1>
          <p className="text-gray-500">
            Управление приглашениями новых сотрудников
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button
              className="gap-2"
              onClick={() => setIsCreateDialogOpen(true)}
            >
              <Send className="w-4 h-4" />
              Создать приглашение
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Создать приглашение</DialogTitle>
              <DialogDescription>
                Отправьте приглашение новому сотруднику для регистрации в
                системе
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="employee@company.com"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                />
              </div>
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
                  {roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                Отмена
              </Button>
              <Button
                className="gap-2"
                onClick={handleCreateInvitation}
                disabled={!formData.email}
              >
                <Send className="w-4 h-4" />
                Отправить
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
                <p className="text-sm text-gray-500">Всего приглашений</p>
                <p className="text-2xl font-bold">{invitations.length}</p>
              </div>
              <Mail className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Ожидают</p>
                <p className="text-2xl font-bold">
                  {invitations.filter((i) => i.status === "PENDING").length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Принято</p>
                <p className="text-2xl font-bold">
                  {invitations.filter((i) => i.status === "ACCEPTED").length}
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
                <p className="text-sm text-gray-500">Истекло</p>
                <p className="text-2xl font-bold">
                  {invitations.filter((i) => i.status === "EXPIRED").length}
                </p>
              </div>
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Список приглашений</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Поиск по email..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
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
                  <TableHead>Email</TableHead>
                  <TableHead>Роль</TableHead>
                  <TableHead>Отдел</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Пригласил</TableHead>
                  <TableHead>Создано</TableHead>
                  <TableHead>Истекает</TableHead>
                  <TableHead className="w-[80px]">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInvitations.map((invitation) => (
                  <TableRow key={invitation.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{invitation.email}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {roles.find((r) => r.value === invitation.role)?.label}
                      </Badge>
                    </TableCell>
                    <TableCell>{invitation.department}</TableCell>
                    <TableCell>{getStatusBadge(invitation.status)}</TableCell>
                    <TableCell>{invitation.invitedBy}</TableCell>
                    <TableCell>
                      {new Date(invitation.createdAt).toLocaleDateString(
                        "ru-RU",
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(invitation.expiresAt).toLocaleDateString(
                        "ru-RU",
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-500"
                        onClick={() => handleDeleteInvitation(invitation.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
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
