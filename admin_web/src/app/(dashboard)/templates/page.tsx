"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useTemplates } from "@/hooks/use-templates";
import { useDepartments } from "@/hooks/use-departments";
import { TemplateFormDialog } from "@/components/features/templates/template-form-dialog";
import { TemplatesTable } from "@/components/features/templates/templates-table";
import { TemplateStats } from "@/components/features/templates/template-stats";

export default function TemplatesPage() {
  const t = useTranslations();
  const tmpl = useTemplates();
  const deps = useDepartments();

  return (
    <PageContent
      title={t("templates.title")}
      subtitle={t("templates.title")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            tmpl.resetForm();
            tmpl.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("templates.addTemplate")}
        </Button>
      }
    >
      <TemplateFormDialog
        open={tmpl.isCreateDialogOpen}
        onOpenChange={tmpl.setIsCreateDialogOpen}
        mode="create"
        formData={tmpl.formData}
        onFormDataChange={tmpl.setFormData}
        tasks={tmpl.tasks}
        departments={deps.items}
        onTasksChange={tmpl.setTasks}
        onSubmit={tmpl.handleCreate}
        onCancel={() => tmpl.setIsCreateDialogOpen(false)}
      />

      <TemplateFormDialog
        open={tmpl.isEditDialogOpen}
        onOpenChange={(open) => {
          tmpl.setIsEditDialogOpen(open);
          if (!open) tmpl.setSelectedTemplate(null);
        }}
        mode="edit"
        formData={tmpl.formData}
        onFormDataChange={tmpl.setFormData}
        tasks={tmpl.tasks}
        departments={deps.items}
        onTasksChange={tmpl.setTasks}
        onSubmit={tmpl.handleUpdate}
        onCancel={() => {
          tmpl.setIsEditDialogOpen(false);
          tmpl.setSelectedTemplate(null);
        }}
      />

      <TemplateStats templates={tmpl.templates} />

      <TemplatesTable
        templates={tmpl.templates}
        loading={tmpl.loading}
        onEdit={tmpl.openEditDialog}
        onPublish={tmpl.handlePublish}
        onDelete={tmpl.handleDelete}
        searchQuery={tmpl.searchQuery}
        onSearchChange={tmpl.setSearchQuery}
        statusFilter={tmpl.statusFilter}
        onStatusFilterChange={tmpl.setStatusFilter}
        onReset={tmpl.resetFilters}
        currentPage={tmpl.currentPage}
        totalPages={tmpl.totalPages}
        totalCount={tmpl.totalCount}
        pageSize={tmpl.pageSize}
        onPageChange={tmpl.setCurrentPage}
        onPageSizeChange={tmpl.setPageSize}
      />
    </PageContent>
  );
}
