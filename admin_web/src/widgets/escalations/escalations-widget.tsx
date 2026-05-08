"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Select } from "@/shared/ui/select";
import { SearchInput } from "@/shared/ui/search-input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { DataTable } from "@/shared/ui/data-table";
import { PageContent } from "@/shared/layout/page-content";
import { CardHeader, CardTitle } from "@/shared/ui/card";
import { TableActions, buildCompleteAction, buildDeleteAction, buildAssignAction } from "@/shared/components";
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
import { Input } from "@/shared/ui/input";

const STATUS_CONFIG: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  OPEN: { label: "Open", icon: <AlertTriangle className="size-3" />, cls: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300" },
  IN_PROGRESS: { label: "In Progress", icon: <Clock className="size-3" />, cls: "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300" },
  RESOLVED: { label: "Resolved", icon: <CheckCircle2 className="size-3" />, cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300" },
  CLOSED: { label: "Closed", icon: <XCircle className="size-3" />, cls: "bg-muted text-muted-foreground" },
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
  const [assigneeId, setAssigneeId] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!escalationId || !assigneeId) return;
    setLoading(true);
    try {
      await api.escalations.assign(escalationId, Number(assigneeId));
      toast(t("escalations.assigned") || "Escalation assigned", "success");
      onAssigned();
      onOpenChange(false);
      setAssigneeId("");
    } catch {
      toast(t("common.error") || "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={t("escalations.assignTo") || "Assign escalation"}
      isSubmitting={loading}
      onSubmit={handleSubmit}
      onCancel={() => { onOpenChange(false); setAssigneeId(""); }}
    >
      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("escalations.assigneeId") || "Assignee User ID"}</Label>
          <Input type="number" value={assigneeId} onChange={(ev) => setAssigneeId(ev.target.value)} placeholder="User ID" required autoFocus />
          <p className="text-muted-foreground text-xs">{t("escalations.assigneeHint") || "Enter the ID of the HR or admin user to assign"}</p>
        </div>
      </div>
    </FormDialog>
  );
}

function StatusChip({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, icon: null, cls: "bg-muted text-muted-foreground" };
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", cfg.cls)}>
      {cfg.icon}
      {cfg.label}
    </span>
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
        header={
          <CardHeader>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <CardTitle>
                  {t("escalations.title")}{" "}
                  <span className="text-muted-foreground text-sm font-normal">({e.totalCount})</span>
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
              <div className="flex flex-wrap gap-2">
                <SearchInput value={e.searchQuery} onChange={e.setSearchQuery} />
                <Select value={e.statusFilter} onChange={e.setStatusFilter} options={statusOptions} />
                <Select value={e.typeFilter} onChange={e.setTypeFilter} options={typeOptions} />
                <Button variant="outline" onClick={e.resetFilters}>{t("common.clear")}</Button>
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <SortableTableHead field="id" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort} className="w-16">ID</SortableTableHead>
              <SortableTableHead field="userId" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.user")}</SortableTableHead>
              <SortableTableHead field="type" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.subject")}</SortableTableHead>
              <SortableTableHead field="source" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.description")}</SortableTableHead>
              <SortableTableHead field="status" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.status")}</SortableTableHead>
              <TableHead>{t("escalations.assignedTo")}</TableHead>
              <SortableTableHead field="reason" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.priority")}</SortableTableHead>
              <SortableTableHead field="createdAt" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.createdAt")}</SortableTableHead>
              <SortableTableHead field="resolvedAt" sortable sortField={e.sortField} sortDirection={e.sortDirection} onSort={e.toggleSort}>{t("escalations.resolvedAt")}</SortableTableHead>
              <TableHead className="w-28">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {e.escalations.map((esc) => (
              <TableRow
                key={esc.id}
                className={cn(
                  "hover:bg-muted transition-colors",
                  esc.status === "OPEN" && "border-l-2 border-l-amber-500",
                  esc.status === "IN_PROGRESS" && "border-l-2 border-l-blue-500",
                )}
              >
                <TableCell className="text-muted-foreground font-mono text-xs">#{esc.id}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <UserAvatar name={e.getUserName(esc.userId)} id={esc.userId} size="sm" />
                    <span className="text-sm">{e.getUserName(esc.userId)}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium">{esc.type}</span>
                </TableCell>
                <TableCell><span className="text-muted-foreground text-xs">{esc.source}</span></TableCell>
                <TableCell><StatusChip status={esc.status} /></TableCell>
                <TableCell>
                  {esc.assignedTo ? (
                    <div className="flex items-center gap-1.5">
                      <UserCheck className="text-emerald-500 size-3.5" />
                      <span className="text-xs">{e.getUserName(esc.assignedTo)}</span>
                    </div>
                  ) : (
                    <span className="text-muted-foreground text-xs">—</span>
                  )}
                </TableCell>
                <TableCell><span className="text-muted-foreground line-clamp-1 max-w-36 text-xs">{esc.reason || "—"}</span></TableCell>
                <TableCell><span className="text-muted-foreground text-xs">{formatDateTime(esc.createdAt)}</span></TableCell>
                <TableCell><span className="text-muted-foreground text-xs">{esc.resolvedAt ? formatDateTime(esc.resolvedAt) : "—"}</span></TableCell>
                <TableCell>
                  <TableActions
                    actions={[
                      buildAssignAction(() => setAssigningId(esc.id), t("escalations.assign") || "Assign"),
                      buildCompleteAction(() => e.handleResolve(esc.id), t("common.confirm"), esc.status !== "RESOLVED" && esc.status !== "CLOSED"),
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
