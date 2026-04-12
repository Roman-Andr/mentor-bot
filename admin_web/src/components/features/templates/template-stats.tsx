import { useTranslations } from "@/hooks/use-translations";
import { StatsGrid } from "@/components/ui/stat-card";
import { FileText, CheckCircle, Users } from "lucide-react";
import type { TemplateItem } from "@/hooks/use-templates";

interface TemplateStatsProps {
  templates: TemplateItem[];
}

export function TemplateStats({ templates }: TemplateStatsProps) {
  const t = useTranslations();

  const active = templates.filter((t) => t.status === "ACTIVE").length;
  const drafts = templates.filter((t) => t.status === "DRAFT").length;
  const defaults = templates.filter((t) => t.isDefault).length;

  return (
    <StatsGrid
      stats={[
        { label: t("common.title") || "Total Templates", value: templates.length, icon: FileText },
        { label: t("common.active") || "Active", value: active, icon: CheckCircle },
        { label: t("templates.draftTemplates") || "Drafts", value: drafts, icon: FileText },
        { label: t("templates.defaultTemplates") || "Default", value: defaults, icon: Users },
      ]}
    />
  );
}
