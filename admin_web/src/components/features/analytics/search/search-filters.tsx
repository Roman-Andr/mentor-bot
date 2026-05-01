"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
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
  const [departments, setDepartments] = useState<Array<{ id: number; name: string }>>([]);

  useEffect(() => {
    async function loadDepartments() {
      try {
        const result = await departmentsApi.list({ limit: 1000 });
        if (result.success && result.data?.departments) {
          setDepartments(result.data.departments);
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
            <Label htmlFor="from-date">{t("analytics.search.fromDate")}</Label>
            <input
              id="from-date"
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="to-date">{t("analytics.search.toDate")}</Label>
            <input
              id="to-date"
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="department">{t("analytics.search.department")}</Label>
            <select
              id="department"
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">{t("analytics.search.allDepartments")}</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
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
