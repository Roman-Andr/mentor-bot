"use client";

import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export interface EntityFormDialogProps<TForm> {
  /** Whether the dialog is open */
  isOpen: boolean;
  /** Callback when dialog is closed (via close button, overlay click, or cancel) */
  onClose: () => void;
  /** Callback when form is submitted - passes the form data */
  onSubmit: (data: TForm) => void;
  /** Dialog title shown in the header */
  title: string;
  /** Optional dialog description shown below the title */
  description?: string;
  /** Label for the submit button (default: "Save") */
  submitLabel?: string;
  /** Label for the cancel button (default: "Cancel") */
  cancelLabel?: string;
  /** Whether the form is currently submitting (disables buttons) */
  isSubmitting?: boolean;
  /** Error message to display at the top of the form */
  error?: string | null;
  /** Form content (fields) */
  children: ReactNode;
  /** Maximum width class for the dialog (default: "max-w-lg") */
  maxWidth?: string;
  /** Additional className for the DialogContent */
  className?: string;
  /** Whether the form data is valid (controls submit button disabled state) */
  isValid?: boolean;
  /** Current form data - passed to onSubmit when form is submitted */
  formData: TForm;
}

/**
 * Generic, reusable form dialog component for entity creation/editing.
 * 
 * @example
 * ```tsx
 * <EntityFormDialog
 *   isOpen={isOpen}
 *   onClose={handleClose}
 *   onSubmit={handleSubmit}
 *   title="Create Department"
 *   submitLabel="Create"
 *   formData={formData}
 *   isValid={!!formData.name}
 *   error={error}
 *   isSubmitting={isPending}
 * >
 *   <div className="grid gap-2">
 *     <label>Name *</label>
 *     <Input 
 *       value={formData.name} 
 *       onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
 *     />
 *   </div>
 * </EntityFormDialog>
 * ```
 */
export function EntityFormDialog<TForm>({
  isOpen,
  onClose,
  onSubmit,
  title,
  description,
  submitLabel = "Save",
  cancelLabel = "Cancel",
  isSubmitting = false,
  error = null,
  children,
  maxWidth = "max-w-lg",
  className,
  isValid = true,
  formData,
}: EntityFormDialogProps<TForm>) {
  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        className={cn(
          "max-h-[90vh] overflow-y-auto",
          maxWidth,
          className
        )}
      >
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>

        {error && (
          <div className="bg-destructive/10 text-destructive rounded-md p-3 text-sm">
            {error}
          </div>
        )}

        <div className="grid gap-4 py-4">
          {children}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isSubmitting}
            type="button"
          >
            {cancelLabel}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !isValid}
            type="button"
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                {submitLabel}
              </span>
            ) : (
              submitLabel
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
