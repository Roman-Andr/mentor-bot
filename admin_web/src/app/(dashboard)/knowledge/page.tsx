"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { PageContent } from "@/components/layout/page-content";
import { Plus, BookOpen, FolderOpen } from "lucide-react";
import { ArticleFormDialog } from "@/components/features/knowledge/article-form-dialog";
import { ArticleStats } from "@/components/features/knowledge/article-stats";
import { ArticlesTable } from "@/components/features/knowledge/articles-table";
import { CategoriesTable } from "@/components/features/knowledge/categories-table";
import { CategoryFormDialog } from "@/components/features/knowledge/category-form-dialog";
import { useArticles } from "@/hooks/use-articles";
import { useCategories } from "@/hooks/use-categories";
import { useDepartments } from "@/hooks/use-departments";
import { cn } from "@/lib/utils";

type Tab = "articles" | "categories";

export default function KnowledgePage() {
  const [activeTab, setActiveTab] = useState<Tab>("articles");
  const a = useArticles();
  const c = useCategories();
  const deps = useDepartments();

  const handleCategorySubmit = async () => {
    await c.handleSubmit();
    a.loadCategories();
  };

  const handleCategoryDelete = async (id: number) => {
    await c.handleDelete(id);
    a.loadCategories();
  };

  return (
    <PageContent
      title="База знаний"
      subtitle="Управление статьями и категориями"
      actions={
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border">
            <button
              className={cn(
                "flex items-center gap-1.5 rounded-l-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "articles"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("articles")}
            >
              <BookOpen className="size-4" />
              Статьи
            </button>
            <button
              className={cn(
                "flex items-center gap-1.5 rounded-r-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "categories"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("categories")}
            >
              <FolderOpen className="size-4" />
              Категории
            </button>
          </div>
          <Button
            className="gap-2"
            onClick={() => {
              if (activeTab === "articles") {
                a.resetForm();
                a.setIsCreateDialogOpen(true);
              } else {
                c.resetForm();
                c.setIsCreateDialogOpen(true);
              }
            }}
          >
            <Plus className="size-4" />
            {activeTab === "articles" ? "Создать статью" : "Создать категорию"}
          </Button>
        </div>
      }
    >
      {activeTab === "articles" && (
        <>
          <Dialog open={a.isCreateDialogOpen} onOpenChange={a.setIsCreateDialogOpen}>
            <ArticleFormDialog
              mode="create"
              formData={a.formData}
              onFormDataChange={a.setFormData}
              categories={a.categories}
              departments={deps.departments}
              articleId={a.selectedArticle?.id ?? null}
              attachments={[]}
              onAttachmentsChange={() => {}}
              pendingFiles={a.pendingFiles}
              onPendingFilesChange={a.setPendingFiles}
              onSubmit={a.handleSubmit}
              onCancel={() => {
                a.setIsCreateDialogOpen(false);
                a.resetForm();
              }}
            />
          </Dialog>
          <Dialog open={a.isEditDialogOpen} onOpenChange={a.setIsEditDialogOpen}>
            <ArticleFormDialog
              mode="edit"
              formData={a.formData}
              onFormDataChange={a.setFormData}
              categories={a.categories}
              departments={deps.departments}
              articleId={a.selectedArticle?.id ?? null}
              attachments={a.attachments}
              onAttachmentsChange={a.setAttachments}
              pendingFiles={a.pendingFiles}
              onPendingFilesChange={a.setPendingFiles}
              onSubmit={a.handleSubmit}
              onCancel={() => {
                a.setIsEditDialogOpen(false);
                a.resetForm();
              }}
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
            categories={a.categories}
            onEdit={a.openEdit}
            onPublish={a.handlePublish}
            onDelete={a.handleDelete}
            currentPage={a.currentPage}
            totalPages={a.totalPages}
            totalCount={a.totalCount}
            onPageChange={a.setCurrentPage}
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
              departments={deps.departments}
              onSubmit={handleCategorySubmit}
              onCancel={() => {
                c.setIsCreateDialogOpen(false);
                c.resetForm();
              }}
            />
          </Dialog>
          <Dialog open={c.isEditDialogOpen} onOpenChange={c.setIsEditDialogOpen}>
            <CategoryFormDialog
              mode="edit"
              formData={c.formData}
              onFormDataChange={c.updateFormField}
              categories={c.categories.filter((cat) => cat.id !== c.selectedCategory?.id)}
              departments={deps.departments}
              onSubmit={handleCategorySubmit}
              onCancel={() => {
                c.setIsEditDialogOpen(false);
                c.resetForm();
              }}
            />
          </Dialog>

          <CategoriesTable
            categories={c.categories}
            loading={c.loading}
            searchQuery={c.searchQuery}
            onSearchChange={c.setSearchQuery}
            currentPage={c.currentPage}
            totalPages={c.totalPages}
            totalCount={c.totalCount}
            onPageChange={c.setCurrentPage}
            onEdit={c.openEdit}
            onDelete={handleCategoryDelete}
          />
        </>
      )}
    </PageContent>
  );
}
