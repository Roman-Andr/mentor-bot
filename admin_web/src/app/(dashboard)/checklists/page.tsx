"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useChecklists } from "@/hooks/use-checklists";
import { useDepartments } from "@/hooks/use-departments";
import { ChecklistFormDialog } from "@/components/features/checklists/checklist-form-dialog";
import { ChecklistsTable } from "@/components/features/checklists/checklists-table";
import { ChecklistStats } from "@/components/features/checklists/checklist-stats";

export default function ChecklistsPage() {
  const t = useTranslations("checklists");
  const checklists = useChecklists();
  const deps = useDepartments();

  return (
    <PageContent
      title={t("title")}
      subtitle={t("title")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            checklists.resetForm();
            checklists.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("addChecklist")}
        </Button>
      }
    >
      <ChecklistFormDialog
        open={checklists.isCreateDialogOpen}
        onOpenChange={checklists.setIsCreateDialogOpen}
        mode="create"
        formData={checklists.formData}
        onFormDataChange={checklists.setFormData}
        onSubmit={checklists.handleCreate}
        onCancel={() => checklists.setIsCreateDialogOpen(false)}
      />

      <ChecklistFormDialog
        open={checklists.isEditDialogOpen}
        onOpenChange={(open) => {
          checklists.setIsEditDialogOpen(open);
          if (!open) checklists.setSelectedChecklist(null);
        }}
        mode="edit"
        formData={checklists.formData}
        onFormDataChange={checklists.setFormData}
        onSubmit={checklists.handleUpdate}
        onCancel={() => {
          checklists.setIsEditDialogOpen(false);
          checklists.setSelectedChecklist(null);
        }}
      />

      <ChecklistStats checklists={checklists.checklists} />

      <ChecklistsTable
        checklists={checklists.checklists}
        loading={checklists.loading}
        onEdit={checklists.openEditDialog}
        onComplete={checklists.handleComplete}
        onDelete={checklists.handleDelete}
        searchQuery={checklists.searchQuery}
        onSearchChange={checklists.setSearchQuery}
        statusFilter={checklists.statusFilter}
        onStatusFilterChange={checklists.setStatusFilter}
        departmentFilter={checklists.departmentFilter}
        onDepartmentFilterChange={checklists.setDepartmentFilter}
        onReset={checklists.resetFilters}
        departments={deps.departments}
        currentPage={checklists.currentPage}
        totalPages={checklists.totalPages}
        totalCount={checklists.totalCount}
        onPageChange={checklists.setCurrentPage}
      />
    </PageContent>
  );
}
