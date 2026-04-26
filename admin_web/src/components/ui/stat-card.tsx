import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface StatCardProps {
  value: string | number;
  label: string;
  icon: LucideIcon;
  color?: string;
}

const DEFAULT_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

export function StatCard({ value, label, icon: Icon, color = "#3B82F6" }: StatCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-muted-foreground text-sm">{label}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
          <Icon className="size-8" style={{ color }} />
        </div>
      </CardContent>
    </Card>
  );
}

interface StatsGridProps {
  stats: Omit<StatCardProps, "color">[];
}

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-4">
      {stats.map((stat, index) => (
        <StatCard
          key={stat.label}
          {...stat}
          color={DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
        />
      ))}
    </div>
  );
}
