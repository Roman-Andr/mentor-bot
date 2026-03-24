import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";

export function GeneralSettings() {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Основные настройки</CardTitle>
          <CardDescription>Общие параметры системы онбординга</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="companyName">Название компании</Label>
              <Input id="companyName" defaultValue="ООО Компания" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="timezone">Часовой пояс</Label>
              <Select
                id="timezone"
                className="mt-1"
                options={[
                  { value: "Europe/Moscow", label: "Москва (UTC+3)" },
                  { value: "Europe/Kaliningrad", label: "Калининград (UTC+2)" },
                  { value: "Europe/Samara", label: "Самара (UTC+4)" },
                ]}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="defaultDuration">Длительность онбординга по умолчанию (дней)</Label>
            <Input id="defaultDuration" type="number" defaultValue="30" className="mt-1 w-32" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Автоматическое назначение наставников</p>
              <p className="text-muted-foreground text-sm">
                Автоматически назначать наставника новому сотруднику
              </p>
            </div>
            <input type="checkbox" defaultChecked className="toggle" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Интеграция с Telegram</CardTitle>
          <CardDescription>Настройки Telegram бота</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="botToken">Telegram Bot Token</Label>
            <Input
              id="botToken"
              type="password"
              defaultValue="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="botUsername">Имя бота</Label>
            <Input id="botUsername" defaultValue="@CompanyMentorBot" className="mt-1" />
          </div>
        </CardContent>
      </Card>
    </>
  );
}
