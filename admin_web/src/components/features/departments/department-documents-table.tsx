"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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
import { TableActions, buildEditAction, buildDeleteAction } from "@/components/shared";
import { DepartmentDocumentDownloadButton } from "./department-document-download-button";
import { DOCUMENT_CATEGORIES } from "@/lib/constants";
import type { DepartmentDocument } from "@/types/department-document";
import { useDepartments } from "@/hooks/use-departments";

interface DepartmentDocumentsTableProps {
  documents: DepartmentDocument[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  categoryFilter?: string;
  onCategoryFilterChange: (category: string | undefined) => void;
  departmentFilter?: number;
  onDepartmentFilterChange: (departmentId: number | undefined) => void;
  onEdit: (document: DepartmentDocument) => void;
  onDelete: (id: number) => void;
}

export function DepartmentDocumentsTable({
  documents,
  loading,
  searchQuery,
  onSearchChange,
  categoryFilter,
  onCategoryFilterChange,
  departmentFilter,
  onDepartmentFilterChange,
  onEdit,
  onDelete,
}: DepartmentDocumentsTableProps) {
  const t = useTranslations();
  const { items: departments } = useDepartments();

  const getCategoryLabel = (category: string) => {
    return DOCUMENT_CATEGORIES.find((c) => c.value === category)?.label || category;
  };

  const getDepartmentName = (departmentId: number) => {
    return departments.find((d) => d.id === departmentId)?.name || "Неизвестно";
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <DataTable loading={loading} empty={documents.length === 0} header={
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <CardTitle>Документы департаментов</CardTitle>
          <div className="flex gap-2">
            <Select
              value={departmentFilter?.toString() || "all"}
              onValueChange={(value) => onDepartmentFilterChange(value === "all" ? undefined : parseInt(value, 10))}
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Все департаменты" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все департаменты</SelectItem>
                {departments.map((dept) => (
                  <SelectItem key={dept.id} value={dept.id.toString()}>
                    {dept.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={categoryFilter || "all"}
              onValueChange={(value) => onCategoryFilterChange(value === "all" ? undefined : value)}
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Все категории" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все категории</SelectItem>
                {DOCUMENT_CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <SearchInput placeholder="Поиск по названию" value={searchQuery} onChange={onSearchChange} />
          </div>
        </div>
      </CardHeader>
    }>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Название</TableHead>
            <TableHead>Категория</TableHead>
            <TableHead>Департамент</TableHead>
            <TableHead>Файл</TableHead>
            <TableHead>Размер</TableHead>
            <TableHead>Загружен</TableHead>
            <TableHead>Видимость</TableHead>
            <TableHead className="w-25">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((document) => (
            <TableRow key={document.id}>
              <TableCell>
                <span className="font-medium">{document.title}</span>
                {document.description && (
                  <p className="text-sm text-muted-foreground max-w-75 truncate">{document.description}</p>
                )}
              </TableCell>
              <TableCell>{getCategoryLabel(document.category)}</TableCell>
              <TableCell>{getDepartmentName(document.department_id)}</TableCell>
              <TableCell>
                <DepartmentDocumentDownloadButton
                  documentId={document.id}
                  fileName={document.file_name}
                />
              </TableCell>
              <TableCell>{formatFileSize(document.file_size)}</TableCell>
              <TableCell>{new Date(document.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                {document.is_public ? (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Публичный</span>
                ) : (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Только отдел</span>
                )}
              </TableCell>
              <TableCell>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(document)),
                    buildDeleteAction(() => onDelete(document.id)),
                  ]}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}
