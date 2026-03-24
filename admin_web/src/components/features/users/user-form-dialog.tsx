"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ROLES, LEVELS_WITH_EMPTY } from "@/lib/constants";
import type { UserFormData } from "@/hooks/use-users";

interface UserFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  formData: UserFormData;
  onFormDataChange: (data: UserFormData) => void;
  onSubmit: () => void;
  onCancel: () => void;
  departments?: { id: number; name: string }[];
}

export function UserFormDialog({
  open,
  onOpenChange,
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
  departments = [],
}: UserFormDialogProps) {
  const updateField = <K extends keyof UserFormData>(key: K, value: UserFormData[K]) => {
    onFormDataChange({ ...formData, [key]: value });
  };

  const isEdit = mode === "edit";
  const canSubmit = formData.first_name && formData.email && (isEdit || formData.password);

  const departmentOptions = [
    { value: "0", label: "Не выбран" },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEdit ? "Редактирование пользователя" : "Добавление пользователя"}
          </DialogTitle>
          <DialogDescription>
            {isEdit ? "Измените данные пользователя" : "Добавьте нового пользователя в систему"}
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
                onChange={(e) => updateField("first_name", e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="lastName">Фамилия</Label>
              <Input
                id="lastName"
                placeholder="Петров"
                value={formData.last_name}
                onChange={(e) => updateField("last_name", e.target.value)}
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
              onChange={(e) => updateField("email", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="phone">Телефон</Label>
            <Input
              id="phone"
              placeholder="+7 (999) 123-45-67"
              value={formData.phone}
              onChange={(e) => updateField("phone", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="employeeId">Табельный номер *</Label>
            <Input
              id="employeeId"
              placeholder="EMP-001"
              value={formData.employee_id}
              onChange={(e) => updateField("employee_id", e.target.value)}
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
                onChange={(e) => updateField("password", e.target.value)}
              />
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="department">Отдел</Label>
              <Select
                id="department"
                value={formData.department_id}
                onChange={(e) => updateField("department_id", parseInt(e.target.value) || 0)}
                placeholder="Выберите отдел"
                options={departmentOptions}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="position">Должность</Label>
              <Input
                id="position"
                placeholder="Backend Developer"
                value={formData.position}
                onChange={(e) => updateField("position", e.target.value)}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="role">Роль</Label>
              <Select
                id="role"
                value={formData.role}
                onChange={(e) => updateField("role", e.target.value)}
                options={ROLES}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="level">Уровень</Label>
              <Select
                id="level"
                value={formData.level}
                onChange={(e) => updateField("level", e.target.value)}
                options={LEVELS_WITH_EMPTY}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isActive"
              checked={formData.is_active}
              onChange={(e) => updateField("is_active", e.target.checked)}
               className="border-input rounded"
            />
            <Label htmlFor="isActive">Активен</Label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            Отмена
          </Button>
          <Button onClick={onSubmit} disabled={!canSubmit}>
            {isEdit ? "Сохранить" : "Добавить"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
