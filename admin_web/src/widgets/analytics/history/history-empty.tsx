"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { FileText } from "lucide-react";

export function HistoryEmpty() {
  const t = useTranslations();

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
      <h3 className="mb-2 text-lg font-semibold">{t("analytics.history.empty")}</h3>
      <p className="text-sm text-muted-foreground">
        Try adjusting your filters to see more results
      </p>
    </div>
  );
}
