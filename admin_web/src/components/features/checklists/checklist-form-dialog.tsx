"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { SearchableSelect, type SelectOption } from "@/components/ui/searchable-select";
import { api } from "@/lib/api";
import type { User, Template } from "@/types";
import type { ChecklistFormData } from "@/hooks/use-checklists";

interface ChecklistFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  formData: ChecklistFormData;
  onFormDataChange: (data: ChecklistFormData) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

function formatUserLabel(user: User): string {
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ");
  return `${name} (${user.employee_id})`;
}

function formatUserDescription(user: User): string {
  return [user.department, user.position].filter(Boolean).join(" · ");
}

export function ChecklistFormDialog({
  open,
  onOpenChange,
  mode,
  formData,
  onFormDataChange,
  onSubmit,
  onCancel,
}: ChecklistFormDialogProps) {
  const t = useTranslations();

  const isCreate = mode === "create";

  const [users, setUsers] = useState<User[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

  const loadReferenceData = useCallback(async () => {
    setLoading(true);
    try {
      const [usersRes, templatesRes] = await Promise.all([
        api.users.list({ limit: 100 }),
        api.templates.list({ limit: 100 }),
      ]);
      if (usersRes.data) setUsers(usersRes.data.users);
      if (templatesRes.data) setTemplates(templatesRes.data);
    } catch (err) {
      console.error("Failed to load reference data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (open) loadReferenceData();
  }, [open, loadReferenceData]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const employeeOptions: SelectOption[] = users.map((u) => ({
    value: String(u.id),
    label: formatUserLabel(u),
    description: formatUserDescription(u),
  }));

  const allTemplateOptions: SelectOption[] = templates.map((t) => ({
    value: String(t.id),
    label: t.name,
    description: [t.department, t.position].filter(Boolean).join(" · ") || `${t.status}`,
  }));

  const mentorOptions: SelectOption[] = users
    .filter((u) => u.role === "MENTOR" || u.role === "HR" || u.role === "ADMIN")
    .map((u) => ({
      value: String(u.id),
      label: formatUserLabel(u),
      description: formatUserDescription(u),
    }));

  const hrOptions: SelectOption[] = users
    .filter((u) => u.role === "HR" || u.role === "ADMIN")
    .map((u) => ({
      value: String(u.id),
      label: formatUserLabel(u),
      description: formatUserDescription(u),
    }));

  const handleUserSelect = (userIdStr: string) => {
    const userId = userIdStr ? parseInt(userIdStr) : 0;
    const selectedUser = users.find((u) => u.id === userId);
    onFormDataChange({
      ...formData,
      user_id: userId,
      employee_id: selectedUser?.employee_id || "",
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isCreate ? t("checklists.addChecklist") : t("checklists.editChecklist")}</DialogTitle>
          <DialogDescription>
            {isCreate ? t("checklists.assignChecklist") : t("checklists.changeChecklistParams")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("checklists.employee")} *</label>
            <SearchableSelect
              options={employeeOptions}
              value={formData.user_id ? String(formData.user_id) : ""}
              onChange={handleUserSelect}
              placeholder={loading ? t("common.loading") : t("checklists.selectEmployee")}
              searchPlaceholder={t("checklists.searchByNameOrId")}
              disabled={!isCreate || loading}
            />
            {formData.employee_id && (
              <p className="text-muted-foreground text-xs">
                {t("checklists.employeeId")}: {formData.employee_id}
              </p>
            )}
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("checklists.template")} *</label>
            <SearchableSelect
              options={isCreate ? allTemplateOptions : allTemplateOptions}
              value={formData.template_id ? String(formData.template_id) : ""}
              onChange={(v) =>
                onFormDataChange({
                  ...formData,
                  template_id: v ? parseInt(v) : 0,
                })
              }
              placeholder={loading ? t("common.loading") : t("checklists.selectTemplate")}
              searchPlaceholder={t("checklists.searchTemplate")}
              disabled={!isCreate || loading}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("checklists.startDate")} *</label>
              <Input
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  onFormDataChange({
                    ...formData,
                    start_date: e.target.value,
                  })
                }
                disabled={!isCreate}
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("checklists.dueDate")}</label>
              <Input
                type="date"
                value={formData.due_date}
                onChange={(e) =>
                  onFormDataChange({
                    ...formData,
                    due_date: e.target.value,
                  })
                }
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">{t("checklists.mentor")}</label>
              <SearchableSelect
                options={mentorOptions}
                value={formData.mentor_id ? String(formData.mentor_id) : ""}
                onChange={(v) =>
                  onFormDataChange({
                    ...formData,
                    mentor_id: v ? parseInt(v) : null,
                  })
                }
                placeholder={loading ? t("common.loading") : t("checklists.selectMentor")}
                searchPlaceholder={t("checklists.searchByName")}
                disabled={loading}
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">HR</label>
              <SearchableSelect
                options={hrOptions}
                value={formData.hr_id ? String(formData.hr_id) : ""}
                onChange={(v) =>
                  onFormDataChange({
                    ...formData,
                    hr_id: v ? parseInt(v) : null,
                  })
                }
                placeholder={loading ? t("common.loading") : t("checklists.selectHr")}
                searchPlaceholder={t("checklists.searchByName")}
                disabled={loading}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">{t("checklists.notes")}</label>
            <Textarea
              placeholder={t("checklists.notesPlaceholder")}
              value={formData.notes}
              onChange={(e) =>
                onFormDataChange({
                  ...formData,
                  notes: e.target.value,
                })
              }
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            {t("common.cancel")}
          </Button>
          <Button
            onClick={onSubmit}
            disabled={
              !formData.user_id ||
              !formData.employee_id ||
              !formData.template_id ||
              !formData.start_date
            }
          >
            {isCreate ? t("common.create") : t("common.save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}