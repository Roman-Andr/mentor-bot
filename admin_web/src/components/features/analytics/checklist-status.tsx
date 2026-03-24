"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChecklistStats } from "@/lib/api";

interface ChecklistStatusProps {
  stats: ChecklistStats | null;
}

export function ChecklistStatus({ stats }: ChecklistStatusProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Статус чек-листов</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-green-50 p-3">
            <span className="text-sm text-green-700">Завершено</span>
            <span className="font-bold text-green-700">{stats?.completed || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-blue-50 p-3">
            <span className="text-sm text-blue-700">В процессе</span>
            <span className="font-bold text-blue-700">{stats?.in_progress || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-yellow-50 p-3">
            <span className="text-sm text-yellow-700">Не начато</span>
            <span className="font-bold text-yellow-700">{stats?.not_started || 0}</span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-red-50 p-3">
            <span className="text-sm text-red-700">Просрочено</span>
            <span className="font-bold text-red-700">{stats?.overdue || 0}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
