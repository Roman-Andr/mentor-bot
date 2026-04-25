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
    default: "bg-primary/10 text-primary",
    blue: "bg-blue-500/10 text-blue-500",
    green: "bg-green-500/10 text-green-500",
    purple: "bg-purple-500/10 text-purple-500",
    orange: "bg-orange-500/10 text-orange-500",
  };

  return (
    <div className="bg-card border rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-sm text-muted-foreground font-medium">{title}</div>
          <div className="text-3xl font-bold mt-2">{value}</div>
          <div className="text-xs text-muted-foreground mt-1">{subtitle}</div>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}
