"use client";

import { useTranslations } from "next-intl";
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
  const t = useTranslations("users");
  const tCommon = useTranslations("common");

  const updateField = <K extends keyof UserFormData>(key: K, value: UserFormData[K]) => {
    onFormDataChange({ ...formData, [key]: value });
  };

  const isEdit = mode === "edit";
  const canSubmit =
    formData.first_name && formData.email && formData.employee_id && (isEdit || formData.password);

  const departmentOptions = [
    { value: "0", label: t("notSelected") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? t("editUserTitle") : t("addUserTitle")}</DialogTitle>
          <DialogDescription>
            {isEdit ? t("changeUserData") : t("addNewUser")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="firstName">{t("firstName")} *</Label>
              <Input
                id="firstName"
                placeholder={t("firstName")}
                value={formData.first_name}
                onChange={(e) => updateField("first_name", e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="lastName">{t("lastName")}</Label>
              <Input
                id="lastName"
                placeholder={t("lastName")}
                value={formData.last_name}
                onChange={(e) => updateField("last_name", e.target.value)}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="email">{tCommon("email")} *</Label>
            <Input
              id="email"
              type="email"
              placeholder="ivan.petrov@company.com"
              value={formData.email}
              onChange={(e) => updateField("email", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="phone">{tCommon("phone")}</Label>
            <Input
              id="phone"
              placeholder="+7 (999) 123-45-67"
              value={formData.phone}
              onChange={(e) => updateField("phone", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="employeeId">{t("employeeId")} *</Label>
            <Input
              id="employeeId"
              placeholder="EMP-001"
              value={formData.employee_id}
              onChange={(e) => updateField("employee_id", e.target.value)}
            />
          </div>
          {!isEdit && (
            <div className="grid gap-2">
              <Label htmlFor="password">{t("password")} *</Label>
              <Input
                id="password"
                type="password"
                placeholder={t("passwordHint")}
                value={formData.password}
                onChange={(e) => updateField("password", e.target.value)}
              />
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="department">{tCommon("department")}</Label>
              <Select
                id="department"
                value={formData.department_id ? String(formData.department_id) : ""}
                onChange={(val) => updateField("department_id", parseInt(val) || 0)}
                placeholder={t("selectDepartment")}
                options={departmentOptions}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="position">{t("position")}</Label>
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
              <Label htmlFor="role">{tCommon("role")}</Label>
              <Select
                id="role"
                value={formData.role}
                onChange={updateField.bind(null, "role")}
                options={ROLES}
                placeholder={t("selectRole")}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="level">{t("level")}</Label>
              <Select
                id="level"
                value={formData.level || ""}
                onChange={(val) => updateField("level", val)}
                options={LEVELS_WITH_EMPTY}
                placeholder={t("selectLevel")}
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
            <Label htmlFor="isActive">{t("isActive")}</Label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            {tCommon("cancel")}
          </Button>
          <Button onClick={onSubmit} disabled={!canSubmit}>
            {isEdit ? tCommon("save") : tCommon("create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}