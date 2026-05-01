"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent } from "@/components/ui/card";
import { Search, Users, FileText, BarChart3, AlertCircle } from "lucide-react";
import type { SearchSummary } from "@/types";

interface SearchSummaryCardsProps {
  summary: SearchSummary | null;
}

export function SearchSummaryCards({ summary }: SearchSummaryCardsProps) {
  const t = useTranslations();

  if (!summary) return null;

  return (
    <div className="grid gap-4 md:grid-cols-5">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.search.totalSearches")}</p>
              <p className="text-2xl font-bold">{summary.total_searches}</p>
            </div>
            <Search className="size-8 text-blue-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.search.uniqueUsers")}</p>
              <p className="text-2xl font-bold">{summary.unique_users}</p>
            </div>
            <Users className="size-8 text-purple-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.search.uniqueQueries")}</p>
              <p className="text-2xl font-bold">{summary.unique_queries}</p>
            </div>
            <FileText className="size-8 text-green-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.search.avgResults")}</p>
              <p className="text-2xl font-bold">{summary.avg_results_per_search.toFixed(1)}</p>
            </div>
            <BarChart3 className="size-8 text-yellow-500" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">{t("analytics.search.zeroResultsPercent")}</p>
              <p className="text-2xl font-bold">{summary.zero_results_percentage.toFixed(1)}%</p>
            </div>
            <AlertCircle className="size-8 text-red-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
