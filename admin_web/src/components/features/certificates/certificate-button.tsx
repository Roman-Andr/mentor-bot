"use client";

import { useState } from "react";
import { Award, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocale } from "next-intl";
import { useTranslations } from "@/hooks/use-translations";
import { useToast } from "@/hooks/use-toast";
import type { User } from "@/types";
import type { Checklist } from "@/types";
import {
  generateCertificatePDF,
  downloadPDF,
  generateCertificateFilename,
} from "@/lib/pdf/export";

interface CertificateButtonProps {
  user: User;
  checklist: Checklist & { template_name?: string };
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  className?: string;
}

export function CertificateButton({
  user,
  checklist,
  variant = "outline",
  size = "default",
  className,
}: CertificateButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const locale = useLocale();
  const tNav = useTranslations("nav");
  const { toast } = useToast();

  const handleExport = async () => {
    setIsGenerating(true);
    try {
      const translations = {
        title: locale === "ru" ? "Сертификат о Завершении" : "Certificate of Completion",
        subtitle: locale === "ru" ? "Онбординг успешно завершён" : "Onboarding Successfully Completed",
        presentedTo: locale === "ru" ? "Вручается" : "Presented to",
        achievement: locale === "ru"
          ? `За успешное завершение программы онбординга "{templateName}"`
          : `For successfully completing the "{templateName}" onboarding program`,
        completedOn: locale === "ru" ? "Дата завершения" : "Completed on",
        hrSignature: locale === "ru" ? "Подпись HR" : "HR Signature",
        mentorSignature: locale === "ru" ? "Подпись наставника" : "Mentor Signature",
        date: locale === "ru" ? "Дата" : "Date",
        certificateId: locale === "ru" ? "№ сертификата" : "Certificate #",
        appName: tNav("appName"),
      };

      const blob = await generateCertificatePDF(user, checklist, translations, locale);
      const filename = generateCertificateFilename(user, locale);
      downloadPDF(blob, filename);
      toast(locale === "ru" ? "Сертификат скачан" : "Certificate downloaded", "success");
    } catch (error) {
      console.error("Failed to generate certificate:", error);
      toast(locale === "ru" ? "Ошибка генерации сертификата" : "Failed to generate certificate", "error");
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
          <Award className="mr-2 h-4 w-4" />
          {locale === "ru" ? "Сертификат" : "Certificate"}
        </>
      )}
    </Button>
  );
}
