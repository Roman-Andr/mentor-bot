"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertCircle } from "lucide-react";
import type { ZeroResultQuery } from "@/types";

interface SearchZeroResultsTableProps {
  data: ZeroResultQuery[];
}

export function SearchZeroResultsTable({ data }: SearchZeroResultsTableProps) {
  const t = useTranslations();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>{t("analytics.search.zeroResults")}</CardTitle>
          <AlertCircle className="size-5 text-red-500" />
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("analytics.search.query")}</TableHead>
              <TableHead className="text-right">{t("analytics.search.count")}</TableHead>
              <TableHead className="text-right">{t("analytics.search.lastSearched")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="text-muted-foreground text-center">
                  {t("common.noData")}
                </TableCell>
              </TableRow>
            ) : (
              data.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.query}</TableCell>
                  <TableCell className="text-right">{item.count}</TableCell>
                  <TableCell className="text-right">{formatDate(item.last_searched_at)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
