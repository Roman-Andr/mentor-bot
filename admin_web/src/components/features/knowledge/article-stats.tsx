import { useTranslations } from "next-intl";
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
  const t = useTranslations("knowledge");

  const published = articles.filter((a) => a.status === "PUBLISHED").length;
  const pinned = articles.filter((a) => a.isPinned).length;
  const featured = articles.filter((a) => a.isFeatured).length;

  return (
    <StatsGrid
      stats={[
        { label: t("totalArticles") || "Total Articles", value: articles.length, icon: BookOpen },
        { label: t("published") || "Published", value: published, icon: Eye },
        { label: t("pinned") || "Pinned", value: pinned, icon: Pin },
        { label: t("featured") || "Featured", value: featured, icon: Star },
      ]}
    />
  );
}
