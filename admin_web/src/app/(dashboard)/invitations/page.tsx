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
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, XCircle, Copy, Check } from "lucide-react";
import { ROLES, ROLES_WITH_ALL, INVITATION_STATUSES } from "@/lib/constants";

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
        isCreateOpen={inv.isCreateDialogOpen}
        isEditOpen={false}
        selectedItem={null}
        onCreateOpen={() => {
          inv.resetForm();
          inv.setIsCreateDialogOpen(true);
        }}
        onEditOpen={() => {}}
        onDelete={inv.handleDeleteInvitation}
        onCloseDialog={() => {
          inv.setIsCreateDialogOpen(false);
          inv.resetForm();
        }}
        formData={inv.formData}
        onFormChange={(data) => inv.setFormData(data)}
        onSubmit={inv.handleCreateInvitation}
        isSubmitting={inv.isCreating}
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
            <select
              value={inv.roleFilter}
              onChange={(e) => inv.setRoleFilter(e.target.value)}
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
            >
              {ROLES_WITH_ALL.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <select
              value={inv.statusFilter}
              onChange={(e) => inv.setStatusFilter(e.target.value)}
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
            >
              {INVITATION_STATUSES.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </>
        }
        columns={[
          {
            key: "email",
            header: t("invitations.email"),
            cell: (item) => <span className="font-medium">{item.email}</span>,
            sortable: true,
          },
          {
            key: "role",
            header: t("invitations.role"),
            cell: (item) => ROLES.find((r) => r.value === item.role)?.label || item.role,
            sortable: true,
          },
          {
            key: "department",
            header: t("common.department"),
            cell: (item) => item.department || "—",
            sortable: true,
          },
          {
            key: "status",
            header: t("common.status"),
            cell: (item) => <StatusBadge status={item.status} />,
            sortable: true,
          },
          {
            key: "createdAt",
            header: t("invitations.createdAt"),
            cell: (item) => new Date(item.createdAt).toLocaleDateString(),
            sortable: true,
          },
          {
            key: "expiresAt",
            header: t("invitations.expiresAt"),
            cell: (item) => new Date(item.expiresAt).toLocaleDateString(),
            sortable: true,
          },
          {
            key: "actions",
            header: "",
            cell: (item) => (
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground"
                  onClick={() => handleCopy(item.invitationUrl, item.id)}
                  title={t("invitations.copyLink")}
                >
                  {copiedId === item.id ? (
                    <Check className="size-4 text-green-600" />
                  ) : (
                    <Copy className="size-4" />
                  )}
                </Button>
                {item.status === "PENDING" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-blue-500"
                    title={t("invitations.resend")}
                    onClick={() => inv.handleResendInvitation(item.id)}
                  >
                    <RefreshCw className="size-4" />
                  </Button>
                )}
                {item.status === "PENDING" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-orange-500"
                    title={t("invitations.revoke")}
                    onClick={() => inv.handleRevokeInvitation(item.id)}
                  >
                    <XCircle className="size-4" />
                  </Button>
                )}
              </div>
            ),
            width: "w-40",
          },
        ]}
        renderForm={() => null}
        isFormValid={!!inv.formData.email && inv.emailTouched}
      />
    </PageContent>
  );
}
