"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Select } from "@/components/ui/select";
import { SearchableSelect, type SelectOption } from "@/components/ui/searchable-select";
import { Send } from "lucide-react";
import { ROLES, LEVELS } from "@/lib/constants";
import { useEffect, useState, useCallback } from "react";
import { api, type User } from "@/lib/api";

interface InvitationFormData {
  email: string;
  role: string;
  employee_id: string;
  department_id: number;
  position: string;
  level: string;
  mentor_id: number;
  expires_in_days: number;
}

interface CreateInvitationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  formData: InvitationFormData;
  onFormDataChange: (data: InvitationFormData) => void;
  emailTouched: boolean;
  onEmailTouchedChange: (touched: boolean) => void;
  departments?: { id: number; name: string }[];
  onSubmit: () => void;
  onCancel: () => void;
}

export function CreateInvitationDialog({
  open,
  onOpenChange,
  formData,
  onFormDataChange,
  emailTouched,
  onEmailTouchedChange,
  departments = [],
  onSubmit,
  onCancel,
}: CreateInvitationDialogProps) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isEmailValid = !formData.email || emailRegex.test(formData.email);
  const showEmailError = emailTouched && !isEmailValid;

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const loadMentors = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.users.list({ role: "MENTOR", limit: 100 });
      if (res.data) setUsers(res.data.users);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) loadMentors();
  }, [open, loadMentors]);

  const mentorOptions: SelectOption[] = users.map((u) => ({
    value: String(u.id),
    label: [u.first_name, u.last_name].filter(Boolean).join(" ") + ` (${u.email})`,
    description: [u.department, u.position].filter(Boolean).join(" · "),
  }));

  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        onOpenChange(open);
        if (!open) onEmailTouchedChange(false);
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Создать приглашение</DialogTitle>
          <DialogDescription>
            Отправьте приглашение новому сотруднику для регистрации в системе
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
              className={showEmailError ? "border-red-500 focus-visible:ring-red-500" : ""}
              onChange={(e) => onFormDataChange({ ...formData, email: e.target.value })}
              onBlur={() => onEmailTouchedChange(true)}
            />
            {showEmailError && <p className="text-sm text-red-500">Некорректный формат email</p>}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="employeeId">Табельный номер</Label>
            <Input
              id="employeeId"
              placeholder="EMP-001"
              value={formData.employee_id}
              onChange={(e) => onFormDataChange({ ...formData, employee_id: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="department">Отдел</Label>
            <Select
              id="department"
              options={departments.map((d) => ({ value: String(d.id), label: d.name }))}
              placeholder="Выберите отдел"
              value={formData.department_id}
              onChange={(e) => onFormDataChange({ ...formData, department_id: parseInt(e.target.value) || 0 })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="position">Должность</Label>
            <Input
              id="position"
              placeholder="Разработчик"
              value={formData.position}
              onChange={(e) => onFormDataChange({ ...formData, position: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="level">Уровень</Label>
            <Select
              id="level"
              options={[...LEVELS]}
              placeholder="Не указан"
              value={formData.level}
              onChange={(e) => onFormDataChange({ ...formData, level: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="role">Роль</Label>
            <Select
              id="role"
              options={ROLES}
              value={formData.role}
              onChange={(e) => onFormDataChange({ ...formData, role: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="mentor">Наставник</Label>
            <SearchableSelect
              options={mentorOptions}
              value={formData.mentor_id ? String(formData.mentor_id) : ""}
              onChange={(v) => onFormDataChange({ ...formData, mentor_id: v ? parseInt(v) : 0 })}
              placeholder={loading ? "Загрузка..." : "Не назначен"}
              searchPlaceholder="Поиск по имени..."
              disabled={loading}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              onCancel();
              onEmailTouchedChange(false);
            }}
          >
            Отмена
          </Button>
          <Button className="gap-2" onClick={onSubmit} disabled={!formData.email || showEmailError}>
            <Send className="size-4" />
            Отправить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
