"use client";

import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useTemplates } from "@/hooks/use-templates";
import { useDepartments } from "@/hooks/use-departments";
import { TemplateFormDialog } from "@/components/features/templates/template-form-dialog";
import { TemplatesTable } from "@/components/features/templates/templates-table";
import { TemplateStats } from "@/components/features/templates/template-stats";

export default function TemplatesPage() {
  const t = useTemplates();
  const deps = useDepartments();

  return (
    <PageContent
      title="Шаблоны чек-листов"
      subtitle="Управление шаблонами онбординга"
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            t.resetForm();
            t.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          Создать шаблон
        </Button>
      }
    >
      <TemplateFormDialog
        open={t.isCreateDialogOpen}
        onOpenChange={t.setIsCreateDialogOpen}
        mode="create"
        formData={t.formData}
        onFormDataChange={t.setFormData}
        tasks={t.tasks}
        departments={deps.departments}
        onTasksChange={t.setTasks}
        onSubmit={t.handleCreate}
        onCancel={() => t.setIsCreateDialogOpen(false)}
      />

      <TemplateFormDialog
        open={t.isEditDialogOpen}
        onOpenChange={(open) => {
          t.setIsEditDialogOpen(open);
          if (!open) t.setSelectedTemplate(null);
        }}
        mode="edit"
        formData={t.formData}
        onFormDataChange={t.setFormData}
        tasks={t.tasks}
        departments={deps.departments}
        onTasksChange={t.setTasks}
        onSubmit={t.handleUpdate}
        onCancel={() => {
          t.setIsEditDialogOpen(false);
          t.setSelectedTemplate(null);
        }}
      />

      <TemplateStats templates={t.templates} />

      <TemplatesTable
        templates={t.templates}
        loading={t.loading}
        onEdit={t.openEditDialog}
        onPublish={t.handlePublish}
        onDelete={t.handleDelete}
        searchQuery={t.searchQuery}
        onSearchChange={t.setSearchQuery}
        statusFilter={t.statusFilter}
        onStatusFilterChange={t.setStatusFilter}
        currentPage={t.currentPage}
        totalPages={t.totalPages}
        totalCount={t.totalCount}
        onPageChange={t.setCurrentPage}
      />
    </PageContent>
  );
}
