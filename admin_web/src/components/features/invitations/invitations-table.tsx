"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Mail, Trash2, RefreshCw, Ban, Copy, Check } from "lucide-react";
import { useState } from "react";
import { ROLES, ROLES_WITH_ALL, INVITATION_STATUSES } from "@/lib/constants";
import type { InvitationItem } from "@/hooks/use-invitations";

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
}: InvitationsTableProps) {
  const t = useTranslations("invitations");
  const tCommon = useTranslations("common");
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopy = async (url: string, id: number) => {
    await navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <DataTable
      loading={loading}
      empty={invitations.length === 0}
      header={
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{t("title")}</CardTitle>
            <div className="flex gap-2">
              <SearchInput
                placeholder={t("searchByEmail")}
                value={searchQuery}
                onChange={onSearchChange}
              />
              <Select value={roleFilter} onChange={onRoleFilterChange} options={ROLES_WITH_ALL} />
              <Select
                value={statusFilter}
                onChange={onStatusFilterChange}
                options={INVITATION_STATUSES}
              />
              <Button variant="outline" onClick={onReset}>
                {tCommon("reset")}
              </Button>
            </div>
          </div>
        </CardHeader>
      }
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{tCommon("email")}</TableHead>
            <TableHead>{tCommon("role")}</TableHead>
            <TableHead>{tCommon("department")}</TableHead>
            <TableHead>{tCommon("status")}</TableHead>
            <TableHead>{t("createdAt")}</TableHead>
            <TableHead>{t("expiresAt")}</TableHead>
            <TableHead className="w-[160px]">{tCommon("actions")}</TableHead>
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
                  {ROLES.find((r) => r.value === invitation.role)?.label}
                </Badge>
              </TableCell>
              <TableCell>{invitation.department}</TableCell>
              <TableCell>
                <StatusBadge status={invitation.status} />
              </TableCell>
              <TableCell>{new Date(invitation.createdAt).toLocaleDateString()}</TableCell>
              <TableCell>{new Date(invitation.expiresAt).toLocaleDateString()}</TableCell>
              <TableCell>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-muted-foreground"
                    onClick={() => handleCopy(invitation.invitationUrl, invitation.id)}
                    title={t("copyLink")}
                  >
                    {copiedId === invitation.id ? (
                      <Check className="size-4 text-green-600" />
                    ) : (
                      <Copy className="size-4" />
                    )}
                  </Button>
                  {invitation.status === "PENDING" && (
                    <>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-blue-500"
                        onClick={() => onResend(invitation.id)}
                        title={t("resend")}
                      >
                        <RefreshCw className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-orange-500"
                        onClick={() => onRevoke(invitation.id)}
                        title={t("revoke")}
                      >
                        <Ban className="size-4" />
                      </Button>
                    </>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-500"
                    onClick={() => onDelete(invitation.id)}
                    title={tCommon("delete")}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </DataTable>
  );
}