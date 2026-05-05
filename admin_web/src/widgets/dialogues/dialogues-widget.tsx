"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { PageContent } from "@/shared/layout/page-content";
import { Plus } from "lucide-react";
import { useDialogues } from "@/shared/hooks/use-dialogues";
import { DialogueFormDialog } from "@/widgets/dialogues/dialogue-form-dialog";
import { DialoguesTable } from "@/widgets/dialogues/dialogues-table";

export function DialoguesWidget() {
  const t = useTranslations();
  const dialogues = useDialogues();

  return (
    <PageContent
      title={t("dialogues.title")}
      subtitle={t("dialogues.title")}
      actions={
        <Button className="gap-2" onClick={() => { dialogues.resetForm(); dialogues.setIsCreateDialogOpen(true); }}>
          <Plus className="size-4" />{t("dialogues.addDialogue")}
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
        onCancel={() => { dialogues.setIsCreateDialogOpen(false); dialogues.resetForm(); }}
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
