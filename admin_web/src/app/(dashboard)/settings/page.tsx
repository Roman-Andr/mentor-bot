"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { useToast } from "@/components/ui/toast";
import { Settings, Bell, Shield, Palette, Database, Key, Save } from "lucide-react";
import { GeneralSettings } from "@/components/features/settings/general-settings";
import { NotificationSettings } from "@/components/features/settings/notification-settings";
import { SecuritySettings } from "@/components/features/settings/security-settings";
import { AppearanceSettings } from "@/components/features/settings/appearance-settings";
import { IntegrationsSettings } from "@/components/features/settings/integrations-settings";
import { ApiKeysSettings } from "@/components/features/settings/api-keys-settings";

const tabs = [
  { id: "general", label: "Общие", icon: Settings },
  { id: "notifications", label: "Уведомления", icon: Bell },
  { id: "security", label: "Безопасность", icon: Shield },
  { id: "appearance", label: "Внешний вид", icon: Palette },
  { id: "integrations", label: "Интеграции", icon: Database },
  { id: "api", label: "API ключи", icon: Key },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general");
  const { toast } = useToast();

  const handleSave = () => {
    toast("Настройки сохранены", "success");
  };

  return (
    <div className="space-y-6 p-6">
      <PageHeader title="Настройки" subtitle="Настройка параметров системы" />

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="md:col-span-1">
          <CardContent className="p-4">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                    activeTab === tab.id
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                      : "text-muted-foreground hover:bg-muted"
                  }`}
                >
                  <tab.icon className="size-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </CardContent>
        </Card>

        <div className="space-y-6 md:col-span-3">
          {activeTab === "general" && <GeneralSettings />}
          {activeTab === "notifications" && <NotificationSettings />}
          {activeTab === "security" && <SecuritySettings />}
          {activeTab === "appearance" && <AppearanceSettings />}
          {activeTab === "integrations" && <IntegrationsSettings />}
          {activeTab === "api" && <ApiKeysSettings />}

          <div className="flex justify-end gap-2">
            <Button variant="outline">Отмена</Button>
            <Button className="gap-2" onClick={handleSave}>
              <Save className="size-4" />
              Сохранить изменения
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
