"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { PageContent } from "@/shared/layout/page-content";
import { Plus, ClipboardCheck, Bell } from "lucide-react";
import { useTemplates } from "@/shared/hooks/use-templates";
import { useDepartments } from "@/shared/hooks/use-departments";
import { TemplateFormDialog } from "@/widgets/templates/template-form-dialog";
import { TemplatesTable } from "@/widgets/templates/templates-table";
import { TemplateStats } from "@/widgets/templates/template-stats";
import { TabSwitcher } from "@/shared/ui/tab-switcher";
import { NotificationTemplatesTab } from "@/widgets/notification-templates/notification-templates-tab";
import { NotificationTemplateFormDialog } from "@/widgets/notification-templates/notification-template-form-dialog";
import type { TabItem } from "@/shared/ui/tab-switcher";
import { useSearchParams } from "next/navigation";
import { api } from "@/shared/lib/api";
import { useToast } from "@/shared/hooks/use-toast";

export function TemplatesWidget() {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const activeTab = searchParams.get("tab") || "checklist-templates";
  const tmpl = useTemplates();
  const deps = useDepartments();
  const { toast } = useToast();
  const [notificationDialogOpen, setNotificationDialogOpen] = useState(false);
  const [editingNotificationTemplate, setEditingNotificationTemplate] = useState<any>(null);

  const tabs: TabItem[] = [
    { id: "checklist-templates", label: t("templates.checklistTemplates"), icon: ClipboardCheck },
    { id: "notification-templates", label: t("templates.notificationTemplates"), icon: Bell },
  ];

  const handleNotificationCreate = () => {
    setEditingNotificationTemplate(null);
    setNotificationDialogOpen(true);
  };
  const handleNotificationEdit = (template: any) => {
    setEditingNotificationTemplate(template);
    setNotificationDialogOpen(true);
  };

  const handleClone = async (id: number) => {
    const result = await api.templates.clone(id);
    if (result.success) {
      toast(t("templates.cloned") || "Template cloned", "success");
      tmpl.handlePublish(0);
    } else {
      toast(t("templates.cloneError") || "Failed to clone", "error");
    }
  };

  return (
    <PageContent
      title={t("templates.title")}
      subtitle={t("templates.subtitle") || t("templates.title")}
      actions={
        activeTab === "checklist-templates" ? (
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
        ) : activeTab === "notification-templates" ? (
          <Button className="gap-2" onClick={handleNotificationCreate}>
            <Plus className="size-4" />
            {t("templates.addTemplate")}
          </Button>
        ) : null
      }
    >
      <div className="space-y-6">
        <TabSwitcher tabs={tabs} />

        {activeTab === "checklist-templates" && (
          <>
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
              onClone={handleClone}
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
              sortField={tmpl.sortField}
              sortDirection={tmpl.sortDirection}
              onSort={tmpl.toggleSort}
            />
          </>
        )}

        {activeTab === "notification-templates" && (
          <>
            <NotificationTemplatesTab
              onCreate={handleNotificationCreate}
              onEdit={handleNotificationEdit}
            />
            <NotificationTemplateFormDialog
              open={notificationDialogOpen}
              onOpenChange={setNotificationDialogOpen}
              template={editingNotificationTemplate}
            />
          </>
        )}
      </div>
    </PageContent>
  );
}
