"use client";

import { useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SearchInput } from "@/components/ui/search-input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { AsyncSearchableSelect, type SelectOption } from "@/components/ui/searchable-select";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Trash2, MoreHorizontal, Calendar, UserPlus, Users, X } from "lucide-react";
import { MEETING_TYPES } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { useMeetings } from "@/hooks/use-meetings";
import { useToast } from "@/components/ui/toast";
import { api, type User, type UserMeeting } from "@/lib/api";

export default function MeetingsPage() {
  const m = useMeetings();
  const { toast } = useToast();

  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);
  const [assignMeetingId, setAssignMeetingId] = useState<number | null>(null);
  const [assignMeetingTitle, setAssignMeetingTitle] = useState("");
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedUserLabel, setSelectedUserLabel] = useState("");
  const [assigning, setAssigning] = useState(false);

  const [isAssignmentsDialogOpen, setIsAssignmentsDialogOpen] = useState(false);
  const [assignmentsMeetingId, setAssignmentsMeetingId] = useState<number | null>(null);
  const [assignmentsMeetingTitle, setAssignmentsMeetingTitle] = useState("");
  const [assignments, setAssignments] = useState<UserMeeting[]>([]);
  const [assignmentsUsers, setAssignmentsUsers] = useState<Record<number, User>>({});
  const [assignmentsLoading, setAssignmentsLoading] = useState(false);

  const searchUsers = useCallback(async (query: string): Promise<SelectOption[]> => {
    const resp = await api.users.list({ search: query, limit: 20 });
    if (!resp.data) return [];
    return resp.data.users.map((u) => ({
      value: String(u.id),
      label: `${u.first_name} ${u.last_name || ""}`.trim(),
      description: u.email,
    }));
  }, []);

  const openAssignDialog = (meetingId: number, title: string) => {
    setAssignMeetingId(meetingId);
    setAssignMeetingTitle(title);
    setSelectedUserId("");
    setSelectedUserLabel("");
    setIsAssignDialogOpen(true);
  };

  const openAssignmentsDialog = async (meetingId: number, title: string) => {
    setAssignmentsMeetingId(meetingId);
    setAssignmentsMeetingTitle(title);
    setIsAssignmentsDialogOpen(true);
    setAssignmentsLoading(true);
    try {
      const resp = await api.userMeetings.listByMeeting(meetingId, { limit: 100 });
      if (resp.data) {
        setAssignments(resp.data.items);
        const userIds = [...new Set(resp.data.items.map((a) => a.user_id))];
        if (userIds.length > 0) {
          const usersResp = await api.users.list({ limit: 100 });
          if (usersResp.data) {
            const map: Record<number, User> = {};
            for (const u of usersResp.data.users) {
              if (userIds.includes(u.id)) map[u.id] = u;
            }
            setAssignmentsUsers(map);
          }
        }
      }
    } catch {
      toast("Ошибка загрузки назначенных пользователей", "error");
    } finally {
      setAssignmentsLoading(false);
    }
  };

  const handleRemoveAssignment = async (assignmentId: number) => {
    try {
      await api.userMeetings.delete(assignmentId);
      setAssignments((prev) => prev.filter((a) => a.id !== assignmentId));
      toast("Назначение удалено", "success");
    } catch {
      toast("Ошибка удаления назначения", "error");
    }
  };

  const handleAssign = async () => {
    if (!selectedUserId || !assignMeetingId) return;
    setAssigning(true);
    try {
      const resp = await api.userMeetings.assign({
        user_id: parseInt(selectedUserId),
        meeting_id: assignMeetingId,
      });
      if (resp.data) {
        toast("Встреча назначена", "success");
        setIsAssignDialogOpen(false);
      } else {
        toast(resp.error || "Ошибка назначения", "error");
      }
    } catch {
      toast("Ошибка назначения встречи", "error");
    } finally {
      setAssigning(false);
    }
  };

  return (
    <PageContent
      title="Встречи"
      subtitle="Управление шаблонами встреч для онбординга"
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            m.resetForm();
            m.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          Создать встречу
        </Button>
      }
    >
      <Dialog open={m.isCreateDialogOpen} onOpenChange={m.setIsCreateDialogOpen}>
        <MeetingFormDialog
          mode="create"
          formData={m.formData}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleCreate}
          onCancel={() => {
            m.setIsCreateDialogOpen(false);
            m.resetForm();
          }}
        />
      </Dialog>

      <Dialog open={m.isEditDialogOpen} onOpenChange={m.setIsEditDialogOpen}>
        <MeetingFormDialog
          mode="edit"
          formData={m.formData}
          onFormDataChange={m.setFormData}
          onSubmit={m.handleUpdate}
          onCancel={() => {
            m.setIsEditDialogOpen(false);
            m.setSelectedMeeting(null);
            m.resetForm();
          }}
        />
      </Dialog>

      <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
        <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Назначить встречу</DialogTitle>
            <DialogDescription>
              Назначить &quot;{assignMeetingTitle}&quot; пользователю
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Пользователь</label>
              <AsyncSearchableSelect
                value={selectedUserId}
                onChange={(v) => {
                  setSelectedUserId(v);
                  setSelectedUserLabel("");
                }}
                onSearch={searchUsers}
                selectedLabel={selectedUserLabel}
                placeholder="Выберите пользователя"
                searchPlaceholder="Поиск по имени или email..."
                minSearchLength={2}
                onOptionSelect={(opt) => setSelectedUserLabel(opt.label)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAssignDialogOpen(false)}>
              Отмена
            </Button>
            <Button onClick={handleAssign} disabled={!selectedUserId || assigning}>
              {assigning ? "Назначение..." : "Назначить"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isAssignmentsDialogOpen} onOpenChange={setIsAssignmentsDialogOpen}>
        <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Назначенные пользователи</DialogTitle>
            <DialogDescription>
              Пользователи, назначенные на &quot;{assignmentsMeetingTitle}&quot;
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {assignmentsLoading ? (
              <p className="text-muted-foreground text-sm">Загрузка...</p>
            ) : assignments.length === 0 ? (
              <p className="text-muted-foreground text-sm">Нет назначенных пользователей</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Пользователь</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Запланирована</TableHead>
                    <TableHead>Завершена</TableHead>
                    <TableHead className="w-[60px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {assignments.map((a) => {
                    const user = assignmentsUsers[a.user_id];
                    return (
                      <TableRow key={a.id}>
                        <TableCell>
                          {user ? (
                            <div>
                              <p className="font-medium">
                                {user.first_name} {user.last_name || ""}
                              </p>
                              <p className="text-muted-foreground text-xs">{user.email}</p>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">ID: {a.user_id}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <span className={
                            a.status === "COMPLETED"
                              ? "text-green-600"
                              : a.status === "SCHEDULED"
                                ? "text-blue-600"
                                 : "text-muted-foreground"
                          }>
                            {a.status}
                          </span>
                        </TableCell>
                        <TableCell>
                          {a.scheduled_at ? formatDate(a.scheduled_at) : "-"}
                        </TableCell>
                        <TableCell>
                          {a.completed_at ? formatDate(a.completed_at) : "-"}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-500"
                            onClick={() => handleRemoveAssignment(a.id)}
                          >
                            <X className="size-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAssignmentsDialogOpen(false)}>
              Закрыть
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <DataTable
        loading={m.loading}
        empty={m.meetings.length === 0}
        emptyMessage="Встречи не найдены"
        currentPage={m.currentPage}
        totalPages={m.totalPages}
        totalCount={m.totalCount}
        onPageChange={m.setCurrentPage}
        header={
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                Встречи{" "}
                <span className="text-muted-foreground text-sm font-normal">({m.totalCount})</span>
              </CardTitle>
              <div className="flex gap-2">
                <SearchInput value={m.searchQuery} onChange={m.setSearchQuery} />
                <Select
                  value={m.typeFilter}
                  onChange={(ev) => m.setTypeFilter(ev.target.value)}
                  options={MEETING_TYPES}
                />
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Название</TableHead>
              <TableHead>Тип</TableHead>
              <TableHead>Департамент</TableHead>
              <TableHead>Дедлайн</TableHead>
              <TableHead>Обязательная</TableHead>
              <TableHead>Порядок</TableHead>
              <TableHead>Создана</TableHead>
              <TableHead className="w-[180px]">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {m.meetings.map((meeting) => (
              <TableRow
                key={meeting.id}
                className="hover:bg-muted cursor-pointer"
                onClick={() => m.openEditDialog(meeting)}
              >
                <TableCell>
                  <div>
                    <p className="font-medium">{meeting.title}</p>
                    {meeting.description && (
                      <p className="text-muted-foreground line-clamp-1 max-w-64 text-sm">
                        {meeting.description}
                      </p>
                    )}
                  </div>
                </TableCell>
                <TableCell>{meeting.type}</TableCell>
                <TableCell>{meeting.department || "-"}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Calendar className="text-muted-foreground size-4" />
                    {meeting.deadlineDays} дн.
                  </div>
                </TableCell>
                <TableCell>
                  {meeting.isMandatory ? (
                    <span className="text-green-600">Да</span>
                  ) : (
                    <span className="text-muted-foreground">Нет</span>
                  )}
                </TableCell>
                <TableCell>{meeting.order}</TableCell>
                <TableCell>{formatDate(meeting.createdAt)}</TableCell>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Назначенные пользователи"
                      onClick={() => openAssignmentsDialog(meeting.id, meeting.title)}
                    >
                      <Users className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Назначить пользователю"
                      onClick={() => openAssignDialog(meeting.id, meeting.title)}
                    >
                      <UserPlus className="size-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => m.openEditDialog(meeting)}>
                      <MoreHorizontal className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500"
                      onClick={() => m.handleDelete(meeting.id)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}

interface MeetingFormDialogProps {
  mode: "create" | "edit";
  formData: {
    title: string;
    description: string;
    type: string;
    department_id: number;
    position: string;
    level: string;
    deadline_days: number;
    is_mandatory: boolean;
    order: number;
  };
  onFormDataChange: (data: MeetingFormDialogProps["formData"]) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

function MeetingFormDialog({
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
}: MeetingFormDialogProps) {
  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>
          {mode === "create" ? "Создание встречи" : "Редактирование встречи"}
        </DialogTitle>
        <DialogDescription>
          {mode === "create"
            ? "Создайте новый шаблон встречи"
            : "Измените параметры встречи"}
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Название</label>
          <input
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.title}
            onChange={(e) => onFormDataChange({ ...formData, title: e.target.value })}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Описание</label>
          <textarea
            className="w-full rounded-md border px-3 py-2 text-sm"
            rows={3}
            value={formData.description}
            onChange={(e) => onFormDataChange({ ...formData, description: e.target.value })}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Тип</label>
          <select
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.type}
            onChange={(e) => onFormDataChange({ ...formData, type: e.target.value })}
          >
            {MEETING_TYPES.filter((t) => t.value !== "ALL").map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Дедлайн (дней от начала)</label>
          <input
            type="number"
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.deadline_days}
            onChange={(e) =>
              onFormDataChange({ ...formData, deadline_days: parseInt(e.target.value) || 0 })
            }
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_mandatory"
            checked={formData.is_mandatory}
            onChange={(e) => onFormDataChange({ ...formData, is_mandatory: e.target.checked })}
          />
          <label htmlFor="is_mandatory" className="text-sm font-medium">
            Обязательная встреча
          </label>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Порядок</label>
          <input
            type="number"
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.order}
            onChange={(e) =>
              onFormDataChange({ ...formData, order: parseInt(e.target.value) || 0 })
            }
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Отмена
        </Button>
        <Button onClick={onSubmit}>
          {mode === "create" ? "Создать" : "Сохранить"}
        </Button>
      </DialogFooter>
    </DialogContent>
  );
}
