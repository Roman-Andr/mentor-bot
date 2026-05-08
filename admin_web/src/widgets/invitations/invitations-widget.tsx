"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { PageContent } from "@/shared/layout/page-content";
import { useInvitations, type InvitationItem, type InvitationFormData } from "@/shared/hooks/use-invitations";
import { useDepartments } from "@/shared/hooks/use-departments";
import { CreateInvitationDialog } from "@/widgets/invitations/create-invitation-dialog";
import { InvitationLinkDialog } from "@/widgets/invitations/invitation-link-dialog";
import { InvitationStats } from "@/widgets/invitations/invitation-stats";
import { InvitationsTable } from "@/widgets/invitations/invitations-table";
import { Button } from "@/shared/ui/button";
import { Plus } from "lucide-react";

export function InvitationsWidget() {
  const t = useTranslations();
  const inv = useInvitations();
  const deps = useDepartments();

  return (
    <PageContent title={t("invitations.title")} subtitle={t("invitations.title")}>
      <CreateInvitationDialog
        open={inv.isCreateDialogOpen}
        onOpenChange={inv.setIsCreateDialogOpen}
        formData={inv.formData}
        onFormDataChange={(value: InvitationFormData | ((prev: InvitationFormData) => InvitationFormData)) => {
          inv.setFormData(typeof value === "function" ? value(inv.formData) : value);
        }}
        emailTouched={inv.emailTouched}
        onEmailTouchedChange={(touched: boolean) => inv.setEmailTouched(touched)}
        departments={deps.items}
        onSubmit={inv.handleCreateInvitation}
        onCancel={() => { inv.setIsCreateDialogOpen(false); inv.setEmailTouched(false); }}
      />

      <InvitationLinkDialog
        url={inv.createdUrl}
        onOpenChange={(open) => { if (!open) inv.setCreatedUrl(null); }}
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
        totalPages={Math.ceil(inv.totalCount / inv.pageSize)}
        totalCount={inv.totalCount}
        pageSize={inv.pageSize}
        onPageChange={inv.setCurrentPage}
        onPageSizeChange={inv.setPageSize}
        sortField={inv.sortField ?? null}
        sortDirection={inv.sortDirection}
        onSort={inv.toggleSort}
      />
    </PageContent>
  );
}
