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
    <Card className="col-span-1 transition-shadow hover:shadow-md md:col-span-2 lg:col-span-3">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle>{t("dashboard.recentActivity")}</CardTitle>
        {href && (
          <Link href={href}>
            <Button variant="ghost" size="sm" className="gap-1 text-xs">
              <ExternalLink className="size-3" />
              <span className="hidden sm:inline">{t("common.viewAll")}</span>
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
                  <span className="font-normal text-muted-foreground">{item.action}</span>
                </p>
                <p className="text-xs text-muted-foreground">{item.task}</p>
              </div>
              <span className="text-xs whitespace-nowrap text-muted-foreground">{item.time}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  return card;
}
