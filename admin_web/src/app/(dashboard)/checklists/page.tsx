"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useChecklists } from "@/hooks/use-checklists";
import { useDepartments } from "@/hooks/use-departments";
import { ChecklistFormDialog } from "@/components/features/checklists/checklist-form-dialog";
import { ChecklistsTable } from "@/components/features/checklists/checklists-table";
import { ChecklistStats } from "@/components/features/checklists/checklist-stats";

export default function ChecklistsPage() {
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
      {/* Create Dialog */}
      <ChecklistFormDialog
        open={c.isCreateDialogOpen}
        onOpenChange={c.setIsCreateDialogOpen}
        mode="create"
        formData={c.formData}
        onFormDataChange={c.setFormData}
        onSubmit={c.handleCreate}
        onCancel={() => c.setIsCreateDialogOpen(false)}
      />

      {/* Edit Dialog */}
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

      {/* Stats */}
      <ChecklistStats checklists={c.checklists} />

      {/* Table with Filters */}
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
