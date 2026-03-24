import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function SecuritySettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Настройки безопасности</CardTitle>
        <CardDescription>Настройки безопасности и доступа</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="sessionTimeout">Тайм-аут сессии (минуты)</Label>
          <Input id="sessionTimeout" type="number" defaultValue="60" className="mt-1 w-32" />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Двухфакторная аутентификация</p>
            <p className="text-muted-foreground text-sm">Требовать 2FA для всех пользователей</p>
          </div>
          <input type="checkbox" className="toggle" />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Журналирование действий</p>
            <p className="text-muted-foreground text-sm">Вести журнал всех действий пользователей</p>
          </div>
          <input type="checkbox" defaultChecked className="toggle" />
        </div>
      </CardContent>
    </Card>
  );
}
