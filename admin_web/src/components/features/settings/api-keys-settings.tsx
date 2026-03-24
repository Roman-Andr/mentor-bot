import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Key } from "lucide-react";

export function ApiKeysSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>API ключи</CardTitle>
        <CardDescription>Управление API ключами для внешних интеграций</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <p className="font-medium">Основной ключ</p>
              <p className="text-muted-foreground font-mono text-sm">sk_live_••••••••••••</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Копировать
              </Button>
              <Button variant="outline" size="sm">
                Обновить
              </Button>
            </div>
          </div>
        </div>
        <Button variant="outline" className="gap-2">
          <Key className="size-4" />
          Создать новый ключ
        </Button>
      </CardContent>
    </Card>
  );
}
