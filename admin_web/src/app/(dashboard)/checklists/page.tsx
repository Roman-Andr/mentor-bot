"use client";

import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useChecklists } from "@/hooks/use-checklists";
import { useDepartments } from "@/hooks/use-departments";
import { ChecklistFormDialog } from "@/components/features/checklists/checklist-form-dialog";
import { ChecklistsTable } from "@/components/features/checklists/checklists-table";
import { ChecklistStats } from "@/components/features/checklists/checklist-stats";

export default function ChecklistsPage() {
  const c = useChecklists();
  const deps = useDepartments();

  return (
    <PageContent
      title="Чек-листы"
      subtitle="Управление чек-листами онбординга сотрудников"
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            c.resetForm();
            c.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          Назначить чек-лист
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
        onSubmit={c.handleUpdate}
        onCancel={() => {
          c.setIsEditDialogOpen(false);
          c.setSelectedChecklist(null);
        }}
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
        departments={deps.departments}
        currentPage={c.currentPage}
        totalPages={c.totalPages}
        totalCount={c.totalCount}
        onPageChange={c.setCurrentPage}
      />
    </PageContent>
  );
}
