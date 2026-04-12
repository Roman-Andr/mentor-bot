"use client";

import { useTranslations as useNextIntlTranslations } from "next-intl";

export type Namespace =
  | "common"
  | "dashboard"
  | "nav"
  | "knowledge"
  | "dialogues"
  | "templates"
  | "checklists"
  | "users"
  | "departments"
  | "analytics"
  | "invitations"
  | "settings"
  | "meetings"
  | "escalations"
  | "auth"
  | "pagination"
  | "statuses";

export function useTranslations(namespace?: Namespace) {
  return useNextIntlTranslations(namespace);
}
