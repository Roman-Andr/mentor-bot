"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { PageContent } from "@/shared/layout/page-content";
import { Plus } from "lucide-react";
import { useChecklists } from "@/shared/hooks/use-checklists";
import { useDepartments } from "@/shared/hooks/use-departments";
import { ChecklistFormDialog } from "@/widgets/checklists/checklist-form-dialog";
import { ChecklistsTable } from "@/widgets/checklists/checklists-table";
import { ChecklistStats } from "@/widgets/checklists/checklist-stats";

export function ChecklistsWidget() {
  const t = useTranslations();
  const c = useChecklists();
  const deps = useDepartments();

  return (
    <PageContent
      title={t("checklists.title")}
      subtitle={t("checklists.subtitle")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            c.resetForm();
            c.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("checklists.addChecklist")}
        </Button>
      }
    >
      <ChecklistFormDialog
        open={c.isCreateDialogOpen}
        onOpenChange={c.setIsCreateDialogOpen}
        mode="create"
        formData={c.formData}
        onFormDataChange={c.setFormData}
        onSubmit={c.handleCreate}
        onCancel={() => c.setIsCreateDialogOpen(false)}
      />
      <ChecklistFormDialog
        open={c.isEditDialogOpen}
        onOpenChange={(open) => {
          c.setIsEditDialogOpen(open);
          if (!open) c.setSelectedChecklist(null);
        }}
        mode="edit"
        formData={c.formData}
        onFormDataChange={c.setFormData}
        onSubmit={(tasksToComplete) => c.handleUpdate(tasksToComplete)}
        onCancel={() => {
          c.setIsEditDialogOpen(false);
          c.setSelectedChecklist(null);
        }}
        checklistId={c.selectedChecklist?.id}
      />
      <ChecklistStats checklists={c.checklists} />
      <ChecklistsTable
        checklists={c.checklists}
        loading={c.loading}
        onEdit={c.openEditDialog}
        onComplete={c.handleComplete}
        onDelete={c.handleDelete}
        searchQuery={c.searchQuery}
        onSearchChange={c.setSearchQuery}
        statusFilter={c.statusFilter}
        onStatusFilterChange={c.setStatusFilter}
        departmentFilter={c.departmentFilter}
        onDepartmentFilterChange={c.setDepartmentFilter}
        onReset={c.resetFilters}
        departments={deps.items}
        currentPage={c.currentPage}
        totalPages={c.totalPages}
        totalCount={c.totalCount}
        pageSize={c.pageSize}
        onPageChange={c.setCurrentPage}
        onPageSizeChange={c.setPageSize}
        sortField={c.sortField}
        sortDirection={c.sortDirection}
        onSort={c.toggleSort}
      />
    </PageContent>
  );
}
