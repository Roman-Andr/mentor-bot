"use client";

import { useTranslations } from "@/hooks/use-translations";
import { FileText } from "lucide-react";

export function HistoryEmpty() {
  const t = useTranslations();

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <FileText className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">{t("analytics.history.empty")}</h3>
      <p className="text-muted-foreground text-sm">
        Try adjusting your filters to see more results
      </p>
    </div>
  );
}
