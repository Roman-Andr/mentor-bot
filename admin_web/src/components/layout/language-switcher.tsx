"use client";

import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (newLocale: string) => {
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`;
    startTransition(() => {
      router.refresh();
    });
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => switchLocale("ru")}
        className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
          locale === "ru"
            ? "bg-blue-600 text-white"
            : "text-slate-400 hover:bg-slate-800 hover:text-white"
        }`}
        disabled={isPending}
      >
        RU
      </button>
      <button
        onClick={() => switchLocale("en")}
        className={`rounded px-2 py-1 text-xs font-medium transition-colors ${
          locale === "en"
            ? "bg-blue-600 text-white"
            : "text-slate-400 hover:bg-slate-800 hover:text-white"
        }`}
        disabled={isPending}
      >
        EN
      </button>
    </div>
  );
}