"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useDialogues } from "@/hooks/use-dialogues";
import { DialogueFormDialog } from "@/components/features/dialogues/dialogue-form-dialog";
import { DialoguesTable } from "@/components/features/dialogues/dialogues-table";

export default function DialoguesPage() {
  const t = useTranslations("dialogues");
  const dialogues = useDialogues();

  return (
    <PageContent
      title={t("title")}
      subtitle={t("title")}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            dialogues.resetForm();
            dialogues.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("addDialogue")}
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

      <DialogueFormDialog
        open={dialogues.isEditDialogOpen}
        onOpenChange={(open) => {
          dialogues.setIsEditDialogOpen(open);
          if (!open) dialogues.resetForm();
        }}
        mode="edit"
        formData={dialogues.formData}
        onFormDataChange={dialogues.setFormData}
        onSubmit={dialogues.handleSubmit}
        onCancel={() => {
          dialogues.setIsEditDialogOpen(false);
          dialogues.resetForm();
        }}
      />

      <DialoguesTable
        dialogues={dialogues.dialogues}
        loading={dialogues.loading}
        onEdit={dialogues.openEdit}
        onDelete={dialogues.handleDelete}
        onToggleActive={dialogues.handleToggleActive}
        searchQuery={dialogues.searchQuery}
        onSearchChange={dialogues.setSearchQuery}
        categoryFilter={dialogues.categoryFilter}
        onCategoryFilterChange={dialogues.setCategoryFilter}
        currentPage={dialogues.currentPage}
        totalPages={dialogues.totalPages}
        totalCount={dialogues.totalCount}
        onPageChange={dialogues.setCurrentPage}
      />
    </PageContent>
  );
}
