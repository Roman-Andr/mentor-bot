"use client";

import { useCallback, useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Select } from "@/shared/ui/select";
import { SearchInput } from "@/shared/ui/search-input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { PageContent } from "@/shared/layout/page-content";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import {
  TableActions,
  buildCompleteAction,
  buildDeleteAction,
  buildAssignAction,
} from "@/shared/components";
import { getEscalationStatusOptions, getEscalationTypeOptions } from "@/shared/lib/constants";
import { formatDateTime } from "@/shared/lib/utils";
import { useEscalations } from "@/shared/hooks/use-escalations";
import { useToast } from "@/shared/hooks/use-toast";
import { api } from "@/shared/lib/api";
import { SortableTableHead } from "@/shared/ui/sortable-table-head";
import { AlertTriangle, Clock, CheckCircle2, XCircle, UserCheck } from "lucide-react";
import { UserAvatar } from "@/shared/ui/user-avatar";
import { cn } from "@/shared/lib/utils";
import { FormDialog } from "@/shared/ui/form-dialog";
import { Label } from "@/shared/ui/label";
import { AsyncSearchableSelect, type SelectOption } from "@/shared/ui/searchable-select";
import type { EscalationItem } from "@/shared/hooks/use-escalations";

const STATUS_CONFIG: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  OPEN: {
    label: "Open",
    icon: <AlertTriangle className="size-3" />,
    cls: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
  },
  IN_PROGRESS: {
    label: "In Progress",
    icon: <Clock className="size-3" />,
    cls: "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
  },
  RESOLVED: {
    label: "Resolved",
    icon: <CheckCircle2 className="size-3" />,
    cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300",
  },
  CLOSED: {
    label: "Closed",
    icon: <XCircle className="size-3" />,
    cls: "bg-muted text-muted-foreground",
  },
};

interface AssignDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  escalationId: number | null;
  onAssigned: () => void;
}

function AssignDialog({ open, onOpenChange, escalationId, onAssigned }: AssignDialogProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const [selectedAssigneeId, setSelectedAssigneeId] = useState("");
  const [selectedAssigneeLabel, setSelectedAssigneeLabel] = useState("");
  const [loading, setLoading] = useState(false);

  const searchUsers = useCallback(async (query: string): Promise<SelectOption[]> => {
    const responses = await Promise.all([
      api.users.list({ search: query, role: "ADMIN", limit: 20 }),
      api.users.list({ search: query, role: "HR", limit: 20 }),
    ]);

    const users = responses.flatMap((resp) => (resp.success && resp.data ? resp.data.users : []));
    const uniqueUsers = Array.from(new Map(users.map((user) => [user.id, user])).values());

    return uniqueUsers.map((u) => ({
      value: String(u.id),
      label: `${u.first_name} ${u.last_name || ""}`.trim(),
      description: u.email,
    }));
  }, []);

  const handleSubmit = async () => {
    if (!escalationId || !selectedAssigneeId) return;
    setLoading(true);
    try {
      await api.escalations.assign(escalationId, Number(selectedAssigneeId));
      toast(t("escalations.assigned") || "Escalation assigned", "success");
      onAssigned();
      onOpenChange(false);
      setSelectedAssigneeId("");
      setSelectedAssigneeLabel("");
    } catch {
      toast(t("common.error") || "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setSelectedAssigneeId("");
      setSelectedAssigneeLabel("");
    }
    onOpenChange(open);
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
      title={t("escalations.assignTo") || "Assign escalation"}
      isSubmitting={loading}
      onSubmit={handleSubmit}
      onCancel={() => {
        handleOpenChange(false);
      }}
    >
      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("escalations.assignee") || "Assignee"}</Label>
          <AsyncSearchableSelect
            value={selectedAssigneeId}
            onChange={(v) => {
              setSelectedAssigneeId(v);
              setSelectedAssigneeLabel("");
            }}
            onSearch={searchUsers}
            selectedLabel={selectedAssigneeLabel}
            placeholder={t("escalations.searchAssigneePlaceholder") || "Search for user..."}
            searchPlaceholder={t("escalations.searchAssignee") || "Search user by name or email"}
            minSearchLength={2}
            onOptionSelect={(opt) => setSelectedAssigneeLabel(opt.label)}
          />
          <p className="text-xs text-muted-foreground">
            {t("escalations.assigneeHint") ||
              "Search for HR or admin user to assign this escalation"}
          </p>
        </div>
      </div>
    </FormDialog>
  );
}

