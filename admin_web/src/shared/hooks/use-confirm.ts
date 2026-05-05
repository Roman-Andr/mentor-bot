"use client";

import { useContext } from "react";
import { ConfirmContext } from "@/shared/ui/confirm-dialog";

export function useConfirm() {
  return useContext(ConfirmContext);
}
