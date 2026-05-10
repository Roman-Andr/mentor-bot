"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { StatusBadge } from "@/shared/ui/status-badge";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import {
  TableActions,
  buildCopyAction,
  buildResendAction,
  buildRevokeAction,
  buildDeleteAction,
} from "@/shared/components";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { DataTableSkeleton } from "@/shared/ui/table-skeleton";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import { Mail } from "lucide-react";
import { useState } from "react";
import { cn } from "@/shared/lib/utils";
import { getRoleOptions, getInvitationStatusOptions } from "@/shared/lib/constants";
import type { InvitationItem } from "@/shared/hooks/use-invitations";
import type { SortDirection } from "@/shared/hooks/use-sorting";

interface InvitationsTableProps {
  invitations: InvitationItem[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  roleFilter: string;
  onRoleFilterChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  onReset: () => void;
  onResend: (id: number) => void;
  onRevoke: (id: number) => void;
  onDelete: (id: number) => void;
  currentPage?: number;
  totalPages?: number;
  totalCount?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

export function InvitationsTable({
  invitations,
  loading,
  searchQuery,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  statusFilter,
  onStatusFilterChange,
  onReset,
  onResend,
  onRevoke,
  onDelete,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortField,
  sortDirection = "asc",
  onSort,
}: InvitationsTableProps) {
  const t = useTranslations();
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const roleOptions = getRoleOptions(t, true);
  const statusOptions = getInvitationStatusOptions(t, true);

  const handleCopy = async (url: string, id: number) => {
    await navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const mobileView = (
    <div className="space-y-3 p-4">
      {invitations.map((invitation) => (
        <InvitationCard
          key={invitation.id}
          invitation={invitation}
          onResend={onResend}
          onRevoke={onRevoke}
          onDelete={onDelete}
          handleCopy={handleCopy}
          copiedId={copiedId}
          t={t}
        />
      ))}
    </div>
  );

  const ROLE_STYLES: Record<string, string> = {
    ADMIN:
      "bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-950/50 dark:text-violet-300 dark:border-violet-800",
    HR: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800",
    MENTOR:
      "bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-950/50 dark:text-teal-300 dark:border-teal-800",
    NEWBIE:
      "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800",
  };

  function InvitationCard({
    invitation,
    onResend,
    onRevoke,
    onDelete,
    handleCopy,
    copiedId,
    t,
  }: {
    invitation: InvitationItem;
    onResend: (id: number) => void;
    onRevoke: (id: number) => void;
    onDelete: (id: number) => void;
    handleCopy: (url: string, id: number) => Promise<void>;
    copiedId: number | null;
    t: (key: string) => string;
  }) {
    const isRevoked = invitation.status === "REVOKED";

    return (
      <Card>
        <CardContent className="p-4">
          {/* Header: Email + Status */}
          <div className="mb-3 flex items-start gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Mail className="size-4 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h3 className="truncate font-semibold">{invitation.email}</h3>
                <StatusBadge status={invitation.status} />
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">{t("common.role")}: </span>
              <span
                className={cn(
                  "inline-flex items-center rounded-full border px-2 py-0.5 font-semibold",
                  ROLE_STYLES[invitation.role] ?? "bg-muted text-muted-foreground",
                )}
              >
                {t(`statuses.${invitation.role}`)}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("common.department")}: </span>
              <span>{invitation.department || "—"}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("invitations.createdAt")}: </span>
              <span>{new Date(invitation.createdAt).toLocaleDateString()}</span>
            </div>
            <div>
              <span className="text-muted-foreground">{t("invitations.expiresAt")}: </span>
              <span>{new Date(invitation.expiresAt).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Footer: Actions */}
          <div
            className="grid grid-cols-2 gap-2 border-t pt-3 sm:flex sm:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            {!isRevoked && (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopy(invitation.invitationUrl, invitation.id)}
                >
                  {copiedId === invitation.id ? t("common.copied") : t("invitations.copyLink")}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onResend(invitation.id)}
                  disabled={invitation.status !== "PENDING"}
                >
                  {t("invitations.resend")}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onRevoke(invitation.id)}
                  disabled={invitation.status !== "PENDING"}
                >
                  {t("invitations.revoke")}
                </Button>
              </>
            )}
            <Button size="sm" variant="destructive" onClick={() => onDelete(invitation.id)}>
              {t("common.delete")}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <DataTable
      loading={loading}
      empty={invitations.length === 0}
      currentPage={currentPage}
      totalPages={totalPages}
      totalCount={totalCount}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      showPageSizeSelector={!!onPageSizeChange}
      skeleton={<DataTableSkeleton columns={7} rows={5} showHeader={false} />}
      mobileView={mobileView}
      header={
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>{t("invitations.title")}</CardTitle>
            <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
              <SearchInput
                placeholder={t("invitations.searchByEmail")}
                value={searchQuery}
                onChange={onSearchChange}
                className="w-full sm:w-auto"
              />
              <Select
                value={roleFilter}
                onChange={onRoleFilterChange}
                options={roleOptions}
                className="w-full sm:w-auto"
              />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
                className="w-full sm:w-auto"
              />
              <Button variant="outline" onClick={onReset} className="w-full sm:w-auto">
                {t("common.reset")}
              </Button>
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead
              field="email"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.email")}
            </SortableTableHead>
            <SortableTableHead
              field="role"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.role")}
            </SortableTableHead>
            <SortableTableHead
              field="department"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.department")}
            </SortableTableHead>
            <SortableTableHead
              field="status"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("common.status")}
            </SortableTableHead>
            <SortableTableHead
              field="created_at"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("invitations.createdAt")}
            </SortableTableHead>
            <SortableTableHead
              field="expires_at"
              sortable={!!onSort}
              sortField={sortField ?? null}
              sortDirection={sortDirection}
              onSort={onSort ?? (() => {})}
            >
              {t("invitations.expiresAt")}
            </SortableTableHead>
            <TableHead className="w-40">{t("common.actions")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {invitations.map((invitation) => (
            <TableRow key={invitation.id}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Mail className="size-4 text-muted-foreground" />
                  <span className="font-medium">{invitation.email}</span>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="outline">{t(`statuses.${invitation.role}`)}</Badge>
              </TableCell>
              <TableCell>{invitation.department}</TableCell>
              <TableCell>
                <StatusBadge status={invitation.status} />
              </TableCell>
              <TableCell>{new Date(invitation.createdAt).toLocaleDateString()}</TableCell>
              <TableCell>{new Date(invitation.expiresAt).toLocaleDateString()}</TableCell>
              <TableCell>
                <TableActions
                  actions={[
                    buildResendAction(
                      () => onResend(invitation.id),
                      t("invitations.resend"),
                      invitation.status === "PENDING",
                    ),
                    buildCopyAction(
                      () => handleCopy(invitation.invitationUrl, invitation.id),
                      t("invitations.copyLink"),
                      invitation.status !== "REVOKED",
                      copiedId === invitation.id,
                    ),
                    buildRevokeAction(
                      () => onRevoke(invitation.id),
                      t("invitations.revoke"),
                      invitation.status === "PENDING",
                    ),
                    buildDeleteAction(() => onDelete(invitation.id), t("common.delete")),
                  ]}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}
