"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Label } from "@/shared/ui/label";
import { Button } from "@/shared/ui/button";
import { DatePicker } from "@/shared/ui/date-picker";
import { cn } from "@/shared/lib/utils";

interface DateRange {
  from_date?: string;
  to_date?: string;
}

interface KnowledgeDateRangePickerProps {
  onChange: (range: DateRange) => void;
  defaultFrom?: string;
  defaultTo?: string;
}

const PRESETS = [
  { label: "7d", days: 7 },
  { label: "30d", days: 30 },
  { label: "3mo", days: 90 },
  { label: "6mo", days: 180 },
];

function toISODate(d: Date) {
  return d.toISOString().split("T")[0];
}

export function KnowledgeDateRangePicker({ onChange, defaultFrom, defaultTo }: KnowledgeDateRangePickerProps) {
  const t = useTranslations();
  const [fromDate, setFromDate] = useState(defaultFrom || "");
  const [toDate, setToDate] = useState(defaultTo || "");
  const [activePreset, setActivePreset] = useState<number | null>(null);

  const handleApply = () => {
    setActivePreset(null);
    onChange({ from_date: fromDate || undefined, to_date: toDate || undefined });
  };

  const handleReset = () => {
    setFromDate("");
    setToDate("");
    setActivePreset(null);
    onChange({});
  };

  const applyPreset = (days: number, idx: number) => {
    const to = new Date();
    const from = new Date();
    from.setDate(from.getDate() - days);
    const fromStr = toISODate(from);
    const toStr = toISODate(to);
    setFromDate(fromStr);
    setToDate(toStr);
    setActivePreset(idx);
    onChange({ from_date: fromStr, to_date: toStr });
  };

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="flex items-center gap-1.5">
        {PRESETS.map((p, i) => (
          <Button
            key={p.label}
            variant={activePreset === i ? "default" : "outline"}
            size="sm"
            onClick={() => applyPreset(p.days, i)}
            className={cn("h-8 px-3 text-xs", activePreset === i && "shadow-none")}
          >
            {p.label}
          </Button>
        ))}
      </div>
      <div className="flex items-end gap-3">
        <div className="flex flex-col gap-1.5">
          <Label className="text-xs">{t("analytics.knowledge.fromDate")}</Label>
          <DatePicker
            value={fromDate}
            onChange={(v) => { setFromDate(v); setActivePreset(null); }}
            placeholder={t("analytics.knowledge.fromDate")}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label className="text-xs">{t("analytics.knowledge.toDate")}</Label>
          <DatePicker
            value={toDate}
            onChange={(v) => { setToDate(v); setActivePreset(null); }}
            placeholder={t("analytics.knowledge.toDate")}
          />
        </div>
        <Button onClick={handleApply} size="default">
          {t("analytics.knowledge.apply")}
        </Button>
        <Button onClick={handleReset} variant="outline" size="default">
          {t("analytics.knowledge.reset")}
        </Button>
      </div>
    </div>
  );
}
