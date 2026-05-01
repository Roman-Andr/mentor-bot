"use client";

import { useState, useCallback } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { AsyncSearchableSelect, type SelectOption } from "@/components/ui/searchable-select";
import { api } from "@/lib/api";

export interface AssignDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  meetingId: number | null;
  meetingTitle: string;
  onAssign: (userId: number, meetingId: number) => Promise<void>;
}

export function AssignDialog({
  isOpen,
  onOpenChange,
  meetingId,
  meetingTitle,
  onAssign,
}: AssignDialogProps) {
  const t = useTranslations();
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedUserLabel, setSelectedUserLabel] = useState("");
  const [assigning, setAssigning] = useState(false);

  const searchUsers = useCallback(async (query: string): Promise<SelectOption[]> => {
    const resp = await api.users.list({ search: query, limit: 20 });
    if (!resp.success || !resp.data) return [];
    return resp.data.users.map((u) => ({
      value: String(u.id),
      label: `${u.first_name} ${u.last_name || ""}`.trim(),
      description: u.email,
    }));
  }, []);

  const handleAssign = async () => {
    if (!selectedUserId || !meetingId) return;
    setAssigning(true);
    try {
      await onAssign(parseInt(selectedUserId), meetingId);
      // Reset state after successful assignment
      setSelectedUserId("");
      setSelectedUserLabel("");
    } finally {
      setAssigning(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setSelectedUserId("");
      setSelectedUserLabel("");
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("meetings.assignMeeting")}</DialogTitle>
          <DialogDescription>
            {t("meetings.assignToUser", { title: meetingTitle })}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <label className="mb-1 block text-sm font-medium">{t("meetings.participant")}</label>
            <AsyncSearchableSelect
              value={selectedUserId}
              onChange={(v) => {
                setSelectedUserId(v);
                setSelectedUserLabel("");
              }}
              onSearch={searchUsers}
              selectedLabel={selectedUserLabel}
              placeholder={t("meetings.selectUser")}
              searchPlaceholder={t("meetings.searchUser")}
              minSearchLength={2}
              onOptionSelect={(opt) => setSelectedUserLabel(opt.label)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button onClick={handleAssign} disabled={!selectedUserId || assigning}>
            {assigning ? t("meetings.assigning") : t("meetings.assign")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
