"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useTranslations } from "@/hooks/use-translations";

interface FormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  title: string;
  description?: string;
  submitLabel?: string;
  cancelLabel?: string;
  canSubmit?: boolean;
  isSubmitting?: boolean;
  onSubmit: () => void;
  onCancel: () => void;
  children: React.ReactNode;
}

export function FormDialog({
  open,
  onOpenChange,
  mode,
  title,
  description,
  submitLabel,
  cancelLabel,
  canSubmit = true,
  isSubmitting = false,
  onSubmit,
  onCancel,
  children,
}: FormDialogProps) {
  const isEdit = mode === "edit";
  const t = useTranslations("common");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <div className="grid gap-4 py-4">{children}</div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
            {cancelLabel || t("cancel")}
          </Button>
          <Button onClick={onSubmit} disabled={!canSubmit || isSubmitting}>
            {isSubmitting ? t("saving") : submitLabel || (isEdit ? t("save") : t("add"))}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
