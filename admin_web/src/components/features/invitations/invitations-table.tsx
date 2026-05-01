"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { StatusBadge } from "@/components/ui/status-badge";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
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
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Mail, Trash2, RefreshCw, Ban, Copy, Check } from "lucide-react";
import { useState } from "react";
import { getRoleOptions, getInvitationStatusOptions } from "@/lib/constants";
import type { InvitationItem } from "@/hooks/use-invitations";
import type { SortDirection } from "@/hooks/use-sorting";

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
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{t("invitations.title")}</CardTitle>
            <div className="flex gap-2">
              <SearchInput
                placeholder={t("invitations.searchByEmail")}
                value={searchQuery}
                onChange={onSearchChange}
              />
              <Select value={roleFilter} onChange={onRoleFilterChange} options={roleOptions} />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={statusOptions}
              />
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" onClick={onReset}>
                    {t("common.reset")}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t("common.reset")}</p>
                </TooltipContent>
              </Tooltip>
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
                  <Mail className="text-muted-foreground size-4" />
                  <span className="font-medium">{invitation.email}</span>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="outline">
                  {t(`statuses.${invitation.role}`)}
                </Badge>
              </TableCell>
              <TableCell>{invitation.department}</TableCell>
              <TableCell>
                <StatusBadge status={invitation.status} />
              </TableCell>
              <TableCell>{new Date(invitation.createdAt).toLocaleDateString()}</TableCell>
              <TableCell>{new Date(invitation.expiresAt).toLocaleDateString()}</TableCell>
              <TableCell>
                <TooltipProvider>
                  <div className="flex gap-1">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-muted-foreground"
                          onClick={() => handleCopy(invitation.invitationUrl, invitation.id)}
                          aria-label={t("invitations.copyLink")}
                        >
                          {copiedId === invitation.id ? (
                            <Check className="size-4 text-green-600" />
                          ) : (
                            <Copy className="size-4" />
                          )}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t("invitations.copyLink")}</p>
                      </TooltipContent>
                    </Tooltip>
                    {invitation.status === "PENDING" && (
                      <>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-blue-500"
                              onClick={() => onResend(invitation.id)}
                              aria-label={t("invitations.resend")}
                            >
                              <RefreshCw className="size-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{t("invitations.resend")}</p>
                          </TooltipContent>
                        </Tooltip>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-orange-500"
                              onClick={() => onRevoke(invitation.id)}
                              aria-label={t("invitations.revoke")}
                            >
                              <Ban className="size-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{t("invitations.revoke")}</p>
                          </TooltipContent>
                        </Tooltip>
                      </>
                    )}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500"
                          onClick={() => onDelete(invitation.id)}
                          aria-label={t("common.delete")}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t("common.delete")}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                </TooltipProvider>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}