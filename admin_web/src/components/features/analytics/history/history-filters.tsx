"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/date-picker";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { SearchableSelect, type SelectOption } from "@/components/ui/searchable-select";
import type { HistoryFilters, AuditSource, AuditEventType } from "@/types/audit";

interface HistoryFiltersProps {
  filters: HistoryFilters;
  onChange: (filters: HistoryFilters) => void;
}

const ALL_SOURCES: AuditSource[] = ["auth", "knowledge", "meetings", "feedback", "checklists", "escalations"];

const EVENT_TYPES_BY_SOURCE: Record<AuditSource, AuditEventType[]> = {
  auth: ["login", "role_change", "invitation_status_change", "mentor_assignment"],
  knowledge: ["article_change", "article_view", "category_change", "dialogue_scenario_change"],
  meetings: ["meeting_status_change", "meeting_participant_change"],
  feedback: ["feedback_status_change"],
  checklists: ["checklist_status_change", "task_completion", "template_change"],
  escalations: ["escalation_status_change", "mentor_intervention"],
};

export function HistoryFilters({ filters, onChange }: HistoryFiltersProps) {
  const t = useTranslations();

  const handleDateChange = (field: "from_date" | "to_date", value: string) => {
    onChange({ ...filters, [field]: value || undefined });
  };

  const handleSourceToggle = (source: AuditSource, checked: boolean) => {
    const currentSources = filters.sources || ALL_SOURCES;
    let newSources: AuditSource[];
    if (checked) {
      newSources = [...currentSources, source];
    } else {
      newSources = currentSources.filter((s) => s !== source);
    }
    onChange({ ...filters, sources: newSources.length === ALL_SOURCES.length ? undefined : newSources });
  };

  const handleEventTypeToggle = (eventType: AuditEventType, checked: boolean) => {
    const currentEventTypes = filters.event_types || [];
    let newEventTypes: AuditEventType[];
    if (checked) {
      newEventTypes = [...currentEventTypes, eventType];
    } else {
      newEventTypes = currentEventTypes.filter((e) => e !== eventType);
    }
    // If all event types for selected sources are checked, clear the filter
    const selectedSources = filters.sources || ALL_SOURCES;
    const allSelectedEventTypes = selectedSources.flatMap((s) => EVENT_TYPES_BY_SOURCE[s]);
    if (newEventTypes.length === allSelectedEventTypes.length) {
      onChange({ ...filters, event_types: undefined });
    } else {
      onChange({ ...filters, event_types: newEventTypes });
    }
  };

  const handleActorChange = (userId: number | null) => {
    onChange({ ...filters, actor_id: userId || undefined });
  };

  const handleReset = () => {
    onChange({});
  };

  const selectedSources = filters.sources || ALL_SOURCES;
  const selectedEventTypes = filters.event_types || [];

  return (
    <div className="space-y-4 p-4 border rounded-md bg-muted/20">
      <div className="flex items-end gap-4">
        <div className="flex flex-col gap-2">
          <Label>{t("analytics.history.filters.dateRange")}</Label>
          <div className="flex gap-2">
            <DatePicker
              value={filters.from_date || ""}
              onChange={(v) => handleDateChange("from_date", v)}
              placeholder={t("analytics.history.filters.fromDate")}
            />
            <DatePicker
              value={filters.to_date || ""}
              onChange={(v) => handleDateChange("to_date", v)}
              placeholder={t("analytics.history.filters.toDate")}
            />
          </div>
        </div>

        <div className="flex flex-col gap-2 flex-1">
          <Label>{t("analytics.history.filters.actor")}</Label>
          <Input
            type="number"
            placeholder={t("analytics.history.filters.actorPlaceholder")}
            value={filters.actor_id || ""}
            onChange={(e) => onChange({ ...filters, actor_id: e.target.value ? parseInt(e.target.value) : undefined })}
          />
        </div>

        <Button onClick={handleReset} variant="outline">
          {t("analytics.history.filters.reset")}
        </Button>
      </div>

      <div>
        <Label className="mb-2 block">{t("analytics.history.filters.source")}</Label>
        <div className="flex flex-wrap gap-2">
          {ALL_SOURCES.map((source) => (
            <div key={source} className="flex items-center gap-2">
              <Checkbox
                id={`source-${source}`}
                checked={selectedSources.includes(source)}
                onCheckedChange={(checked) => handleSourceToggle(source, checked as boolean)}
              />
              <label htmlFor={`source-${source}`} className="text-sm cursor-pointer">
                {t(`analytics.history.sources.${source}`)}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Label className="mb-2 block">{t("analytics.history.filters.eventTypes")}</Label>
        <SearchableSelect
          value={selectedEventTypes.length > 0 ? selectedEventTypes[0] : ""}
          onChange={(value) => onChange({ ...filters, event_types: value ? [value as AuditEventType] : undefined })}
          options={[
            { value: "", label: t("analytics.history.filters.allEventTypes") },
            ...selectedSources.flatMap((source) =>
              EVENT_TYPES_BY_SOURCE[source].map((eventType) => ({
                value: eventType,
                label: t(`analytics.history.eventTypes.${eventType}`),
              }))
            ),
          ]}
          placeholder={t("analytics.history.filters.allEventTypes")}
        />
      </div>
    </div>
  );
}
