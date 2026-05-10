import { Card, CardContent } from "@/shared/ui/card";
import type { LucideIcon } from "lucide-react";
import { TrendingUp, TrendingDown, Minus, ExternalLink } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import Link from "next/link";

interface StatItem {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: LucideIcon;
  color: string;
  description?: string;
  href?: string;
}

interface StatsCardsProps {
  statsData: StatItem[];
}

const colorMap: Record<string, string> = {
  "bg-blue-500":
    "from-blue-500/20 to-blue-600/10 border-blue-500/20 [&_.icon-bg]:bg-blue-500 [&_.icon-text]:text-blue-400",
  "bg-yellow-500":
    "from-yellow-500/20 to-yellow-600/10 border-yellow-500/20 [&_.icon-bg]:bg-yellow-500 [&_.icon-text]:text-yellow-400",
  "bg-green-500":
    "from-green-500/20 to-green-600/10 border-green-500/20 [&_.icon-bg]:bg-green-500 [&_.icon-text]:text-green-400",
  "bg-red-500":
    "from-red-500/20 to-red-600/10 border-red-500/20 [&_.icon-bg]:bg-red-500 [&_.icon-text]:text-red-400",
  "bg-purple-500":
    "from-purple-500/20 to-purple-600/10 border-purple-500/20 [&_.icon-bg]:bg-purple-500 [&_.icon-text]:text-purple-400",
};

export function StatsCards({ statsData }: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {statsData.map((stat) => {
        const Icon = stat.icon;
        const colorClass = colorMap[stat.color] ?? colorMap["bg-blue-500"];
        const card = (
          <Card
            className={cn(
              "group relative overflow-hidden border bg-gradient-to-br transition-shadow hover:shadow-md",
              stat.href && "cursor-pointer",
              colorClass,
            )}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-muted-foreground">{stat.title}</p>
                  <p className="mt-1 text-3xl font-bold tracking-tight">{stat.value}</p>
                  {stat.description && (
                    <p className="mt-0.5 text-xs text-muted-foreground">{stat.description}</p>
                  )}
                </div>
                <div className="icon-bg ml-3 shrink-0 rounded-xl p-2.5">
                  <Icon className="size-5 text-white" />
                </div>
              </div>

              {stat.change && (
                <div className="mt-4 flex items-center gap-1.5">
                  {stat.changeType === "positive" && (
                    <TrendingUp className="size-3.5 text-green-500" />
                  )}
                  {stat.changeType === "negative" && (
                    <TrendingDown className="size-3.5 text-red-500" />
                  )}
                  {stat.changeType === "neutral" && (
                    <Minus className="size-3.5 text-muted-foreground" />
                  )}
                  <span
                    className={cn(
                      "text-xs font-medium",
                      stat.changeType === "positive" && "text-green-600 dark:text-green-400",
                      stat.changeType === "negative" && "text-red-600 dark:text-red-400",
                      stat.changeType === "neutral" && "text-muted-foreground",
                    )}
                  >
                    {stat.change}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        );
        return stat.href ? (
          <Link key={stat.title} href={stat.href} className="block">
            {card}
          </Link>
        ) : (
          <div key={stat.title}>{card}</div>
        );
      })}
    </div>
  );
}
