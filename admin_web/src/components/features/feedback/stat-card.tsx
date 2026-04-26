import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  color?: "default" | "blue" | "green" | "purple" | "orange";
}

export function StatCard({ title, value, subtitle, icon: Icon, color = "default" }: StatCardProps) {
  const colorClasses = {
    default: "bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary",
    blue: "bg-blue-500/10 text-blue-500 dark:bg-blue-500/20 dark:text-blue-400",
    green: "bg-green-500/10 text-green-500 dark:bg-green-500/20 dark:text-green-400",
    purple: "bg-purple-500/10 text-purple-500 dark:bg-purple-500/20 dark:text-purple-400",
    orange: "bg-orange-500/10 text-orange-500 dark:bg-orange-500/20 dark:text-orange-400",
  };

  return (
    <div className="bg-card rounded-xl border p-6 transition-shadow hover:shadow-lg">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-muted-foreground text-sm font-medium">{title}</div>
          <div className="mt-2 text-3xl font-bold">{value}</div>
          <div className="text-muted-foreground mt-1 text-xs">{subtitle}</div>
        </div>
        <div className={`rounded-lg p-3 ${colorClasses[color]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
