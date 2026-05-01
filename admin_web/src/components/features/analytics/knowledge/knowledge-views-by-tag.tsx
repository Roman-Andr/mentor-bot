"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TagStats {
  tag_id: number;
  tag_name: string;
  view_count: number;
}

interface KnowledgeViewsByTagProps {
  data: TagStats[];
}

export function KnowledgeViewsByTag({ data }: KnowledgeViewsByTagProps) {
  const t = useTranslations();

  const chartData = data.slice(0, 10).map((item) => ({
    name: item.tag_name,
    views: item.view_count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.knowledge.byTag")}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="views" name={t("analytics.knowledge.views")} fill="#8B5CF6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
