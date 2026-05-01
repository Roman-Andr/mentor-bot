"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { TopQueryStats } from "@/types";

interface SearchTopQueriesTableProps {
  data: TopQueryStats[];
}

export function SearchTopQueriesTable({ data }: SearchTopQueriesTableProps) {
  const t = useTranslations();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("analytics.search.topQueries")}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("analytics.search.query")}</TableHead>
              <TableHead className="text-right">{t("analytics.search.count")}</TableHead>
              <TableHead className="text-right">{t("analytics.search.avgResults")}</TableHead>
              <TableHead className="text-right">{t("analytics.search.zeroResultsCount")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  {t("common.noData")}
                </TableCell>
              </TableRow>
            ) : (
              data.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.query}</TableCell>
                  <TableCell className="text-right">{item.count}</TableCell>
                  <TableCell className="text-right">{item.avg_results_count.toFixed(1)}</TableCell>
                  <TableCell className="text-right">{item.zero_results_count}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
