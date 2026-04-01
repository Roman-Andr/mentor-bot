"use client";

import { useTranslations } from "next-intl";
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
  const t = useTranslations("invitations");
  const tCommon = useTranslations("common");

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
          <DialogTitle>{t("createInvitation")}</DialogTitle>
          <DialogDescription>
            {t("sendInvitationDescription") || "Send invitation to new employee for registration"}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="email">{tCommon("email")}</Label>
            <Input
              id="email"
              type="email"
              placeholder="employee@company.com"
              value={formData.email}
              className={showEmailError ? "border-red-500 focus-visible:ring-red-500" : ""}
              onChange={(e) => onFormDataChange({ ...formData, email: e.target.value })}
              onBlur={() => onEmailTouchedChange(true)}
            />
            {showEmailError && <p className="text-sm text-red-500">{t("invalidEmail") || "Invalid email format"}</p>}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="employeeId">{t("employeeId")}</Label>
            <Input
              id="employeeId"
              placeholder="EMP-001"
              value={formData.employee_id}
              onChange={(e) => onFormDataChange({ ...formData, employee_id: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="department">{tCommon("department")}</Label>
            <Select
              id="department"
              options={departments.map((d) => ({ value: String(d.id), label: d.name }))}
              placeholder={t("selectDepartment")}
              value={formData.department_id ? String(formData.department_id) : ""}
              onChange={(val) =>
                onFormDataChange({ ...formData, department_id: parseInt(val) || 0 })
              }
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="position">{t("position") || "Position"}</Label>
            <Input
              id="position"
              placeholder="Developer"
              value={formData.position}
              onChange={(e) => onFormDataChange({ ...formData, position: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="level">{t("level")}</Label>
            <Select
              id="level"
              options={[...LEVELS]}
              placeholder={tCommon("notSelected")}
              value={formData.level || ""}
              onChange={(val) => onFormDataChange({ ...formData, level: val })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="role">{tCommon("role")}</Label>
            <Select
              id="role"
              options={ROLES}
              value={formData.role}
              onChange={(val) => onFormDataChange({ ...formData, role: val })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="mentor">{t("mentor")}</Label>
            <SearchableSelect
              options={mentorOptions}
              value={formData.mentor_id ? String(formData.mentor_id) : ""}
              onChange={(v) => onFormDataChange({ ...formData, mentor_id: v ? parseInt(v) : 0 })}
              placeholder={loading ? tCommon("loading") : t("notAssigned") || "Not assigned"}
              searchPlaceholder={t("searchByName")}
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
            {tCommon("cancel")}
          </Button>
          <Button className="gap-2" onClick={onSubmit} disabled={!formData.email || showEmailError}>
            <Send className="size-4" />
            {t("sendInvitation")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
