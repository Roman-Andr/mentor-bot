import { useMutation } from "@tanstack/react-query";
import { handleError } from "@/lib/error";
import { useCallback } from "react";
import type { UseEntityContext, UseEntityOptions } from "./types";

export function useEntityMutations<TItem, TForm, TCreatePayload, TUpdatePayload, TExtendedState>(
  options: Pick<
    UseEntityOptions<TItem, TForm, TCreatePayload, TUpdatePayload, TExtendedState>,
    "createFn" | "updateFn" | "deleteFn" | "queryKeyPrefix" | "onAfterCreate" | "onAfterUpdate" | "toCreatePayload"
  >,
  context: Pick<
    UseEntityContext<TItem, TForm, TExtendedState>,
    "toast" | "invalidate" | "extendedState" | "setExtendedState" | "selectedItem" | "formData"
  >,
  labels: {
    created: string;
    updated: string;
    deleted: string;
    createError: string;
    updateError: string;
    deleteError: string;
  },
  resetFormInternal: () => void,
  setIsCreateDialogOpen: (open: boolean) => void,
  setIsEditDialogOpen: (open: boolean) => void,
  setSelectedItem: (item: TItem | null) => void,
  toUpdatePayload: (form: TForm) => TUpdatePayload,
) {
  const { createFn, updateFn, deleteFn, toCreatePayload } = options;
  const { toast, invalidate } = context;

  const createMutation = useMutation<unknown, Error, TCreatePayload>({
    mutationFn: async (data) => {
      if (!createFn) throw new Error("createFn not provided");
      const result = await createFn(data);
      if (!result.success) {
        throw handleError(result.error, { action: "create" });
      }
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      setIsCreateDialogOpen(false);
      resetFormInternal();
      toast(labels.created, "success");
    },
    onError: () => toast(labels.createError, "error"),
  });

  const updateMutation = useMutation<unknown, Error, { id: number; data: TUpdatePayload }>({
    mutationFn: async ({ id, data }) => {
      if (!updateFn) throw new Error("updateFn not provided");
      const result = await updateFn(id, data);
      if (!result.success) {
        throw handleError(result.error, { action: "update", id });
      }
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      setIsEditDialogOpen(false);
      setSelectedItem(null);
      toast(labels.updated, "success");
    },
    onError: () => toast(labels.updateError, "error"),
  });

  const deleteMutation = useMutation<unknown, Error, number>({
    mutationFn: async (id) => {
      if (!deleteFn) throw new Error("deleteFn not provided");
      const result = await deleteFn(id);
      if (!result.success) throw new Error(result.error.message);
      return result.data;
    },
    onSuccess: () => {
      invalidate();
      toast(labels.deleted, "success");
    },
    onError: () => toast(labels.deleteError, "error"),
  });

  const handleSubmit = useCallback(() => {
    if (context.selectedItem) {
      const payload = toUpdatePayload(context.formData);
      updateMutation.mutate({ id: (context.selectedItem as Record<string, unknown>).id as number, data: payload });
    } else {
      const payload = toCreatePayload(context.formData);
      createMutation.mutate(payload);
    }
  }, [context.selectedItem, context.formData, toUpdatePayload, toCreatePayload, createMutation, updateMutation]);

  return {
    createMutation,
    updateMutation,
    deleteMutation,
    handleSubmit,
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
