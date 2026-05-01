"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { PageContent } from "@/components/layout/page-content";
import { useInvitations, type InvitationItem, type InvitationFormData } from "@/hooks/use-invitations";
import { useDepartments } from "@/hooks/use-departments";
import { CreateInvitationDialog } from "@/components/features/invitations/create-invitation-dialog";
import { InvitationLinkDialog } from "@/components/features/invitations/invitation-link-dialog";
import { InvitationStats } from "@/components/features/invitations/invitation-stats";
import { useInvitationsColumns } from "@/components/features/invitations/invitations-columns";
import { getRoleOptions, getInvitationStatusOptions } from "@/lib/constants";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Plus } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { DataTableSkeleton } from "@/components/ui/table-skeleton";
import { SortableTableHead } from "@/components/ui/sortable-table-head";

export default function InvitationsPage() {
  const t = useTranslations();
  const inv = useInvitations();
  const deps = useDepartments();
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const roleOptions = getRoleOptions(t, true);
  const statusOptions = getInvitationStatusOptions(t, true);

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

  const handleCreateInvitation = () => {
    inv.resetForm();
    inv.setIsCreateDialogOpen(true);
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

      <DataTable
        loading={inv.loading}
        empty={inv.invitations.length === 0}
        currentPage={inv.currentPage}
        totalPages={Math.ceil(inv.totalCount / inv.pageSize)}
        totalCount={inv.totalCount}
        pageSize={inv.pageSize}
        onPageChange={inv.setCurrentPage}
        onPageSizeChange={inv.setPageSize}
        showPageSizeSelector={true}
        skeleton={<DataTableSkeleton columns={7} rows={5} showHeader={false} />}
        header={
          <CardHeader>
            <div className="flex items-center justify-between gap-4">
              <CardTitle>{t("invitations.title")}</CardTitle>
              <div className="flex items-center gap-2">
                <SearchInput
                  placeholder={t("invitations.searchByEmail")}
                  value={inv.searchQuery}
                  onChange={inv.setSearchQuery}
                />
                <Select
                  options={roleOptions}
                  value={inv.roleFilter}
                  onChange={inv.setRoleFilter}
                  className="w-[180px]"
                />
                <Select
                  options={statusOptions}
                  value={inv.statusFilter}
                  onChange={inv.setStatusFilter}
                  className="w-[180px]"
                />
                <Button onClick={handleCreateInvitation} className="gap-2">
                  <Plus className="size-4" />
                  {t("invitations.sendInvitation")}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
        emptyStateMessage={t("invitations.empty")}
      >
        <Table>
          <TableHeader>
            <TableRow>
              <SortableTableHead
                field="email"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("common.email")}
              </SortableTableHead>
              <SortableTableHead
                field="role"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("common.role")}
              </SortableTableHead>
              <SortableTableHead
                field="department"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("common.department")}
              </SortableTableHead>
              <SortableTableHead
                field="status"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("common.status")}
              </SortableTableHead>
              <SortableTableHead
                field="created_at"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("invitations.createdAt")}
              </SortableTableHead>
              <SortableTableHead
                field="expires_at"
                sortable={true}
                sortField={inv.sortField ?? null}
                sortDirection={inv.sortDirection}
                onSort={inv.toggleSort}
              >
                {t("invitations.expiresAt")}
              </SortableTableHead>
              <TableHead className="w-40">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {inv.invitations.map((invitation) => (
              <TableRow key={invitation.id}>
                {columns.map((column, idx) => (
                  <TableCell key={idx}>{column.cell(invitation)}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
