"use client";

import { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocale } from "next-intl";
import { useTranslations } from "@/hooks/use-translations";
import { useToast } from "@/hooks/use-toast";
import { logger } from "@/lib/logger";
import type { ChecklistStats } from "@/types";
import {
  generateOnboardingReportPDF,
  downloadPDF,
  generatePDFReportFilename,
} from "@/lib/pdf/export";

interface PDFExportButtonProps {
  data: {
    stats: ChecklistStats | null;
    userCount: number;
    monthlyData: Array<{ month: string; newUsers: number; completed: number }>;
    completionTimeData: Array<{ range: string; count: number }>;
    departmentData: Array<{ name: string; value: number; color: string }>;
  };
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  className?: string;
}

export function PDFExportButton({
  data,
  variant = "outline",
  size = "default",
  className,
}: PDFExportButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const locale = useLocale();
  const t = useTranslations("analytics");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  const { toast } = useToast();

  const handleExport = async () => {
    setIsGenerating(true);
    try {
      const translations = {
        title: t("title"),
        overview: t("overview"),
        generatedAt: locale === "ru" ? "Сгенерировано" : "Generated at",
        summary: locale === "ru" ? "Сводка" : "Summary",
        totalNewbies: t("totalNewbies"),
        completed: tCommon("completed"),
        inProgress: tCommon("inProgress"),
        overdue: t("overdue"),
        averageTime: t("averageTime"),
        completionRate: t("completionRate"),
        byDepartments: t("byDepartments"),
        monthlyDynamics: t("onboardingDynamics"),
        completionTimeDistribution: locale === "ru" ? "Распределение по времени завершения" : "Completion Time Distribution",
        department: tCommon("department"),
        count: tCommon("total"),
        month: locale === "ru" ? "Месяц" : "Month",
        newUsers: t("newUsers"),
        range: locale === "ru" ? "Диапазон" : "Range",
        appName: tNav("appName"),
        page: locale === "ru" ? "Страница" : "Page",
        of: locale === "ru" ? "из" : "of",
      };

      const blob = await generateOnboardingReportPDF(data, translations, locale);
      const filename = generatePDFReportFilename(locale);
      downloadPDF(blob, filename);
      toast(locale === "ru" ? "PDF успешно экспортирован" : "PDF exported successfully", "success");
    } catch (error) {
      logger.error("Failed to generate PDF", { error });
      toast(locale === "ru" ? "Ошибка генерации PDF" : "Failed to generate PDF", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleExport}
      disabled={isGenerating}
      className={className}
    >
      {isGenerating ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          {locale === "ru" ? "Генерация..." : "Generating..."}
        </>
      ) : (
        <>
          <FileText className="mr-2 h-4 w-4" />
          PDF
        </>
      )}
    </Button>
  );
}
