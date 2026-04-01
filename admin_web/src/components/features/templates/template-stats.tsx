import { useTranslations } from "next-intl";
import { StatsGrid } from "@/components/ui/stat-card";
import { FileText, CheckCircle, Users } from "lucide-react";
import type { TemplateItem } from "@/hooks/use-templates";

interface TemplateStatsProps {
  templates: TemplateItem[];
}

export function TemplateStats({ templates }: TemplateStatsProps) {
  const t = useTranslations("templates");

  const active = templates.filter((t) => t.status === "ACTIVE").length;
  const drafts = templates.filter((t) => t.status === "DRAFT").length;
  const defaults = templates.filter((t) => t.isDefault).length;

  return (
    <StatsGrid
      stats={[
        { label: t("totalTemplates") || "Total Templates", value: templates.length, icon: FileText },
        { label: t("activeTemplates") || "Active", value: active, icon: CheckCircle },
        { label: t("draftTemplates") || "Drafts", value: drafts, icon: FileText },
        { label: t("defaultTemplates") || "Default", value: defaults, icon: Users },
      ]}
    />
  );
}
