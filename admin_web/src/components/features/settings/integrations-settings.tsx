import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function IntegrationsSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Интеграции</CardTitle>
        <CardDescription>Подключение внешних сервисов</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="flex items-center gap-4">
            <div className="flex size-10 items-center justify-center rounded-lg bg-blue-100 font-bold text-blue-600">
              G
            </div>
            <div>
              <p className="font-medium">Google Workspace</p>
              <p className="text-muted-foreground text-sm">Календарь, почта, документы</p>
            </div>
          </div>
          <Button variant="outline" size="sm">
            Подключить
          </Button>
        </div>
        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="flex items-center gap-4">
            <div className="flex size-10 items-center justify-center rounded-lg bg-green-100 font-bold text-green-600">
              S
            </div>
            <div>
              <p className="font-medium">Slack</p>
              <p className="text-muted-foreground text-sm">Уведомления и сообщения</p>
            </div>
          </div>
          <Button variant="outline" size="sm">
            Подключить
          </Button>
        </div>
        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="flex items-center gap-4">
            <div className="flex size-10 items-center justify-center rounded-lg bg-blue-100 font-bold text-blue-600">
              T
            </div>
            <div>
              <p className="font-medium">Telegram</p>
              <p className="text-muted-foreground text-sm">Telegram бот для уведомлений</p>
            </div>
          </div>
          <Badge>Подключено</Badge>
        </div>
        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="flex items-center gap-4">
            <div className="flex size-10 items-center justify-center rounded-lg bg-yellow-100 font-bold text-yellow-600">
              H
            </div>
            <div>
              <p className="font-medium">HRM система</p>
              <p className="text-muted-foreground text-sm">Интеграция с HRM</p>
            </div>
          </div>
          <Button variant="outline" size="sm">
            Подключить
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
