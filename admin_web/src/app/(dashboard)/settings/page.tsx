"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Settings,
  Bell,
  Shield,
  Palette,
  Database,
  Key,
  Save,
} from "lucide-react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general");

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Настройки</h1>
        <p className="text-gray-500">Настройка параметров системы</p>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="md:col-span-1">
          <CardContent className="p-4">
            <nav className="space-y-1">
              {[
                { id: "general", label: "Общие", icon: Settings },
                { id: "notifications", label: "Уведомления", icon: Bell },
                { id: "security", label: "Безопасность", icon: Shield },
                { id: "appearance", label: "Внешний вид", icon: Palette },
                { id: "integrations", label: "Интеграции", icon: Database },
                { id: "api", label: "API ключи", icon: Key },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeTab === tab.id
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </CardContent>
        </Card>

        <div className="md:col-span-3 space-y-6">
          {activeTab === "general" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Основные настройки</CardTitle>
                  <CardDescription>
                    Общие параметры системы онбординга
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="companyName">Название компании</Label>
                      <Input
                        id="companyName"
                        defaultValue="ООО Компания"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="timezone">Часовой пояс</Label>
                      <select
                        id="timezone"
                        className="flex h-9 w-full mt-1 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                      >
                        <option value="Europe/Moscow">Москва (UTC+3)</option>
                        <option value="Europe/Kaliningrad">
                          Калининград (UTC+2)
                        </option>
                        <option value="Europe/Samara">Самара (UTC+4)</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="defaultDuration">
                      Длительность онбординга по умолчанию (дней)
                    </Label>
                    <Input
                      id="defaultDuration"
                      type="number"
                      defaultValue="30"
                      className="mt-1 w-32"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">
                        Автоматическое назначение наставников
                      </p>
                      <p className="text-sm text-gray-500">
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
                    <Input
                      id="botUsername"
                      defaultValue="@CompanyMentorBot"
                      className="mt-1"
                    />
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {activeTab === "notifications" && (
            <Card>
              <CardHeader>
                <CardTitle>Настройки уведомлений</CardTitle>
                <CardDescription>
                  Настройка каналов и расписания уведомлений
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Email уведомления</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Напоминания о задачах</p>
                        <p className="text-sm text-gray-500">
                          Отправлять email напоминания о предстоящих задачах
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="toggle"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Уведомления о встречах</p>
                        <p className="text-sm text-gray-500">
                          Отправлять напоминания о запланированных встречах
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="toggle"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Ежедневный дайджест</p>
                        <p className="text-sm text-gray-500">
                          Отправлять ежедневную сводку о прогрессе
                        </p>
                      </div>
                      <input type="checkbox" className="toggle" />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium">Время отправки</h4>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="notifyMorning">
                        Утренние уведомления
                      </Label>
                      <Input
                        id="notifyMorning"
                        type="time"
                        defaultValue="09:00"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="notifyEvening">
                        Вечерние уведомления
                      </Label>
                      <Input
                        id="notifyEvening"
                        type="time"
                        defaultValue="18:00"
                        className="mt-1"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "security" && (
            <Card>
              <CardHeader>
                <CardTitle>Настройки безопасности</CardTitle>
                <CardDescription>
                  Настройки безопасности и доступа
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="sessionTimeout">
                    Тайм-аут сессии (минуты)
                  </Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    defaultValue="60"
                    className="mt-1 w-32"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Двухфакторная аутентификация</p>
                    <p className="text-sm text-gray-500">
                      Требовать 2FA для всех пользователей
                    </p>
                  </div>
                  <input type="checkbox" className="toggle" />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Журналирование действий</p>
                    <p className="text-sm text-gray-500">
                      Вести журнал всех действий пользователей
                    </p>
                  </div>
                  <input type="checkbox" defaultChecked className="toggle" />
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "appearance" && (
            <Card>
              <CardHeader>
                <CardTitle>Внешний вид</CardTitle>
                <CardDescription>
                  Настройки оформления интерфейса
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label>Тема</Label>
                  <div className="flex gap-4 mt-2">
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="theme"
                        defaultChecked
                        className="toggle"
                      />
                      <span>Светлая</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input type="radio" name="theme" className="toggle" />
                      <span>Тёмная</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <input type="radio" name="theme" className="toggle" />
                      <span>Системная</span>
                    </div>
                  </div>
                </div>
                <div>
                  <Label>Цветовая схема</Label>
                  <div className="flex gap-3 mt-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500 border-2 border-blue-700 cursor-pointer"></div>
                    <div className="w-8 h-8 rounded-full bg-green-500 border border-gray-300 cursor-pointer"></div>
                    <div className="w-8 h-8 rounded-full bg-purple-500 border border-gray-300 cursor-pointer"></div>
                    <div className="w-8 h-8 rounded-full bg-red-500 border border-gray-300 cursor-pointer"></div>
                  </div>
                </div>
                <div>
                  <Label>Логотип компании</Label>
                  <div className="mt-2 p-4 border-2 border-dashed rounded-lg text-center">
                    <p className="text-sm text-gray-500">
                      Перетащите файл или нажмите для загрузки
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      PNG, JPG до 2MB
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "integrations" && (
            <Card>
              <CardHeader>
                <CardTitle>Интеграции</CardTitle>
                <CardDescription>Подключение внешних сервисов</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold">
                      G
                    </div>
                    <div>
                      <p className="font-medium">Google Workspace</p>
                      <p className="text-sm text-gray-500">
                        Календарь, почта, документы
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Подключить
                  </Button>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-bold">
                      S
                    </div>
                    <div>
                      <p className="font-medium">Slack</p>
                      <p className="text-sm text-gray-500">
                        Уведомления и сообщения
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Подключить
                  </Button>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold">
                      T
                    </div>
                    <div>
                      <p className="font-medium">Telegram</p>
                      <p className="text-sm text-gray-500">
                        Telegram бот для уведомлений
                      </p>
                    </div>
                  </div>
                  <Badge>Подключено</Badge>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center text-yellow-600 font-bold">
                      H
                    </div>
                    <div>
                      <p className="font-medium">HRM система</p>
                      <p className="text-sm text-gray-500">Интеграция с HRM</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Подключить
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "api" && (
            <Card>
              <CardHeader>
                <CardTitle>API ключи</CardTitle>
                <CardDescription>
                  Управление API ключами для внешних интеграций
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Основной ключ</p>
                      <p className="text-sm text-gray-500 font-mono">
                        sk_live_••••••••••••
                      </p>
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
                  <Key className="w-4 h-4" />
                  Создать новый ключ
                </Button>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline">Отмена</Button>
            <Button className="gap-2">
              <Save className="w-4 h-4" />
              Сохранить изменения
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
