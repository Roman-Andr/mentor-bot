"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { TrendingUp, Users, Clock, CheckCircle, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, ChecklistStats } from "@/lib/api";

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [userCount, setUserCount] = useState(0);

  const monthlyData = [
    { month: "Сен", newUsers: 12, completed: 8 },
    { month: "Окт", newUsers: 18, completed: 14 },
    { month: "Ноя", newUsers: 15, completed: 12 },
    { month: "Дек", newUsers: 22, completed: 18 },
    { month: "Янв", newUsers: 28, completed: 20 },
    { month: "Фев", newUsers: 25, completed: 22 },
    { month: "Мар", newUsers: 20, completed: 15 },
  ];

  const completionTimeData = [
    { range: "1-7 дней", count: 15 },
    { range: "8-14 дней", count: 28 },
    { range: "15-21 дней", count: 35 },
    { range: "22-30 дней", count: 18 },
    { range: ">30 дней", count: 8 },
  ];

  useEffect(() => {
    async function loadData() {
      try {
        const [statsResult, usersResult] = await Promise.all([
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
        ]);

        if (statsResult.data) {
          setStats(statsResult.data);
        }
        if (usersResult.data) {
          setUserCount(usersResult.data.total);
        }
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const departmentData = stats?.by_department
    ? Object.entries(stats.by_department).map(([name, value], index) => ({
        name,
        value,
        color: ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444"][
          index % 5
        ],
      }))
    : [
        { name: "Разработка", value: 45, color: "#3B82F6" },
        { name: "Дизайн", value: 18, color: "#8B5CF6" },
        { name: "QA", value: 15, color: "#10B981" },
        { name: "Маркетинг", value: 22, color: "#F59E0B" },
      ];

  const handleExport = () => {
    const csvContent = [
      ["Метрика", "Значение"],
      ["Всего новичков", stats?.total || userCount],
      ["Завершено", stats?.completed || 0],
      ["В процессе", stats?.in_progress || 0],
      ["Просрочено", stats?.overdue || 0],
      ["Среднее время (дней)", stats?.avg_completion_days || 0],
      ["Процент завершения", stats?.completion_rate || 0],
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "analytics_export.csv";
    link.click();
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Аналитика</h1>
            <p className="text-gray-500">Статистика и отчёты по онбордингу</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Аналитика</h1>
          <p className="text-gray-500">Статистика и отчёты по онбордингу</p>
        </div>
        <Button className="gap-2" onClick={handleExport}>
          <Download className="w-4 h-4" />
          Экспорт в CSV
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Всего новичков</p>
                <p className="text-2xl font-bold">
                  {stats?.total || userCount}
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Среднее время</p>
                <p className="text-2xl font-bold">
                  {Math.round(stats?.avg_completion_days || 0)} дней
                </p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Успешных завершений</p>
                <p className="text-2xl font-bold">
                  {Math.round(stats?.completion_rate || 0)}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">В процессе</p>
                <p className="text-2xl font-bold">{stats?.in_progress || 0}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Динамика онбординга по месяцам</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar
                  dataKey="newUsers"
                  name="Новые"
                  fill="#3B82F6"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="completed"
                  name="Завершили"
                  fill="#10B981"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Распределение по отделам</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={departmentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {departmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Время завершения онбординга</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={completionTimeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="range" type="category" width={100} />
                <Tooltip />
                <Bar
                  dataKey="count"
                  name="Количество"
                  fill="#8B5CF6"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Статус чек-листов</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm text-green-700">Завершено</span>
                <span className="font-bold text-green-700">
                  {stats?.completed || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm text-blue-700">В процессе</span>
                <span className="font-bold text-blue-700">
                  {stats?.in_progress || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <span className="text-sm text-yellow-700">Не начато</span>
                <span className="font-bold text-yellow-700">
                  {stats?.not_started || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="text-sm text-red-700">Просрочено</span>
                <span className="font-bold text-red-700">
                  {stats?.overdue || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
