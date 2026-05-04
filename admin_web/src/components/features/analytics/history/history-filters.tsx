"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/date-picker";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { ChevronDown, ChevronUp } from "lucide-react";
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
  const [showEventTypes, setShowEventTypes] = useState(false);

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
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-between"
          onClick={() => setShowEventTypes(!showEventTypes)}
        >
          {t("analytics.history.filters.eventTypes")}
          {showEventTypes ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </Button>
        {showEventTypes && (
          <div className="space-y-3 mt-3">
            {selectedSources.map((source) => (
              <div key={source}>
                <p className="text-sm font-medium mb-2">{t(`analytics.history.sources.${source}`)}</p>
                <div className="flex flex-wrap gap-2">
                  {EVENT_TYPES_BY_SOURCE[source].map((eventType) => (
                    <div key={eventType} className="flex items-center gap-2">
                      <Checkbox
                        id={`event-${eventType}`}
                        checked={selectedEventTypes.includes(eventType)}
                        onCheckedChange={(checked) => handleEventTypeToggle(eventType, checked as boolean)}
                      />
                      <label htmlFor={`event-${eventType}`} className="text-sm cursor-pointer">
                        {t(`analytics.history.eventTypes.${eventType}`)}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
