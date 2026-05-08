"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { PageContent } from "@/shared/layout/page-content";
import { useDepartments, type DepartmentRow, type DepartmentFormData } from "@/shared/hooks/use-departments";
import { TabSwitcher } from "@/shared/ui/tab-switcher";
import { DepartmentDocumentsTab } from "@/widgets/departments/department-documents-tab";
import { Building2, FileText, Calendar } from "lucide-react";
import type { TabItem } from "@/shared/ui/tab-switcher";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { formatDateTime } from "@/shared/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
import { Pagination } from "@/shared/ui/pagination";

export function DepartmentsWidget() {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const activeTab = searchParams.get("tab") || "departments";
  const entity = useDepartments();

  const tabs: TabItem[] = [
    { id: "departments", label: "Подразделения", icon: Building2 },
    { id: "documents", label: "Документы", icon: FileText },
  ];

  function DepartmentCard({ department, onEdit, onDelete }: { department: DepartmentRow; onEdit: (item: DepartmentRow) => void; onDelete: (id: number) => void }) {
    return (
      <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => onEdit(department)}>
        <CardContent className="p-4">
          {/* Header: Name */}
          <div className="mb-3">
            <h3 className="font-semibold truncate">{department.name}</h3>
            {department.description && (
              <p className="text-muted-foreground mt-1 line-clamp-2 text-xs">{department.description}</p>
            )}
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-1 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <Calendar className="text-muted-foreground size-3" />
              <span className="text-muted-foreground">{t("common.created")}: </span>
              <span>{formatDateTime(department.createdAt)}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div className="flex items-center gap-2 border-t pt-3 flex-col sm:flex-row" onClick={(e) => e.stopPropagation()}>
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onEdit(department)}>
              {t("common.edit")}
            </Button>
            <Button size="sm" variant="destructive" onClick={() => onDelete(department.id)}>
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const departmentsTabContent = (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold">{t("departments.title")}</h2>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-2">
          <input
            type="text"
            placeholder={t("common.search")}
            value={entity.searchQuery}
            onChange={(e) => entity.setSearchQuery(e.target.value)}
            className="rounded border px-3 py-2 w-full sm:w-auto"
          />
          <button
            onClick={() => { entity.resetForm(); entity.setIsCreateDialogOpen(true); }}
            className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center justify-center gap-2 rounded px-4 py-2 w-full sm:w-auto"
          >
            <span className="size-4">+</span>
            {t("departments.addDepartment")}
          </button>
        </div>
      </div>
      {entity.loading ? (
        <div className="text-muted-foreground flex items-center justify-center py-12">Loading...</div>
      ) : entity.items.length === 0 ? (
        <div className="text-muted-foreground flex items-center justify-center py-12">{t("departments.empty")}</div>
      ) : (
        <>
          {/* Desktop/Table View */}
          <div className="hidden md:block border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("departments.name")}</TableHead>
                  <TableHead>{t("common.description")}</TableHead>
                  <TableHead>{t("common.created")}</TableHead>
                  <TableHead className="w-28">{t("common.actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entity.items.map((item) => (
                  <TableRow key={item.id} className="hover:bg-muted cursor-pointer transition-colors" onClick={() => entity.openEditDialog(item)}>
                    <TableCell><span className="font-medium">{item.name}</span></TableCell>
                    <TableCell><span className="text-muted-foreground max-w-75 truncate text-sm">{item.description || "—"}</span></TableCell>
                    <TableCell>{new Date(item.createdAt).toLocaleDateString()}</TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => entity.openEditDialog(item)}>{t("common.edit")}</Button>
                        <Button size="sm" variant="destructive" onClick={() => entity.handleDelete(item.id)}>{t("common.delete")}</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {/* Mobile Card View */}
          <div className="block md:hidden space-y-3">
            {entity.items.map((item) => (
              <DepartmentCard
                key={item.id}
                department={item}
                onEdit={entity.openEditDialog}
                onDelete={entity.handleDelete}
              />
            ))}
          </div>
          {/* Pagination */}
          {!entity.loading && entity.totalCount > 0 && (
            <Pagination
              currentPage={entity.currentPage}
              totalPages={Math.ceil(entity.totalCount / entity.pageSize)}
              totalCount={entity.totalCount}
              pageSize={entity.pageSize}
              onPageChange={entity.setCurrentPage}
              onPageSizeChange={entity.setPageSize}
              showPageSizeSelector={true}
            />
          )}
        </>
      )}
    </div>
  );

  return (
    <PageContent title={t("departments.title")} subtitle={t("departments.title")}>
      <div className="space-y-6">
        <TabSwitcher tabs={tabs} />

        {activeTab === "departments" && departmentsTabContent}

        {activeTab === "documents" && <DepartmentDocumentsTab />}
      </div>
    </PageContent>
  );
}
