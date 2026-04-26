"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { PageContent } from "@/components/layout/page-content";
import { useInvitations, type InvitationItem, type InvitationFormData } from "@/hooks/use-invitations";
import { useDepartments } from "@/hooks/use-departments";
import { EntityPage } from "@/components/entity";
import { CreateInvitationDialog } from "@/components/features/invitations/create-invitation-dialog";
import { InvitationLinkDialog } from "@/components/features/invitations/invitation-link-dialog";
import { InvitationStats } from "@/components/features/invitations/invitation-stats";
import { useInvitationsColumns } from "@/components/features/invitations/invitations-columns";
import { ROLES_WITH_ALL, INVITATION_STATUSES } from "@/lib/constants";
import { Select } from "@/components/ui/select";

export default function InvitationsPage() {
  const t = useTranslations();
  const inv = useInvitations();
  const deps = useDepartments();
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopy = async (url: string, id: number) => {
    await navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const columns = useInvitationsColumns({
    copiedId,
    onCopy: handleCopy,
    onResend: inv.handleResendInvitation,
    onRevoke: inv.handleRevokeInvitation,
    t,
  });

  return (
    <PageContent title={t("invitations.title")} subtitle={t("invitations.title")}>
      <CreateInvitationDialog
        open={inv.isCreateDialogOpen}
        onOpenChange={inv.setIsCreateDialogOpen}
        formData={inv.formData}
        onFormDataChange={(value: InvitationFormData | ((prev: InvitationFormData) => InvitationFormData)) => {
          if (typeof value === "function") {
            inv.setFormData(value(inv.formData));
          } else {
            inv.setFormData(value);
          }
        }}
        emailTouched={inv.emailTouched}
        onEmailTouchedChange={(touched: boolean) => inv.setEmailTouched(touched)}
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

      <EntityPage<InvitationItem, InvitationFormData>
        title={t("invitations.title")}
        items={inv.invitations}
        totalItems={inv.totalCount}
        pageSize={inv.pageSize}
        currentPage={inv.currentPage}
        isLoading={inv.loading}
        onPageSizeChange={inv.setPageSize}
        isCreateOpen={false}
        isEditOpen={false}
        selectedItem={null}
        onCreateOpen={() => {
          inv.resetForm();
          inv.setIsCreateDialogOpen(true);
        }}
        onEditOpen={() => {}}
        onDelete={inv.handleDeleteInvitation}
        onCloseDialog={() => {}}
        formData={inv.formData}
        onFormChange={(data) => inv.setFormData(data)}
        onSubmit={() => {}}
        isSubmitting={false}
        submitError={null}
        searchQuery={inv.searchQuery}
        onSearchChange={inv.setSearchQuery}
        onPageChange={inv.setCurrentPage}
        createButtonLabel={t("invitations.sendInvitation")}
        emptyStateMessage={t("invitations.empty")}
        searchPlaceholder={t("invitations.searchByEmail")}
        getItemKey={(item) => item.id}
        sortField={inv.sortField}
        sortDirection={inv.sortDirection}
        onSort={inv.toggleSort}
        filters={
          <>
            <Select
              options={ROLES_WITH_ALL}
              value={inv.roleFilter}
              onChange={inv.setRoleFilter}
              className="w-[180px]"
            />
            <Select
              options={INVITATION_STATUSES}
              value={inv.statusFilter}
              onChange={inv.setStatusFilter}
              className="w-[180px]"
            />
          </>
        }
        columns={columns}
        renderForm={() => null}
        isFormValid={true}
      />
    </PageContent>
  );
}
