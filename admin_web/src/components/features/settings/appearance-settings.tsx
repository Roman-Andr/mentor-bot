"use client";

import { useTheme } from "next-themes";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

const themes = [
  { value: "light" as const, label: "Светлая" },
  { value: "dark" as const, label: "Тёмная" },
  { value: "system" as const, label: "Системная" },
];

export function AppearanceSettings() {
  const { theme, setTheme } = useTheme();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Внешний вид</CardTitle>
        <CardDescription>Настройки оформления интерфейса</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label>Тема</Label>
          <div className="mt-2 flex gap-4">
            {themes.map((t) => (
              <label key={t.value} className="flex cursor-pointer items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value={t.value}
                  checked={theme === t.value}
                  onChange={() => setTheme(t.value)}
                  className="accent-primary"
                />
                <span>{t.label}</span>
              </label>
            ))}
          </div>
        </div>
        <div>
          <Label>Цветовая схема</Label>
          <div className="mt-2 flex gap-3">
            <button
              className={cn(
                "size-8 cursor-pointer rounded-full border-2 border-blue-700 bg-blue-500",
              )}
            />
            <button className="border-border size-8 cursor-pointer rounded-full border bg-green-500" />
            <button className="border-border size-8 cursor-pointer rounded-full border bg-purple-500" />
            <button className="border-border size-8 cursor-pointer rounded-full border bg-red-500" />
          </div>
        </div>
        <div>
          <Label>Логотип компании</Label>
          <div className="mt-2 rounded-lg border-2 border-dashed p-4 text-center">
            <p className="text-muted-foreground text-sm">
              Перетащите файл или нажмите для загрузки
            </p>
            <p className="text-muted-foreground mt-1 text-xs">PNG, JPG до 2MB</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
