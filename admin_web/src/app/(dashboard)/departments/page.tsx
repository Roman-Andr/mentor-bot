"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { EntityPage } from "@/components/entity";
import { useDepartments, type DepartmentRow, type DepartmentFormData } from "@/hooks/use-departments";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { TabSwitcher } from "@/components/ui/tab-switcher";
import { DepartmentDocumentsTab } from "@/components/features/departments/department-documents-tab";

export default function DepartmentsPage() {
  const t = useTranslations();
  const entity = useDepartments();
  const [activeTab, setActiveTab] = useState("departments");

  const tabs = [
    { id: "departments", label: "Подразделения" },
    { id: "documents", label: "Документы" },
  ];

  return (
    <div className="space-y-4">
      <TabSwitcher tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "departments" && (
        <EntityPage<DepartmentRow, DepartmentFormData>
          title={t("departments.title")}
          items={entity.items}
          totalItems={entity.totalCount}
          pageSize={entity.pageSize}
          currentPage={entity.currentPage}
          isLoading={entity.loading}
          onPageSizeChange={entity.setPageSize}
          isCreateOpen={entity.isCreateDialogOpen}
          isEditOpen={entity.isEditDialogOpen}
          selectedItem={entity.selectedItem}
          onCreateOpen={() => {
            entity.resetForm();
            entity.setIsCreateDialogOpen(true);
          }}
          onEditOpen={entity.openEditDialog}
          onDelete={entity.handleDelete}
          onCloseDialog={() => {
            entity.setIsCreateDialogOpen(false);
            entity.setIsEditDialogOpen(false);
            entity.resetForm();
          }}
          formData={entity.formData}
          onFormChange={entity.setFormData}
          onSubmit={entity.handleSubmit}
          isSubmitting={entity.isSubmitting}
          submitError={null}
          searchQuery={entity.searchQuery}
          onSearchChange={entity.setSearchQuery}
          onPageChange={entity.setCurrentPage}
          createButtonLabel={t("departments.addDepartment")}
          emptyStateMessage={t("departments.empty")}
          searchPlaceholder={t("common.search")}
          getItemKey={(item) => item.id}
          sortField={entity.sortField}
          sortDirection={entity.sortDirection}
          onSort={entity.toggleSort}
          columns={[
            {
              key: "name",
              header: t("departments.name"),
              cell: (item) => <span className="font-medium">{item.name}</span>,
              sortable: true,
            },
            {
              key: "description",
              header: t("common.description"),
              cell: (item) => (
                <span className="text-muted-foreground max-w-75 truncate text-sm">
                  {item.description || "—"}
                </span>
              ),
            },
            {
              key: "createdAt",
              header: t("common.created"),
              cell: (item) => new Date(item.createdAt).toLocaleDateString(),
              width: "w-32",
              sortable: true,
            },
          ]}
          renderForm={({ formData, onChange }) => (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">{t("departments.name")} *</label>
                <Input
                  placeholder={t("departments.name")}
                  value={formData.name}
                  onChange={(e) => onChange({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">{t("common.description")}</label>
                <Textarea
                  placeholder={t("common.description")}
                  value={formData.description}
                  onChange={(e) => onChange({ ...formData, description: e.target.value })}
                  rows={4}
                />
              </div>
            </div>
          )}
          isFormValid={!!entity.formData.name}
        />
      )}

      {activeTab === "documents" && <DepartmentDocumentsTab />}
    </div>
  );
}
