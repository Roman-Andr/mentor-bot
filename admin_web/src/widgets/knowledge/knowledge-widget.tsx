"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Dialog } from "@/shared/ui/dialog";
import { PageContent } from "@/shared/layout/page-content";
import { Plus, BookOpen, FolderOpen, Hash } from "lucide-react";
import { ArticleFormDialog } from "@/widgets/knowledge/article-form-dialog";
import { ArticleStats } from "@/widgets/knowledge/article-stats";
import { ArticlesTable } from "@/widgets/knowledge/articles-table";
import { CategoriesTable } from "@/widgets/knowledge/categories-table";
import { CategoryFormDialog } from "@/widgets/knowledge/category-form-dialog";
import { TagsSection } from "@/widgets/knowledge/tags-section";
import { useArticles } from "@/shared/hooks/use-articles";
import { useCategories } from "@/shared/hooks/use-categories";
import { useDepartments } from "@/shared/hooks/use-departments";
import { TabSwitcher } from "@/shared/ui/tab-switcher";
import type { TabItem } from "@/shared/ui/tab-switcher";
import { useSearchParams } from "next/navigation";

type Tab = "articles" | "categories" | "tags";

export function KnowledgeWidget() {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const activeTab = (searchParams.get("tab") as Tab) || "articles";
  const a = useArticles();
  const c = useCategories();
  const deps = useDepartments();

  const tabs: TabItem[] = [
    { id: "articles", label: t("knowledge.articles"), icon: BookOpen },
    { id: "categories", label: t("knowledge.categories"), icon: FolderOpen },
    { id: "tags", label: t("knowledge.tags") || "Tags", icon: Hash },
  ];

  const handleCategorySubmit = async () => { await c.handleSubmit(); a.loadCategories(); };
  const handleCategoryDelete = async (id: number) => { await c.handleDelete(id); a.loadCategories(); };

  const handleAddClick = () => {
    if (activeTab === "articles") { a.resetForm(); a.setIsCreateDialogOpen(true); }
    else if (activeTab === "categories") { c.resetForm(); c.setIsCreateDialogOpen(true); }
  };

  return (
    <PageContent
      title={t("knowledge.title")}
      subtitle={t("knowledge.subtitle") || t("knowledge.title")}
      actions={
        activeTab !== "tags" ? (
          <Button className="gap-2" onClick={handleAddClick}>
            <Plus className="size-4" />
            {activeTab === "articles" ? t("knowledge.addArticle") : t("knowledge.addCategory")}
          </Button>
        ) : null
      }
    >
      <div className="space-y-6">
        <TabSwitcher tabs={tabs} />

        {activeTab === "articles" && (
          <>
            <Dialog open={a.isCreateDialogOpen} onOpenChange={a.setIsCreateDialogOpen}>
              <ArticleFormDialog
                mode="create"
                formData={a.formData}
                onFormDataChange={a.setFormData}
                categories={a.categories}
                departments={deps.items}
                articleId={a.selectedArticle?.id ?? null}
                attachments={[]}
                onAttachmentsChange={() => {}}
                pendingFiles={a.pendingFiles}
                onPendingFilesChange={a.setPendingFiles}
                onSubmit={a.handleSubmit}
                onCancel={() => { a.setIsCreateDialogOpen(false); a.resetForm(); }}
              />
            </Dialog>
            <Dialog open={a.isEditDialogOpen} onOpenChange={a.setIsEditDialogOpen}>
              <ArticleFormDialog
                mode="edit"
                formData={a.formData}
                onFormDataChange={a.setFormData}
                categories={a.categories}
                departments={deps.items}
                articleId={a.selectedArticle?.id ?? null}
                attachments={a.attachments}
                onAttachmentsChange={a.setAttachments}
                pendingFiles={a.pendingFiles}
                onPendingFilesChange={a.setPendingFiles}
                onSubmit={a.handleSubmit}
                onCancel={() => { a.setIsEditDialogOpen(false); a.resetForm(); }}
              />
            </Dialog>
            <ArticleStats articles={a.articles} />
            <ArticlesTable
              articles={a.articles}
              loading={a.loading}
              searchQuery={a.searchQuery}
              onSearchChange={a.setSearchQuery}
              categoryFilter={a.categoryFilter}
              onCategoryFilterChange={a.setCategoryFilter}
              statusFilter={a.statusFilter}
              onStatusFilterChange={a.setStatusFilter}
              pinnedFilter={a.pinnedFilter}
              onPinnedFilterChange={a.setPinnedFilter}
              onReset={a.resetFilters}
              categories={a.categories}
              onEdit={a.openEdit}
              onPublish={a.handlePublish}
              onDelete={a.handleDelete}
              currentPage={a.currentPage}
              totalPages={a.totalPages}
              totalCount={a.totalCount}
              pageSize={a.pageSize}
              onPageChange={a.setCurrentPage}
              onPageSizeChange={a.setPageSize}
              sortField={a.sortField}
              sortDirection={a.sortDirection}
              onSort={a.toggleSort}
            />
          </>
        )}

        {activeTab === "categories" && (
          <>
            <Dialog open={c.isCreateDialogOpen} onOpenChange={c.setIsCreateDialogOpen}>
              <CategoryFormDialog
                mode="create"
                formData={c.formData}
                onFormDataChange={c.updateFormField}
                categories={c.categories}
                departments={deps.items}
                onSubmit={handleCategorySubmit}
                onCancel={() => { c.setIsCreateDialogOpen(false); c.resetForm(); }}
              />
            </Dialog>
            <Dialog open={c.isEditDialogOpen} onOpenChange={c.setIsEditDialogOpen}>
              <CategoryFormDialog
                mode="edit"
                formData={c.formData}
                onFormDataChange={c.updateFormField}
                categories={c.categories.filter((cat) => cat.id !== c.selectedCategory?.id)}
                departments={deps.items}
                onSubmit={handleCategorySubmit}
                onCancel={() => { c.setIsEditDialogOpen(false); c.resetForm(); }}
              />
            </Dialog>
            <CategoriesTable
              categories={c.categories}
              loading={c.loading}
              searchQuery={c.searchQuery}
              onSearchChange={c.setSearchQuery}
              onResetFilters={c.resetFilters}
              currentPage={c.currentPage}
              totalPages={c.totalPages}
              totalCount={c.totalCount}
              pageSize={c.pageSize}
              onPageChange={c.setCurrentPage}
              onPageSizeChange={c.setPageSize}
              onEdit={c.openEdit}
              onDelete={handleCategoryDelete}
              sortField={c.sortField}
              sortDirection={c.sortDirection}
              onSort={c.toggleSort}
            />
          </>
        )}

        {activeTab === "tags" && <TagsSection />}
      </div>
    </PageContent>
  );
}
