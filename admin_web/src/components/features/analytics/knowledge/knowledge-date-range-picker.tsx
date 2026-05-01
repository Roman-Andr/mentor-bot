"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

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
        <Label htmlFor="from-date">{t("analytics.knowledge.fromDate")}</Label>
        <Input
          id="from-date"
          type="date"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
          className="w-40"
        />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="to-date">{t("analytics.knowledge.toDate")}</Label>
        <Input
          id="to-date"
          type="date"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
          className="w-40"
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
