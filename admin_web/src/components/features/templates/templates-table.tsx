"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { CardHeader, CardTitle } from "@/components/ui/card";
import { MoreHorizontal, Calendar, CheckCircle, Trash2 } from "lucide-react";
import { TEMPLATE_STATUSES } from "@/lib/constants";
import type { TemplateItem } from "@/hooks/use-templates";

interface TemplatesTableProps {
  templates: TemplateItem[];
  loading: boolean;
  onEdit: (template: TemplateItem) => void;
  onPublish: (id: number) => void;
  onDelete: (id: number) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  currentPage?: number;
  totalPages?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
}

export function TemplatesTable({
  templates,
  loading,
  onEdit,
  onPublish,
  onDelete,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  currentPage,
  totalPages,
  totalCount,
  onPageChange,
}: TemplatesTableProps) {
  return (
    <DataTable
      loading={loading}
      empty={templates.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      onPageChange={onPageChange}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            Шаблоны <span className="text-muted-foreground text-sm font-normal">({totalCount ?? templates.length})</span>
          </CardTitle>
          <div className="flex gap-2">
            <SearchInput value={searchQuery} onChange={onSearchChange} />
            <Select
              value={statusFilter}
              onChange={(e) => onStatusFilterChange(e.target.value)}
              options={TEMPLATE_STATUSES}
            />
          </div>
        </div>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Название</TableHead>
            <TableHead>Отдел</TableHead>
            <TableHead>Должность</TableHead>
            <TableHead>Дней</TableHead>
            <TableHead>Задач</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead className="w-[100px]">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow
              key={template.id}
              className="hover:bg-muted cursor-pointer"
              onClick={() => onEdit(template)}
            >
              <TableCell>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{template.name}</p>
                    {template.isDefault && (
                      <Badge variant="secondary" className="text-xs">
                        По умолч.
                      </Badge>
                    )}
                  </div>
                    <p className="text-muted-foreground text-sm">{template.description}</p>
                </div>
              </TableCell>
              <TableCell>{template.department}</TableCell>
              <TableCell>{template.position}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Calendar className="text-muted-foreground size-4" />
                  {template.durationDays}
                </div>
              </TableCell>
              <TableCell>{template.taskCount}</TableCell>
              <TableCell>
                <StatusBadge status={template.status} />
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onEdit(template)}>
                    <MoreHorizontal className="size-4" />
                  </Button>
                  {template.status === "DRAFT" && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-green-500"
                      onClick={() => onPublish(template.id)}
                      title="Опубликовать"
                    >
                      <CheckCircle className="size-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(template.id)}
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
  );
}
