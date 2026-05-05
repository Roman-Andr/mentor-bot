import { useTranslations } from "@/shared/hooks/use-translations";
import { StatsGrid } from "@/shared/ui/stat-card";
import { CheckCircle, Clock, AlertTriangle, ListTodo } from "lucide-react";
import type { ChecklistItem } from "@/shared/hooks/use-checklists";

interface ChecklistStatsProps {
  checklists: ChecklistItem[];
}

export function ChecklistStats({ checklists }: ChecklistStatsProps) {
  const t = useTranslations();

  const completed = checklists.filter((c) => c.status === "COMPLETED").length;
  const inProgress = checklists.filter((c) => c.status === "IN_PROGRESS").length;
  const overdue = checklists.filter((c) => c.isOverdue).length;

  return (
    <StatsGrid
      stats={[
        { label: t("checklists.total") || "Total", value: checklists.length, icon: ListTodo },
        { label: t("common.inProgress"), value: inProgress, icon: Clock },
        { label: t("common.completed"), value: completed, icon: CheckCircle },
        { label: t("common.overdue") || "Overdue", value: overdue, icon: AlertTriangle },
      ]}
    />
  );
}
