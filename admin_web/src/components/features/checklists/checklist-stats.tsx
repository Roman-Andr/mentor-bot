import { StatsGrid } from "@/components/ui/stat-card";
import { CheckCircle, Clock, AlertTriangle, ListTodo } from "lucide-react";
import type { ChecklistItem } from "@/hooks/use-checklists";

interface ChecklistStatsProps {
  checklists: ChecklistItem[];
}

export function ChecklistStats({ checklists }: ChecklistStatsProps) {
  const completed = checklists.filter((c) => c.status === "COMPLETED").length;
  const inProgress = checklists.filter((c) => c.status === "IN_PROGRESS").length;
  const overdue = checklists.filter((c) => c.isOverdue).length;

  return (
    <StatsGrid
      stats={[
        { label: "Всего", value: checklists.length, icon: ListTodo },
        { label: "В работе", value: inProgress, icon: Clock },
        { label: "Завершено", value: completed, icon: CheckCircle },
        { label: "Просрочено", value: overdue, icon: AlertTriangle },
      ]}
    />
  );
}
