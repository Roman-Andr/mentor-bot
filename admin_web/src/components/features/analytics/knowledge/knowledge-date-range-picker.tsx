"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/date-picker";

interface DateRange {
  from_date?: string;
  to_date?: string;
}

interface KnowledgeDateRangePickerProps {
  onChange: (range: DateRange) => void;
  defaultFrom?: string;
  defaultTo?: string;
}

export function KnowledgeDateRangePicker({ onChange, defaultFrom, defaultTo }: KnowledgeDateRangePickerProps) {
  const t = useTranslations();
  const [fromDate, setFromDate] = useState(defaultFrom || "");
  const [toDate, setToDate] = useState(defaultTo || "");

  const handleApply = () => {
    onChange({ from_date: fromDate || undefined, to_date: toDate || undefined });
  };

  const handleReset = () => {
    setFromDate("");
    setToDate("");
    onChange({});
  };

  return (
    <div className="flex items-end gap-4">
      <div className="flex flex-col gap-2">
        <Label>{t("analytics.knowledge.fromDate")}</Label>
        <DatePicker
          value={fromDate}
          onChange={setFromDate}
          placeholder={t("analytics.knowledge.fromDate")}
        />
      </div>
      <div className="flex flex-col gap-2">
        <Label>{t("analytics.knowledge.toDate")}</Label>
        <DatePicker
          value={toDate}
          onChange={setToDate}
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
  );
}
