import { StatsGrid } from "@/components/ui/stat-card";
import { FileText, CheckCircle, Users } from "lucide-react";
import type { TemplateItem } from "@/hooks/use-templates";

interface TemplateStatsProps {
  templates: TemplateItem[];
}

export function TemplateStats({ templates }: TemplateStatsProps) {
  const active = templates.filter((t) => t.status === "ACTIVE").length;
  const drafts = templates.filter((t) => t.status === "DRAFT").length;
  const defaults = templates.filter((t) => t.isDefault).length;

  return (
    <StatsGrid
      stats={[
        { label: "Всего шаблонов", value: templates.length, icon: FileText },
        { label: "Активных", value: active, icon: CheckCircle },
        { label: "Черновиков", value: drafts, icon: FileText },
        { label: "По умолчанию", value: defaults, icon: Users },
      ]}
    />
  );
}
