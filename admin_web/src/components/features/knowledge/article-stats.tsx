import { StatsGrid } from "@/components/ui/stat-card";
import { BookOpen, Eye, Pin, Star } from "lucide-react";

interface ArticleStatsArticle {
  status: string;
  isPinned: boolean;
  isFeatured: boolean;
}

interface ArticleStatsProps {
  articles: ArticleStatsArticle[];
}

export function ArticleStats({ articles }: ArticleStatsProps) {
  const published = articles.filter((a) => a.status === "PUBLISHED").length;
  const pinned = articles.filter((a) => a.isPinned).length;
  const featured = articles.filter((a) => a.isFeatured).length;

  return (
    <StatsGrid
      stats={[
        { label: "Всего статей", value: articles.length, icon: BookOpen },
        { label: "Опубликовано", value: published, icon: Eye },
        { label: "Закреплённых", value: pinned, icon: Pin },
        { label: "Избранных", value: featured, icon: Star },
      ]}
    />
  );
}
