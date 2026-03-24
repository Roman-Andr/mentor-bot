"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface CompletionTimeData {
  range: string;
  count: number;
}

interface CompletionTimeChartProps {
  data: CompletionTimeData[];
}

export function CompletionTimeChart({ data }: CompletionTimeChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Время завершения онбординга</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="range" type="category" width={100} />
            <Tooltip />
            <Bar dataKey="count" name="Количество" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
