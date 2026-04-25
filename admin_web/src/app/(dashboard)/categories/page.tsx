"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useCategories, CategoryRow, CategoryFormData } from "@/hooks/use-categories";
import { useDepartments } from "@/hooks/use-departments";
import { EntityFormDialog } from "@/components/entity/entity-form-dialog";
import { DataTable } from "@/components/ui/data-table";
import { CategoryForm } from "@/components/features/knowledge/category-form";
import { CategoriesTable } from "@/components/features/knowledge/categories-table";

export default function CategoriesPage() {
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const categories = useCategories();
  const departments = useDepartments();

  // Create dialog
  const createDialog = (
    <EntityFormDialog
      isOpen={categories.isCreateDialogOpen}
      onClose={() => categories.setIsCreateDialogOpen(false)}
      onSubmit={categories.handleSubmit}
      title={t("addCategoryTitle") ?? "Add Category"}
      description={t("createNewCategory") ?? "Create a new category"}
      submitLabel={tCommon("create") ?? "Create"}
      cancelLabel={tCommon("cancel") ?? "Cancel"}
      isSubmitting={categories.isSubmitting}
      isValid={!!categories.formData.name}
      formData={categories.formData}
    >
      <CategoryForm
        formData={categories.formData}
        onChange={categories.setFormData}
        categories={categories.categories}
        departments={departments.items}
      />
    </EntityFormDialog>
  );

  // Edit dialog
  const editDialog = (
    <EntityFormDialog
      isOpen={categories.isEditDialogOpen}
      onClose={() => {
        categories.setIsEditDialogOpen(false);
        categories.setSelectedCategory(null);
      }}
      onSubmit={categories.handleSubmit}
      title={t("editCategoryTitle") ?? "Edit Category"}
      description={t("changeCategory") ?? "Change category details"}
      submitLabel={tCommon("save") ?? "Save"}
      cancelLabel={tCommon("cancel") ?? "Cancel"}
      isSubmitting={categories.isSubmitting}
      isValid={!!categories.formData.name}
      formData={categories.formData}
    >
      <CategoryForm
        formData={categories.formData}
        onChange={categories.setFormData}
        categories={categories.categories}
        departments={departments.items}
        isEdit
      />
    </EntityFormDialog>
  );

  return (
    <PageContent
      title={t("categories") ?? "Categories"}
      subtitle={t("title") ?? "Knowledge Base"}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            categories.resetForm();
            categories.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("addCategory") ?? "Add Category"}
        </Button>
      }
    >
      {createDialog}
      {editDialog}

      <DataTable
        loading={categories.loading}
        empty={categories.categories.length === 0}
        currentPage={categories.currentPage}
        totalPages={categories.totalPages}
        totalCount={categories.totalCount}
        pageSize={categories.pageSize}
        onPageChange={categories.setCurrentPage}
        onPageSizeChange={categories.setPageSize}
        showPageSizeSelector={true}
      >
        <CategoriesTable
          categories={categories.categories}
          loading={categories.loading}
          searchQuery={categories.searchQuery}
          onSearchChange={categories.setSearchQuery}
          onResetFilters={categories.resetFilters}
          currentPage={categories.currentPage}
          totalPages={categories.totalPages}
          totalCount={categories.totalCount}
          pageSize={categories.pageSize}
          onPageChange={categories.setCurrentPage}
          onPageSizeChange={categories.setPageSize}
          onEdit={categories.openEdit}
          onDelete={categories.handleDelete}
          sortField={categories.sortField ?? null}
          sortDirection={categories.sortDirection}
          onSort={categories.toggleSort}
          totalCountLabel={t("categories") ?? "Categories"}
        />
      </DataTable>
    </PageContent>
  );
}
