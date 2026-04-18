"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useDialogues } from "@/hooks/use-dialogues";
import { DialogueFormDialog } from "@/components/features/dialogues/dialogue-form-dialog";
import { DialoguesTable } from "@/components/features/dialogues/dialogues-table";

export default function DialoguesPage() {
  const t = useTranslations();
  const dialogues = useDialogues();

  return (
    <PageContent
      title={t("dialogues.title")}
      subtitle={t("dialogues.title")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            dialogues.resetForm();
            dialogues.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("dialogues.addDialogue")}
        </Button>
      }
    >
      <DialogueFormDialog
        open={dialogues.isCreateDialogOpen}
        onOpenChange={dialogues.setIsCreateDialogOpen}
        mode="create"
        formData={dialogues.formData}
        onFormDataChange={dialogues.setFormData}
        onSubmit={dialogues.handleSubmit}
        onCancel={() => {
          dialogues.setIsCreateDialogOpen(false);
          dialogues.resetForm();
        }}
      />

      <DialoguesTable
        dialogues={dialogues.dialogues}
        loading={dialogues.loading}
        onDelete={dialogues.handleDelete}
        onToggleActive={dialogues.handleToggleActive}
        searchQuery={dialogues.searchQuery}
        onSearchChange={dialogues.setSearchQuery}
        categoryFilter={dialogues.categoryFilter}
        onCategoryFilterChange={dialogues.setCategoryFilter}
        currentPage={dialogues.currentPage}
        totalPages={dialogues.totalPages}
        totalCount={dialogues.totalCount}
        pageSize={dialogues.pageSize}
        onPageChange={dialogues.setCurrentPage}
        onPageSizeChange={dialogues.setPageSize}
        sortField={dialogues.sortField}
        sortDirection={dialogues.sortDirection}
        onSort={dialogues.toggleSort}
      />
    </PageContent>
  );
}
