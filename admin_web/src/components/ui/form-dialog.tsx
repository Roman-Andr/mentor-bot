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
  cancelLabel = "Отмена",
  canSubmit = true,
  isSubmitting = false,
  onSubmit,
  onCancel,
  children,
}: FormDialogProps) {
  const isEdit = mode === "edit";

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
            {cancelLabel}
          </Button>
          <Button onClick={onSubmit} disabled={!canSubmit || isSubmitting}>
            {isSubmitting ? "Сохранение..." : submitLabel || (isEdit ? "Сохранить" : "Добавить")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
