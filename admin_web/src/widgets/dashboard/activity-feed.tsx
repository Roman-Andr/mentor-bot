import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

interface Activity {
  user: string;
  action: string;
  task: string;
  time: string;
}

interface ActivityFeedProps {
  activity: Activity[];
  href?: string;
}

export function ActivityFeed({ activity, href }: ActivityFeedProps) {
  const t = useTranslations();

  const card = (
    <Card className="col-span-3 transition-shadow hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle>{t("dashboard.recentActivity")}</CardTitle>
        {href && (
          <Link href={href}>
            <Button variant="ghost" size="sm" className="gap-1 text-xs">
              <ExternalLink className="size-3" />
              {t("common.viewAll")}
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activity.map((item, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="mt-2 size-2 rounded-full bg-blue-500 dark:bg-blue-600" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">
                  {item.user}{" "}
                  <span className="text-muted-foreground font-normal">{item.action}</span>
                </p>
                <p className="text-muted-foreground text-xs">{item.task}</p>
              </div>
              <span className="text-muted-foreground text-xs whitespace-nowrap">{item.time}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  return card;
}
