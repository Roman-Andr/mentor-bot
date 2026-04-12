"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { Plus } from "lucide-react";
import { useInvitations } from "@/hooks/use-invitations";
import { useDepartments } from "@/hooks/use-departments";
import { CreateInvitationDialog } from "@/components/features/invitations/create-invitation-dialog";
import { InvitationLinkDialog } from "@/components/features/invitations/invitation-link-dialog";
import { InvitationStats } from "@/components/features/invitations/invitation-stats";
import { InvitationsTable } from "@/components/features/invitations/invitations-table";

export default function InvitationsPage() {
  const t = useTranslations();
  const inv = useInvitations();
  const deps = useDepartments();

  return (
    <PageContent
      title={t("invitations.title")}
      subtitle={t("invitations.title")}
      actions={
        <Button className="gap-2" onClick={() => inv.setIsCreateDialogOpen(true)}>
          <Plus className="size-4" />
          {t("invitations.sendInvitation")}
        </Button>
      }
    >
      <CreateInvitationDialog
        open={inv.isCreateDialogOpen}
        onOpenChange={inv.setIsCreateDialogOpen}
        formData={inv.formData}
        onFormDataChange={inv.setFormData}
        emailTouched={inv.emailTouched}
        onEmailTouchedChange={inv.setEmailTouched}
        departments={deps.items}
        onSubmit={inv.handleCreateInvitation}
        onCancel={() => {
          inv.setIsCreateDialogOpen(false);
          inv.setEmailTouched(false);
        }}
      />

      <InvitationLinkDialog
        url={inv.createdUrl}
        onOpenChange={(open) => {
          if (!open) inv.setCreatedUrl(null);
        }}
      />

      <InvitationStats stats={inv.stats} />

      <InvitationsTable
        invitations={inv.invitations}
        loading={inv.loading}
        searchQuery={inv.searchQuery}
        onSearchChange={inv.setSearchQuery}
        roleFilter={inv.roleFilter}
        onRoleFilterChange={inv.setRoleFilter}
        statusFilter={inv.statusFilter}
        onStatusFilterChange={inv.setStatusFilter}
        onReset={inv.resetFilters}
        onResend={inv.handleResendInvitation}
        onRevoke={inv.handleRevokeInvitation}
        onDelete={inv.handleDeleteInvitation}
        currentPage={inv.currentPage}
        totalPages={inv.totalPages}
        totalCount={inv.totalCount}
        pageSize={inv.pageSize}
        onPageChange={inv.setCurrentPage}
        onPageSizeChange={inv.setPageSize}
      />
    </PageContent>
  );
}
