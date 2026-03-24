import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SearchInput } from "@/components/ui/search-input";
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
import { ROLES } from "@/lib/constants";
import type { InvitationItem } from "@/hooks/use-invitations";

interface InvitationsTableProps {
  invitations: InvitationItem[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onResend: (id: number) => void;
  onRevoke: (id: number) => void;
  onDelete: (id: number) => void;
}

export function InvitationsTable({
  invitations,
  loading,
  searchQuery,
  onSearchChange,
  onResend,
  onRevoke,
  onDelete,
}: InvitationsTableProps) {
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopy = async (url: string, id: number) => {
    await navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <DataTable loading={loading} empty={invitations.length === 0}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Список приглашений</CardTitle>
          <SearchInput
            placeholder="Поиск по email..."
            value={searchQuery}
            onChange={onSearchChange}
          />
        </div>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Email</TableHead>
            <TableHead>Роль</TableHead>
            <TableHead>Отдел</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead>Создано</TableHead>
            <TableHead>Истекает</TableHead>
            <TableHead className="w-[160px]">Действия</TableHead>
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
              <TableCell>{new Date(invitation.createdAt).toLocaleDateString("ru-RU")}</TableCell>
              <TableCell>{new Date(invitation.expiresAt).toLocaleDateString("ru-RU")}</TableCell>
              <TableCell>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-muted-foreground"
                    onClick={() => handleCopy(invitation.invitationUrl, invitation.id)}
                    title="Скопировать ссылку"
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
                        title="Отправить повторно"
                      >
                        <RefreshCw className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-orange-500"
                        onClick={() => onRevoke(invitation.id)}
                        title="Отозвать"
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
                    title="Удалить"
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
