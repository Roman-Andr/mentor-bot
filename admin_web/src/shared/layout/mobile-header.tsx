"use client";

import { Menu, Bot } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useTranslations } from "@/shared/hooks/use-translations";

interface MobileHeaderProps {
  onMenuClick: () => void;
}

export function MobileHeader({ onMenuClick }: MobileHeaderProps) {
  const t = useTranslations();

  return (
    <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-4 border-b bg-background px-4 lg:hidden">
      <Button
        variant="ghost"
        size="icon"
        onClick={onMenuClick}
        aria-label={t("nav.openMenu")}
        className="shrink-0"
      >
        <Menu className="size-5" />
      </Button>
      <div className="flex items-center gap-2.5">
        <div className="flex size-7 items-center justify-center rounded-lg bg-primary">
          <Bot className="size-4 text-primary-foreground" />
        </div>
        <span className="font-semibold">{t("nav.appName")}</span>
      </div>
    </header>
  );
}
