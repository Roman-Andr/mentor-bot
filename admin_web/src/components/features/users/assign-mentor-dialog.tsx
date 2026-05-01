"use client";

import { useState, useEffect, useCallback } from "react";
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
import type { UserMentor } from "@/types";

export interface AssignMentorDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  userId: number | null;
  userName: string;
  onAssign: (userId: number, mentorId: number) => Promise<void>;
  onUnassign?: (mentorRelationId: number) => Promise<void>;
  currentMentor?: UserMentor | null;
}

export function AssignMentorDialog({
  isOpen,
  onOpenChange,
  userId,
  userName,
  onAssign,
  onUnassign,
  currentMentor,
}: AssignMentorDialogProps) {
  const t = useTranslations();
  const [selectedMentorId, setSelectedMentorId] = useState("");
  const [selectedMentorLabel, setSelectedMentorLabel] = useState("");
  const [assigning, setAssigning] = useState(false);
  const [unassigning, setUnassigning] = useState(false);

  // Reset state when dialog closes
  const resetState = useCallback(() => {
    setSelectedMentorId("");
    setSelectedMentorLabel("");
  }, [setSelectedMentorId, setSelectedMentorLabel]);

  useEffect(() => {
    if (!isOpen) {
      resetState();
    }
  }, [isOpen, resetState]);

  // Search for mentors (users with MENTOR role)
  const searchMentors = useCallback(async (query: string): Promise<SelectOption[]> => {
    const resp = await api.users.list({ search: query, role: "MENTOR", limit: 20 });
    if (!resp.success || !resp.data) return [];
    return resp.data.users.map((u) => ({
      value: String(u.id),
      label: `${u.first_name} ${u.last_name || ""}`.trim(),
      description: u.email,
    }));
  }, []);

  const handleAssign = async () => {
    if (!selectedMentorId || !userId) return;
    setAssigning(true);
    try {
      await onAssign(userId, parseInt(selectedMentorId));
      // Reset state after successful assignment
      setSelectedMentorId("");
      setSelectedMentorLabel("");
    } finally {
      setAssigning(false);
    }
  };

  const handleUnassign = async () => {
    if (!currentMentor?.id || !onUnassign) return;
    setUnassigning(true);
    try {
      await onUnassign(currentMentor.id);
    } finally {
      setUnassigning(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setSelectedMentorId("");
      setSelectedMentorLabel("");
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("users.assignMentor")}</DialogTitle>
          <DialogDescription>
            {t("users.assignMentorToUser", { name: userName })}
          </DialogDescription>
        </DialogHeader>

        {/* Current Mentor Section */}
        {currentMentor && (
          <div className="bg-muted rounded-md p-3">
            <p className="text-sm font-medium">{t("users.currentMentor")}</p>
            <div className="mt-2 flex items-center justify-between">
              <div>
                <p className="text-sm">{t("users.mentorId", { id: currentMentor.mentor_id })}</p>
                <p className="text-muted-foreground text-xs">
                  {currentMentor.is_active ? t("users.mentorActive") : t("users.mentorInactive")}
                </p>
              </div>
              {onUnassign && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleUnassign}
                  disabled={unassigning}
                >
                  {unassigning ? t("users.unassigning") : t("users.unassignMentor")}
                </Button>
              )}
            </div>
          </div>
        )}

        <div className="space-y-4 py-4">
          <div>
            <label className="mb-1 block text-sm font-medium">{t("users.selectMentor")}</label>
            <AsyncSearchableSelect
              value={selectedMentorId}
              onChange={(v) => {
                setSelectedMentorId(v);
                setSelectedMentorLabel("");
              }}
              onSearch={searchMentors}
              selectedLabel={selectedMentorLabel}
              placeholder={t("users.searchMentorPlaceholder")}
              searchPlaceholder={t("users.searchMentor")}
              minSearchLength={2}
              onOptionSelect={(opt) => setSelectedMentorLabel(opt.label)}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button 
            onClick={handleAssign} 
            disabled={!selectedMentorId || assigning}
          >
            {assigning ? t("users.assigning") : t("users.assign")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
