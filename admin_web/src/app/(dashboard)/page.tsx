"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Users,
  FileCheck,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
} from "lucide-react";
import { api, OnboardingProgress } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface Activity {
  user: string;
  action: string;
  task: string;
  time: string;
}

export default function DashboardPage() {
  const { isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState({
    total_users: 0,
    active_newbies: 0,
    completed_onboarding: 0,
    pending_tasks: 0,
    overdue_tasks: 0,
    average_completion_days: 0,
  });
  const [progress, setProgress] = useState<OnboardingProgress[]>([]);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;

    async function fetchData() {
      try {
        const [checklistResult, usersResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
        ]);

        if (checklistResult.data) {
          const cs = checklistResult.data;
          setStats({
            total_users: usersResult.data?.total || 0,
            active_newbies: cs.in_progress || 0,
            completed_onboarding: cs.completed || 0,
            pending_tasks: cs.not_started || 0,
            overdue_tasks: cs.overdue || 0,
            average_completion_days: Math.round(cs.avg_completion_days) || 0,
          });
        }

        const onboardingResult = await api.analytics.onboardingProgress();
        if (onboardingResult.data) {
          const data = onboardingResult.data as unknown as {
            checklists?: Array<{
              user_id: number;
              employee_id?: string;
              department?: string;
              start_date: string;
              progress_percentage: number;
              days_remaining?: number;
              status: string;
            }>;
          };
          const checklists = data.checklists || [];
          setProgress(
            checklists.slice(0, 5).map((c) => ({
              user_id: c.user_id,
              user_name: c.employee_id || `User ${c.user_id}`,
              department: c.department || "Unknown",
              start_date: c.start_date,
              completion_percentage: c.progress_percentage,
              days_remaining: c.days_remaining || 0,
              status: c.status,
            })),
          );
        }

        setActivity([
          {
            user: "Система",
            action: "Загрузила данные",
            task: "Дашборд обновлён",
            time: "Сейчас",
          },
        ]);
      } catch (err) {
        setError("Ошибка загрузки данных");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [authLoading]);

  const statsData = [
    {
      title: "Всего пользователей",
      value: stats.total_users.toString(),
      change: "",
      changeType: "neutral",
      icon: Users,
      color: "bg-blue-500",
    },
    {
      title: "Новички в процессе",
      value: stats.active_newbies.toString(),
      change: "",
      changeType: "neutral",
      icon: Clock,
      color: "bg-yellow-500",
    },
    {
      title: "Завершили онбординг",
      value: stats.completed_onboarding.toString(),
      change: "",
      changeType: "neutral",
      icon: CheckCircle,
      color: "bg-green-500",
    },
    {
      title: "Просроченные задачи",
      value: stats.overdue_tasks.toString(),
      change: "",
      changeType: stats.overdue_tasks > 0 ? "negative" : "neutral",
      icon: AlertTriangle,
      color: "bg-red-500",
    },
  ];

  if (loading || authLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
            <p className="text-gray-500">Обзор процесса онбординга</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
            <p className="text-gray-500">Обзор процесса онбординга</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-red-500">{error}</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
          <p className="text-gray-500">Обзор процесса онбординга</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <TrendingUp className="w-4 h-4" />
          <span>Обновлено: {new Date().toLocaleDateString("ru-RU")}</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsData.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.color}`}>
                <stat.icon className="w-4 h-4 text-white" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              {stat.change && (
                <p className="text-xs text-gray-500 mt-1">
                  <span
                    className={
                      stat.changeType === "positive"
                        ? "text-green-600"
                        : "text-red-600"
                    }
                  >
                    {stat.change}
                  </span>{" "}
                  за последний месяц
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Прогресс онбординга</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {progress.length > 0 ? (
                progress.map((item) => (
                  <div key={item.user_id} className="flex items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-medium truncate">
                          {item.user_name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {item.completion_percentage}%
                        </p>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            item.completion_percentage >= 80
                              ? "bg-green-500"
                              : item.completion_percentage >= 50
                                ? "bg-yellow-500"
                                : "bg-red-500"
                          }`}
                          style={{ width: `${item.completion_percentage}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {item.days_remaining} дн.
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">
                  Нет данных о прогрессе
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Последняя активность</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activity.map((item, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-2 h-2 mt-2 rounded-full bg-blue-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">
                      {item.user}{" "}
                      <span className="text-gray-500 font-normal">
                        {item.action}
                      </span>
                    </p>
                    <p className="text-xs text-gray-500">{item.task}</p>
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {item.time}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>По отделам</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats && stats.total_users > 0 ? (
                <>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                      <span className="text-sm">Разработка</span>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(stats.total_users * 0.4)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-purple-500" />
                      <span className="text-sm">Дизайн</span>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(stats.total_users * 0.2)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-pink-500" />
                      <span className="text-sm">Маркетинг</span>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(stats.total_users * 0.15)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                      <span className="text-sm">QA</span>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(stats.total_users * 0.15)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-orange-500" />
                      <span className="text-sm">HR</span>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(stats.total_users * 0.1)}
                    </span>
                  </div>
                </>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">
                  Нет данных
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Среднее время онбординга</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-4">
              <div className="text-4xl font-bold text-blue-600">
                {stats?.average_completion_days || 0}
              </div>
              <p className="text-sm text-gray-500 mt-2">дней в среднем</p>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Мин.</span>
                <span>7 дней</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Макс.</span>
                <span>35 дней</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Эскалации</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="text-sm text-red-700">К HR</span>
                <span className="font-bold text-red-700">-</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <span className="text-sm text-yellow-700">К наставнику</span>
                <span className="font-bold text-yellow-700">-</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm text-blue-700">В работе</span>
                <span className="font-bold text-blue-700">-</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
