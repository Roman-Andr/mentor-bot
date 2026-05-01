"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/date-picker";
import { Select, SelectOption } from "@/components/ui/select";
import { departmentsApi } from "@/lib/api/departments";
import { useEffect } from "react";
import { logger } from "@/lib/logger";

interface SearchFiltersProps {
  onFiltersChange: (filters: { from_date?: string; to_date?: string; department_id?: number }) => void;
}

export function SearchFilters({ onFiltersChange }: SearchFiltersProps) {
  const t = useTranslations();
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");
  const [departmentId, setDepartmentId] = useState<string>("");
  const [departmentOptions, setDepartmentOptions] = useState<SelectOption[]>([]);

  useEffect(() => {
    async function loadDepartments() {
      try {
        const result = await departmentsApi.list({ limit: 1000 });
        if (result.success && result.data?.departments) {
          const options: SelectOption[] = result.data.departments.map((dept: { id: number; name: string }) => ({
            value: dept.id.toString(),
            label: dept.name,
          }));
          setDepartmentOptions(options);
        }
      } catch (error) {
        logger.error("Failed to load departments", { error });
      }
    }
    loadDepartments();
  }, []);

  const handleApply = () => {
    onFiltersChange({
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
      department_id: departmentId ? parseInt(departmentId, 10) : undefined,
    });
  };

  const handleReset = () => {
    setFromDate("");
    setToDate("");
    setDepartmentId("");
    onFiltersChange({});
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="grid gap-4 md:grid-cols-4">
          <div className="space-y-2">
            <Label>{t("analytics.search.fromDate")}</Label>
            <DatePicker
              value={fromDate}
              onChange={setFromDate}
              placeholder={t("analytics.search.fromDate")}
            />
          </div>
          <div className="space-y-2">
            <Label>{t("analytics.search.toDate")}</Label>
            <DatePicker
              value={toDate}
              onChange={setToDate}
              placeholder={t("analytics.search.toDate")}
            />
          </div>
          <div className="space-y-2">
            <Label>{t("analytics.search.department")}</Label>
            <Select
              value={departmentId}
              onChange={setDepartmentId}
              options={[
                { value: "", label: t("analytics.search.allDepartments") },
                ...departmentOptions,
              ]}
              placeholder={t("analytics.search.allDepartments")}
            />
          </div>
          <div className="flex items-end gap-2">
            <Button onClick={handleApply} className="flex-1">
              {t("common.apply")}
            </Button>
            <Button onClick={handleReset} variant="outline" className="flex-1">
              {t("common.reset")}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
