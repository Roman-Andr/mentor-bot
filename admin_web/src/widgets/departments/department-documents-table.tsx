"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import { TableActions, buildEditAction, buildDeleteAction } from "@/shared/components";
import { DepartmentDocumentDownloadButton } from "./department-document-download-button";
import { getDocumentCategoryOptions } from "@/shared/lib/constants";
import type { DepartmentDocument } from "@/shared/types/department-document";
import { useDepartments } from "@/shared/hooks/use-departments";
import { FileText, Calendar, Eye, Lock, Download } from "lucide-react";
import { formatDateTime } from "@/shared/lib/utils";

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

  const categoryOptions = getDocumentCategoryOptions(t);
  const categoryOptionsWithAll = [
    { value: "all", label: t("departmentDocuments.allCategories") },
    ...categoryOptions,
  ];

  const getCategoryLabel = (category: string) => {
    return categoryOptions.find((c) => c.value === category)?.label || category;
  };

  const departmentOptions = [
    { value: "all", label: t("departmentDocuments.allDepartments") },
    ...departments.map((dept) => ({
      value: dept.id.toString(),
      label: dept.name,
    })),
  ];

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

  function DocumentCard({
    document,
    onEdit,
    onDelete,
  }: {
    document: DepartmentDocument;
    onEdit: (doc: DepartmentDocument) => void;
    onDelete: (id: number) => void;
  }) {
    return (
      <Card
        className="cursor-pointer transition-colors hover:bg-muted/50"
        onClick={() => onEdit(document)}
      >
        <CardContent className="p-4">
          {/* Header: Title */}
          <div className="mb-3 flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <FileText className="size-4 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="truncate font-semibold">{document.title}</h3>
              {document.description && (
                <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                  {document.description}
                </p>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">{t("departmentDocuments.category")}: </span>
              <span>{getCategoryLabel(document.category)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("departmentDocuments.department")}: </span>
              <span>{getDepartmentName(document.department_id)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("departmentDocuments.file")}: </span>
              <span className="truncate">{document.file_name}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("departmentDocuments.upload")}: </span>
              <span>{formatDateTime(document.created_at)}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <DepartmentDocumentDownloadButton
              documentId={document.id}
              fileName={document.file_name}
            />
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(document)}>
              {t("common.edit")}
            </Button>
            <Button size="sm" variant="destructive" onClick={() => onDelete(document.id)}>
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mobileView = (
    <div className="space-y-3 p-4">
      {documents.map((document) => (
        <DocumentCard key={document.id} document={document} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );

  return (
    <DataTable
      loading={loading}
      empty={documents.length === 0}
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Документы департаментов</CardTitle>
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <Select
                options={departmentOptions}
                value={departmentFilter?.toString() || "all"}
                onChange={(value) =>
                  onDepartmentFilterChange(value === "all" ? undefined : parseInt(value, 10))
                }
                className="w-full sm:w-auto"
              />
              <Select
                options={categoryOptionsWithAll}
                value={categoryFilter || "all"}
                onChange={(value) => onCategoryFilterChange(value === "all" ? undefined : value)}
                className="w-full sm:w-auto"
              />
              <SearchInput
                placeholder="Поиск по названию"
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
            </div>
          </div>
        </CardHeader>
      }
    >
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
                  <p className="max-w-75 truncate text-sm text-muted-foreground">
                    {document.description}
                  </p>
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
                  <span className="rounded bg-green-100 px-2 py-1 text-xs text-green-800">
                    Публичный
                  </span>
                ) : (
                  <span className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-800">
                    Только отдел
                  </span>
                )}
              </TableCell>
              <TableCell>
                <TableActions
                  actions={[
                    buildEditAction(() => onEdit(document), t("common.edit")),
                    buildDeleteAction(() => onDelete(document.id), t("common.delete")),
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
