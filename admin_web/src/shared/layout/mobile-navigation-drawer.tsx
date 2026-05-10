"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useAuth } from "@/shared/hooks/use-auth";
import { LanguageSwitcher } from "./language-switcher";
import { ThemeSwitcher } from "./theme-switcher";
import { ICON_MAP, NAV_GROUPS } from "./navigation-config";
import { X, LogOut, Bot } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import * as Dialog from "@radix-ui/react-dialog";

interface MobileNavigationDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MobileNavigationDrawer({ open, onOpenChange }: MobileNavigationDrawerProps) {
  const t = useTranslations();
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/login");
    onOpenChange(false);
  };

  const isActive = (href: string) =>
    pathname === href || (href !== "/" && pathname.startsWith(href));

  // Close drawer on pathname change
  useEffect(() => {
    onOpenChange(false);
  }, [pathname, onOpenChange]);

  const handleNavClick = () => {
    onOpenChange(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="mobile-sidebar-overlay fixed inset-0 z-50 bg-black/50" />
        <Dialog.Content
          className={cn(
            "mobile-sidebar-panel fixed inset-y-0 left-0 z-50 flex w-[calc(100vw-2rem)] max-w-sm flex-col border-r bg-background p-0 shadow-lg sm:max-w-md",
            "focus:outline-none",
          )}
          onEscapeKeyDown={() => onOpenChange(false)}
          onPointerDownOutside={() => onOpenChange(false)}
        >
          <Dialog.Title className="sr-only">{t("nav.openMenu")}</Dialog.Title>
          {/* Header */}
          <div className="mobile-sidebar-content mobile-sidebar-content-header flex h-16 shrink-0 items-center justify-between border-b px-4">
            <div className="flex items-center gap-2.5">
              <div className="flex size-7 items-center justify-center rounded-lg bg-primary">
                <Bot className="size-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">{t("nav.appName")}</span>
            </div>
            <Dialog.Close asChild>
              <button
                className="rounded-lg p-2 transition-colors hover:bg-muted"
                aria-label={t("common.close")}
                title={t("common.close")}
              >
                <X className="size-5" />
              </button>
            </Dialog.Close>
          </div>

          {/* User info */}
          {user && (
            <div className="mobile-sidebar-content mobile-sidebar-content-user border-b px-4 py-3">
              <div className="flex items-center gap-2.5">
                <div className="flex size-8 items-center justify-center rounded-full bg-primary/10">
                  <span className="text-xs font-semibold text-primary">
                    {user.email?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{user.email}</p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {user.role?.toLowerCase()}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="mobile-sidebar-content mobile-sidebar-content-nav flex-1 overflow-y-auto px-3 py-3">
            {NAV_GROUPS.map((group) => (
              <div key={group.labelKey} className="mb-4">
                <p className="mb-2 px-2 text-xs font-semibold tracking-wider text-muted-foreground uppercase">
                  {t(group.labelKey as Parameters<typeof t>[0])}
                </p>
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const active = isActive(item.href);
                    const IconComponent = ICON_MAP[item.icon as keyof typeof ICON_MAP];
                    const name = t(`nav.${item.key}` as Parameters<typeof t>[0]);
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={handleNavClick}
                        className={cn(
                          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                          active
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground",
                        )}
                      >
                        {IconComponent && <IconComponent className="size-4 shrink-0" />}
                        <span className="truncate">{name}</span>
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          {/* Footer */}
          <div className="mobile-sidebar-content mobile-sidebar-content-footer border-t p-4">
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <LanguageSwitcher />
                <ThemeSwitcher />
              </div>
              <button
                onClick={handleLogout}
                title={t("nav.logout")}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-[var(--foreground)]"
              >
                <LogOut className="size-4 shrink-0" />
                <span>{t("nav.logout")}</span>
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
