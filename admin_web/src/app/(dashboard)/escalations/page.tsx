"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SearchInput } from "@/components/ui/search-input";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Trash2 } from "lucide-react";
import { ESCALATION_STATUSES, ESCALATION_TYPES } from "@/lib/constants";
import { formatDateTime } from "@/lib/utils";
import { useEscalations } from "@/hooks/use-escalations";

export default function EscalationsPage() {
  const t = useTranslations();
  const e = useEscalations();

  return (
    <PageContent title={t("escalations.title")} subtitle={t("escalations.title")}>
      <DataTable
        loading={e.loading}
        empty={e.escalations.length === 0}
        emptyMessage={t("common.noData")}
        currentPage={e.currentPage}
        totalPages={e.totalPages}
        totalCount={e.totalCount}
        pageSize={e.pageSize}
        onPageChange={e.setCurrentPage}
        onPageSizeChange={e.setPageSize}
        showPageSizeSelector={true}
        header={
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                {t("escalations.title")}{" "}
                <span className="text-muted-foreground text-sm font-normal">({e.totalCount})</span>
              </CardTitle>
              <div className="flex gap-2">
                <SearchInput value={e.searchQuery} onChange={e.setSearchQuery} />
                <Select
                  value={e.statusFilter}
                  onChange={e.setStatusFilter}
                  options={ESCALATION_STATUSES}
                />
                <Select
                  value={e.typeFilter}
                  onChange={e.setTypeFilter}
                  options={ESCALATION_TYPES}
                />
                <Button variant="outline" onClick={e.resetFilters}>
                  {t("common.clear")}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>{t("escalations.assignedTo")}</TableHead>
              <TableHead>{t("escalations.subject")}</TableHead>
              <TableHead>{t("escalations.description")}</TableHead>
              <TableHead>{t("escalations.status")}</TableHead>
              <TableHead>{t("escalations.priority")}</TableHead>
              <TableHead>{t("escalations.createdAt")}</TableHead>
              <TableHead>{t("escalations.resolvedAt")}</TableHead>
              <TableHead className="w-25">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {e.escalations.map((esc) => (
              <TableRow key={esc.id}>
                <TableCell>{esc.id}</TableCell>
                <TableCell>{e.getUserName(esc.userId)}</TableCell>
                <TableCell>{esc.type}</TableCell>
                <TableCell>{esc.source}</TableCell>
                <TableCell>
                  <StatusBadge status={esc.status} />
                </TableCell>
                <TableCell>
                  <span className="line-clamp-2 max-w-48">{esc.reason || "-"}</span>
                </TableCell>
                <TableCell>{formatDateTime(esc.createdAt)}</TableCell>
                <TableCell>{formatDateTime(esc.resolvedAt)}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    {esc.status !== "RESOLVED" && esc.status !== "CLOSED" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-green-500"
                        onClick={() => e.handleResolve(esc.id)}
                        title={t("common.confirm")}
                      >
                        <CheckCircle className="size-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500"
                      onClick={() => e.handleDelete(esc.id)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
