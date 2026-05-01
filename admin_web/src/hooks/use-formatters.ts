import { useLocale } from "next-intl";
import { useMemo } from "react";
import { formatDate, formatDateTime } from "@/lib/utils";

export function useFormatters() {
  const locale = useLocale();

  return useMemo(
    () => ({
      formatDate: (date: string | Date | null | undefined) => formatDate(date, locale),
      formatDateTime: (date: string | Date | null | undefined) => formatDateTime(date, locale),
    }),
    [locale],
  );
}
