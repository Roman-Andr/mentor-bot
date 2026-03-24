import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatItem {
  title: string;
  value: string;
  change: string;
  changeType: string;
  icon: LucideIcon;
  color: string;
}

interface StatsCardsProps {
  statsData: StatItem[];
}

export function StatsCards({ statsData }: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {statsData.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">{stat.title}</CardTitle>
            <div className={`rounded-lg p-2 ${stat.color}`}>
              <stat.icon className="size-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            {stat.change && (
              <p className="text-muted-foreground mt-1 text-xs">
                <span
                  className={stat.changeType === "positive" ? "text-green-600" : "text-red-600"}
                >
                  {stat.change}
                </span>{" "}
                за последний месяц
              </p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
