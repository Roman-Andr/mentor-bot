import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Activity {
  user: string;
  action: string;
  task: string;
  time: string;
}

interface ActivityFeedProps {
  activity: Activity[];
}

export function ActivityFeed({ activity }: ActivityFeedProps) {
  const t = useTranslations("dashboard");

  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>{t("recentActivity")}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activity.map((item, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="mt-2 size-2 rounded-full bg-blue-500" />
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
}
