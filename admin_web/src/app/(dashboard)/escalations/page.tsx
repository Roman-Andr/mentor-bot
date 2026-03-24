"use client";

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
  const e = useEscalations();

  return (
    <PageContent title="Запросы эскалации" subtitle="Управление запросами на эскалацию">
      <DataTable
        loading={e.loading}
        empty={e.escalations.length === 0}
        emptyMessage="Запросы не найдены"
        currentPage={e.currentPage}
        totalPages={e.totalPages}
        totalCount={e.totalCount}
        onPageChange={e.setCurrentPage}
        header={
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                Запросы{" "}
                <span className="text-muted-foreground text-sm font-normal">({e.totalCount})</span>
              </CardTitle>
              <div className="flex gap-2">
                <SearchInput value={e.searchQuery} onChange={e.setSearchQuery} />
                <Select
                  value={e.statusFilter}
                  onChange={(ev) => e.setStatusFilter(ev.target.value)}
                  options={ESCALATION_STATUSES}
                />
                <Select
                  value={e.typeFilter}
                  onChange={(ev) => e.setTypeFilter(ev.target.value)}
                  options={ESCALATION_TYPES}
                />
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Пользователь</TableHead>
              <TableHead>Тип</TableHead>
              <TableHead>Источник</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead>Причина</TableHead>
              <TableHead>Создан</TableHead>
              <TableHead>Решён</TableHead>
              <TableHead className="w-[100px]">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {e.escalations.map((esc) => (
              <TableRow key={esc.id}>
                <TableCell>{esc.id}</TableCell>
                <TableCell>{esc.userId}</TableCell>
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
                        title="Решить"
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
