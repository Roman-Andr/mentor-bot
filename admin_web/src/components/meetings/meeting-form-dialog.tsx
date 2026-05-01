"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SearchableSelect } from "@/components/ui/searchable-select";
import {
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getMeetingTypeOptions, getLevelOptions } from "@/lib/constants";

interface MeetingFormData {
  title: string;
  description: string;
  type: string;
  department_id: number;
  position: string;
  level: string;
  deadline_days: number;
  duration_minutes: number;
  is_mandatory: boolean;
  order: number;
}

interface Department {
  id: number;
  name: string;
}

export interface MeetingFormDialogProps {
  mode: "create" | "edit";
  formData: MeetingFormData;
  departments: Department[];
  onFormDataChange: React.Dispatch<React.SetStateAction<MeetingFormData>>;
  onSubmit: () => void;
  onCancel: () => void;
}

export function MeetingFormDialog({
  mode,
  formData,
  departments,
  onFormDataChange,
  onSubmit,
  onCancel,
}: MeetingFormDialogProps) {
  const t = useTranslations();

  const meetingTypeOptions = getMeetingTypeOptions(t);
  const levelOptions = getLevelOptions(t, true);

  const departmentOptions = [
    { value: "", label: t("common.notSpecified") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  return (
    <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
      <DialogHeader>
        <DialogTitle>
          {mode === "create" ? t("meetings.createMeeting") : t("meetings.editMeetingTitle")}
        </DialogTitle>
        <DialogDescription>
          {mode === "create" ? t("meetings.createNewMeeting") : t("meetings.editMeetingParams")}
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.name")}</label>
          <input
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.title}
            onChange={(e) => onFormDataChange((prev) => ({ ...prev, title: e.target.value }))}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.description")}</label>
          <textarea
            className="w-full rounded-md border px-3 py-2 text-sm"
            rows={3}
            value={formData.description}
            onChange={(e) => onFormDataChange((prev) => ({ ...prev, description: e.target.value }))}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.type")}</label>
          <Select
            value={formData.type}
            onChange={(val) => onFormDataChange((prev) => ({ ...prev, type: val }))}
            options={meetingTypeOptions}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.department")}</label>
          <SearchableSelect
            value={formData.department_id ? String(formData.department_id) : ""}
            onChange={(val) => onFormDataChange((prev) => ({ ...prev, department_id: val ? Number(val) : 0 }))}
            options={departmentOptions}
            placeholder={t("meetings.selectDepartment")}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.position")}</label>
          <input
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.position}
            onChange={(e) => onFormDataChange((prev) => ({ ...prev, position: e.target.value }))}
            placeholder={t("meetings.positionPlaceholder")}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.level")}</label>
          <Select
            value={formData.level}
            onChange={(val) => onFormDataChange((prev) => ({ ...prev, level: val }))}
            options={levelOptions}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.deadlineDays")}</label>
          <input
            type="number"
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.deadline_days}
            onChange={(e) =>
              onFormDataChange((prev) => ({ ...prev, deadline_days: parseInt(e.target.value) || 0 }))
            }
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.durationMinutes")}</label>
          <input
            type="number"
            min={1}
            max={480}
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.duration_minutes}
            onChange={(e) =>
              onFormDataChange((prev) => ({ ...prev, duration_minutes: parseInt(e.target.value) || 60 }))
            }
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_mandatory"
            checked={formData.is_mandatory}
            onChange={(e) => onFormDataChange((prev) => ({ ...prev, is_mandatory: e.target.checked }))}
          />
          <label htmlFor="is_mandatory" className="text-sm font-medium">
            {t("meetings.isMandatory")}
          </label>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">{t("meetings.order")}</label>
          <input
            type="number"
            className="w-full rounded-md border px-3 py-2 text-sm"
            value={formData.order}
            onChange={(e) =>
              onFormDataChange((prev) => ({ ...prev, order: parseInt(e.target.value) || 0 }))
            }
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          {t("common.cancel")}
        </Button>
        <Button onClick={onSubmit}>{mode === "create" ? t("common.create") : t("common.save")}</Button>
      </DialogFooter>
    </DialogContent>
  );
}
