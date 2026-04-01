import { useTranslations } from "next-intl";
import { StatsGrid } from "@/components/ui/stat-card";
import { CheckCircle, Clock, AlertTriangle, ListTodo } from "lucide-react";
import type { ChecklistItem } from "@/hooks/use-checklists";

interface ChecklistStatsProps {
  checklists: ChecklistItem[];
}

export function ChecklistStats({ checklists }: ChecklistStatsProps) {
  const t = useTranslations("checklists");
  const tCommon = useTranslations("common");

  const completed = checklists.filter((c) => c.status === "COMPLETED").length;
  const inProgress = checklists.filter((c) => c.status === "IN_PROGRESS").length;
  const overdue = checklists.filter((c) => c.isOverdue).length;

  return (
    <StatsGrid
      stats={[
        { label: t("total") || "Total", value: checklists.length, icon: ListTodo },
        { label: tCommon("inProgress"), value: inProgress, icon: Clock },
        { label: tCommon("completed"), value: completed, icon: CheckCircle },
        { label: tCommon("overdue") || "Overdue", value: overdue, icon: AlertTriangle },
      ]}
    />
  );
}
