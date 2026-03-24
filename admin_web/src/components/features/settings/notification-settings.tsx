import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function NotificationSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Настройки уведомлений</CardTitle>
        <CardDescription>Настройка каналов и расписания уведомлений</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h4 className="font-medium">Email уведомления</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Напоминания о задачах</p>
                <p className="text-muted-foreground text-sm">
                  Отправлять email напоминания о предстоящих задачах
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Уведомления о встречах</p>
                <p className="text-muted-foreground text-sm">
                  Отправлять напоминания о запланированных встречах
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Ежедневный дайджест</p>
                <p className="text-muted-foreground text-sm">Отправлять ежедневную сводку о прогрессе</p>
              </div>
              <input type="checkbox" className="toggle" />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="font-medium">Время отправки</h4>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="notifyMorning">Утренние уведомления</Label>
              <Input id="notifyMorning" type="time" defaultValue="09:00" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="notifyEvening">Вечерние уведомления</Label>
              <Input id="notifyEvening" type="time" defaultValue="18:00" className="mt-1" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
