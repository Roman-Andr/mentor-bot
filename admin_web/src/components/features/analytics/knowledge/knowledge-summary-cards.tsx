"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent } from "@/components/ui/card";
import { Eye, Users, FileText, TrendingUp } from "lucide-react";

interface KnowledgeSummary {
  total_views: number;
  unique_viewers: number;
  total_articles: number;
  avg_views_per_article: number;
}

interface KnowledgeSummaryCardsProps {
  summary: KnowledgeSummary | null;
}

export function KnowledgeSummaryCards({ summary }: KnowledgeSummaryCardsProps) {
  const t = useTranslations();

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.knowledge.totalViews")}</p>
              <p className="text-2xl font-bold">{summary?.total_views || 0}</p>
            </div>
            <Eye className="size-8 text-blue-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.knowledge.uniqueViewers")}</p>
              <p className="text-2xl font-bold">{summary?.unique_viewers || 0}</p>
            </div>
            <Users className="size-8 text-purple-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.knowledge.totalArticles")}</p>
              <p className="text-2xl font-bold">{summary?.total_articles || 0}</p>
            </div>
            <FileText className="size-8 text-green-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.knowledge.avgViewsPerArticle")}</p>
              <p className="text-2xl font-bold">{summary?.avg_views_per_article.toFixed(1) || "0.0"}</p>
            </div>
            <TrendingUp className="size-8 text-yellow-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
