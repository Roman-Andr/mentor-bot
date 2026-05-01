"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TopArticleStats {
  article_id: number;
  title: string;
  view_count: number;
  unique_viewers: number;
}

interface KnowledgeTopArticlesChartProps {
  data: TopArticleStats[];
}

export function KnowledgeTopArticlesChart({ data }: KnowledgeTopArticlesChartProps) {
  const t = useTranslations();

  const chartData = data.map((item) => ({
    title: item.title.length > 30 ? item.title.substring(0, 30) + "..." : item.title,
    views: item.view_count,
    uniqueViewers: item.unique_viewers,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.knowledge.topArticles")}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="title" type="category" width={200} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="views" name={t("analytics.knowledge.views")} fill="#3B82F6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
