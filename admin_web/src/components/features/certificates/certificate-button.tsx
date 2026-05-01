"use client";

import { useState } from "react";
import { Award, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocale } from "next-intl";
import { useToast } from "@/hooks/use-toast";
import { certificatesApi } from "@/lib/api/certificates";

interface CertificateButtonProps {
  certUid: string | null;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  className?: string;
}

export function CertificateButton({
  certUid,
  variant = "outline",
  size = "default",
  className,
}: CertificateButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const locale = useLocale();
  const { toast } = useToast();

  const handleDownload = async () => {
    if (!certUid) {
      toast(locale === "ru" ? "Сертификат не выдан" : "Certificate not issued", "error");
      return;
    }

    setIsGenerating(true);
    try {
      const blob = await certificatesApi.downloadCertificate(certUid, locale);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `certificate_${certUid}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast(locale === "ru" ? "Сертификат скачан" : "Certificate downloaded", "success");
    } catch (error) {
      console.error("Failed to download certificate:", error);
      toast(locale === "ru" ? "Ошибка скачивания сертификата" : "Failed to download certificate", "error");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleDownload}
      disabled={!certUid || isGenerating}
      className={className}
    >
      {isGenerating ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          {locale === "ru" ? "Загрузка..." : "Downloading..."}
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