function StatusChip({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? {
    label: status,
    icon: null,
    cls: "bg-muted text-muted-foreground",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        cfg.cls,
      )}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

function EscalationCard({
  escalation,
  getUserName,
  onAssign,
  onResolve,
  onDelete,
  t,
}: {
  escalation: EscalationItem;
  getUserName: (id: number) => string;
  onAssign: (id: number) => void;
  onResolve: (id: number) => void;
  onDelete: (id: number) => void;
  t: (key: string) => string;
}) {
  const isResolved = escalation.status === "RESOLVED";

  return (
    <Card
      className={cn(
        "transition-colors",
        escalation.status === "OPEN" && "border-l-4 border-l-amber-500",
        escalation.status === "IN_PROGRESS" && "border-l-4 border-l-blue-500",
      )}
    >
      <CardContent className="p-4">
        {/* Header: User + Status */}
        <div className="mb-3 flex items-start gap-3">
          <UserAvatar name={getUserName(escalation.userId)} id={escalation.userId} />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate font-semibold">{getUserName(escalation.userId)}</h3>
              <StatusChip status={escalation.status} />
            </div>
            <span className="text-xs text-muted-foreground">#{escalation.id}</span>
          </div>
        </div>

        {/* Metadata */}
        <div className="mb-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-muted-foreground">{t("escalations.subject")}: </span>
            <span className="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs font-medium">
              {escalation.type}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("escalations.description")}: </span>
            <span className="line-clamp-1 text-muted-foreground">{escalation.source}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("escalations.assignedTo")}: </span>
            {escalation.assignedTo ? (
              <div className="flex items-center gap-1">
                <UserCheck className="size-3 text-emerald-500" />
                <span>{getUserName(escalation.assignedTo)}</span>
              </div>
            ) : (
              <span>—</span>
            )}
          </div>
          <div>
            <span className="text-muted-foreground">{t("escalations.priority")}: </span>
            <span className="line-clamp-1 text-muted-foreground">{escalation.reason || "—"}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("escalations.createdAt")}: </span>
            <span>{formatDateTime(escalation.createdAt)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">{t("escalations.resolvedAt")}: </span>
            <span>{escalation.resolvedAt ? formatDateTime(escalation.resolvedAt) : "—"}</span>
          </div>
        </div>

        {/* Footer: Actions */}
        <div className="flex flex-col items-center gap-2 border-t pt-3 sm:flex-row">
          {!isResolved && (
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              onClick={() => onAssign(escalation.id)}
            >
              {t("escalations.assign") || "Assign"}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onResolve(escalation.id)}
            disabled={escalation.status === "RESOLVED" || escalation.status === "CLOSED"}
          >
            {t("common.confirm")}
          </Button>
          <Button size="sm" variant="destructive" onClick={() => onDelete(escalation.id)}>
            {t("common.delete")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function EscalationsWidget() {
  const t = useTranslations();
  const e = useEscalations();

  const [assigningId, setAssigningId] = useState<number | null>(null);

  const statusOptions = getEscalationStatusOptions(t, true);
  const typeOptions = getEscalationTypeOptions(t, true);

  const openCount = e.escalations.filter((esc) => esc.status === "OPEN").length;
  const inProgressCount = e.escalations.filter((esc) => esc.status === "IN_PROGRESS").length;

  const mobileView = (
    <div className="space-y-3 p-4">
      {e.escalations.map((esc) => (
        <EscalationCard
          key={esc.id}
          escalation={esc}
          getUserName={(id) => e.getUserName(id)}
          onAssign={setAssigningId}
          onResolve={e.handleResolve}
          onDelete={e.handleDelete}
          t={t}
        />
      ))}
    </div>
  );

  return (
    <PageContent title={t("escalations.title")} subtitle={t("escalations.title")}>
      <AssignDialog
        open={assigningId !== null}
        onOpenChange={(open) => !open && setAssigningId(null)}
        escalationId={assigningId}
        onAssigned={e.loadEscalations}
      />

      <DataTable
        loading={e.loading}
        empty={e.escalations.length === 0}
        emptyMessage={t("common.noData")}
        currentPage={e.currentPage}
        totalPages={e.totalPages}
        totalCount={e.totalCount}
        pageSize={e.pageSize}
        onPageChange={e.setCurrentPage}
        onPageSizeChange={e.setPageSize}
        showPageSizeSelector={true}
        mobileView={mobileView}
        header={
          <CardHeader>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
                  {t("escalations.title")}{" "}
                  <span className="text-sm font-normal text-muted-foreground">
                    ({e.totalCount})
                  </span>
                </CardTitle>
                {openCount > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-950/50 dark:text-amber-300">
                    <AlertTriangle className="size-3" />
                    {openCount} {t("escalations.open") || "open"}
                  </span>
                )}
                {inProgressCount > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
                    <Clock className="size-3" />
                    {inProgressCount} {t("escalations.inProgress") || "in progress"}
                  </span>
                )}
              </div>
              <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
                <SearchInput
                  value={e.searchQuery}
                  onChange={e.setSearchQuery}
                  className="w-full sm:w-auto"
                />
                <Select
                  value={e.statusFilter}
                  onChange={e.setStatusFilter}
                  options={statusOptions}
                  className="w-full sm:w-auto"
                />
                <Select
                  value={e.typeFilter}
                  onChange={e.setTypeFilter}
                  options={typeOptions}
                  className="w-full sm:w-auto"
                />
                <Button variant="outline" onClick={e.resetFilters} className="w-full sm:w-auto">
                  {t("common.clear")}
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
                field="id"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
                className="w-16"
              >
                ID
              </SortableTableHead>
              <SortableTableHead
                field="userId"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.user")}
              </SortableTableHead>
              <SortableTableHead
                field="type"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.subject")}
              </SortableTableHead>
              <SortableTableHead
                field="source"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.description")}
              </SortableTableHead>
              <SortableTableHead
                field="status"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.status")}
              </SortableTableHead>
              <TableHead>{t("escalations.assignedTo")}</TableHead>
              <SortableTableHead
                field="reason"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.priority")}
              </SortableTableHead>
              <SortableTableHead
                field="createdAt"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.createdAt")}
              </SortableTableHead>
              <SortableTableHead
                field="resolvedAt"
                sortable
                sortField={e.sortField}
                sortDirection={e.sortDirection}
                onSort={e.toggleSort}
              >
                {t("escalations.resolvedAt")}
              </SortableTableHead>
              <TableHead className="w-28">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {e.escalations.map((esc) => (
              <TableRow
                key={esc.id}
                className={cn(
                  "transition-colors hover:bg-muted",
                  esc.status === "OPEN" && "border-l-2 border-l-amber-500",
                  esc.status === "IN_PROGRESS" && "border-l-2 border-l-blue-500",
                )}
              >
                <TableCell className="font-mono text-xs text-muted-foreground">#{esc.id}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <UserAvatar name={e.getUserName(esc.userId)} id={esc.userId} size="sm" />
                    <span className="text-sm">{e.getUserName(esc.userId)}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium">
                    {esc.type}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">{esc.source}</span>
                </TableCell>
                <TableCell>
                  <StatusChip status={esc.status} />
                </TableCell>
                <TableCell>
                  {esc.assignedTo ? (
                    <div className="flex items-center gap-1.5">
                      <UserCheck className="size-3.5 text-emerald-500" />
                      <span className="text-xs">{e.getUserName(esc.assignedTo)}</span>
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell>
                  <span className="line-clamp-1 max-w-36 text-xs text-muted-foreground">
                    {esc.reason || "—"}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">
                    {formatDateTime(esc.createdAt)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">
                    {esc.resolvedAt ? formatDateTime(esc.resolvedAt) : "—"}
                  </span>
                </TableCell>
                <TableCell>
                  <TableActions
                    actions={[
                      buildAssignAction(
                        () => setAssigningId(esc.id),
                        t("escalations.assign") || "Assign",
                        esc.status !== "RESOLVED",
                      ),
                      buildCompleteAction(
                        () => e.handleResolve(esc.id),
                        t("common.confirm"),
                        esc.status !== "RESOLVED" && esc.status !== "CLOSED",
                      ),
                      buildDeleteAction(() => e.handleDelete(esc.id), t("common.delete")),
                    ]}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
