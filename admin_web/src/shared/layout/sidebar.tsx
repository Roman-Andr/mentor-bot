"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations } from "@/shared/hooks/use-translations";
import { cn } from "@/shared/lib/utils";
import { useAuth } from "@/shared/hooks/use-auth";
import { LanguageSwitcher } from "./language-switcher";
import { ThemeSwitcher } from "./theme-switcher";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import {
  LayoutDashboard,
  Users,
  FileText,
  ClipboardCheck,
  BookOpen,
  Mail,
  BarChart3,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  CalendarCheck,
  MessageSquare,
  MessageCircle,
  Bot,
} from "lucide-react";

const ICON_MAP = {
  LayoutDashboard,
  Users,
  FileText,
  ClipboardCheck,
  BookOpen,
  Mail,
  BarChart3,
  Settings,
  AlertTriangle,
  CalendarCheck,
  MessageSquare,
  MessageCircle,
  Bot,
};

const NAV_GROUPS = [
  {
    labelKey: "nav.groupPeople",
    items: [
      { key: "dashboard", href: "/", icon: "LayoutDashboard" },
      { key: "users", href: "/users", icon: "Users" },
      { key: "invitations", href: "/invitations", icon: "Mail" },
    ],
  },
  {
    labelKey: "nav.groupOnboarding",
    items: [
      { key: "templates", href: "/templates", icon: "FileText" },
      { key: "checklists", href: "/checklists", icon: "ClipboardCheck" },
      { key: "meetings", href: "/meetings", icon: "CalendarCheck" },
      { key: "dialogues", href: "/dialogues", icon: "MessageSquare" },
    ],
  },
  {
    labelKey: "nav.groupKnowledge",
    items: [
      { key: "knowledgeBase", href: "/knowledge", icon: "BookOpen" },
    ],
  },
  {
    labelKey: "nav.groupInsights",
    items: [
      { key: "feedback", href: "/feedback", icon: "MessageCircle" },
      { key: "escalations", href: "/escalations", icon: "AlertTriangle" },
      { key: "analytics", href: "/analytics", icon: "BarChart3" },
    ],
  },
  {
    labelKey: "nav.groupSystem",
    items: [
      { key: "settings", href: "/settings", icon: "Settings" },
    ],
  },
];

export function Sidebar() {
  const t = useTranslations();
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const isActive = (href: string) =>
    pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <div
      className={cn(
        "flex h-screen flex-col border-r bg-card text-card-foreground transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Header */}
      <div className="flex h-16 shrink-0 items-center justify-between border-b px-3">
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="flex size-7 items-center justify-center rounded-lg bg-primary">
              <Bot className="size-4 text-primary-foreground" />
            </div>
            <span className="font-semibold">{t("nav.appName")}</span>
          </div>
        )}
        <div className={cn("flex items-center gap-1", collapsed && "mx-auto")}>
          {!collapsed && <LanguageSwitcher />}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hover:bg-muted rounded-lg p-1.5 transition-colors"
          >
            {collapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
          </button>
        </div>
      </div>

      {/* User info */}
      {!collapsed && user && (
        <div className="border-b px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex size-8 items-center justify-center rounded-full bg-primary/10">
              <span className="text-primary text-xs font-semibold">
                {user.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium">{user.email}</p>
              <p className="text-muted-foreground text-xs capitalize">{user.role?.toLowerCase()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <TooltipProvider>
        <nav className="flex-1 overflow-y-auto py-3">
          {NAV_GROUPS.map((group) => (
            <div key={group.labelKey} className={cn("mb-2", collapsed ? "px-2" : "px-3")}>
              {!collapsed && (
                <p className="text-muted-foreground mb-1 px-2 text-xs font-medium uppercase tracking-wider">
                  {t(group.labelKey as Parameters<typeof t>[0])}
                </p>
              )}
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const active = isActive(item.href);
                  const IconComponent = ICON_MAP[item.icon as keyof typeof ICON_MAP];
                  const name = t(`nav.${item.key}` as Parameters<typeof t>[0]);
                  return (
                    <Tooltip key={item.href}>
                      <TooltipTrigger asChild>
                        <Link
                          href={item.href}
                          className={cn(
                            "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
                            active
                              ? "bg-primary text-primary-foreground"
                              : "text-muted-foreground hover:bg-muted hover:text-foreground",
                            collapsed && "justify-center",
                          )}
                        >
                          {IconComponent && (
                            <IconComponent
                              className={cn(
                                "size-4 shrink-0",
                                active ? "text-primary-foreground" : "",
                              )}
                            />
                          )}
                          {!collapsed && <span className="truncate">{name}</span>}
                        </Link>
                      </TooltipTrigger>
                      {collapsed && (
                        <TooltipContent side="right">
                          <p>{name}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </TooltipProvider>

      {/* Footer */}
      <TooltipProvider>
        <div className="border-t p-3">
          <div className={cn("flex items-center gap-2", collapsed ? "justify-center" : "")}>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={handleLogout}
                  className={cn(
                    "text-muted-foreground hover:bg-muted hover:text-foreground flex flex-1 items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
                    collapsed && "flex-none justify-center",
                  )}
                >
                  <LogOut className="size-4 shrink-0" />
                  {!collapsed && <span>{t("nav.logout")}</span>}
                </button>
              </TooltipTrigger>
              {collapsed && (
                <TooltipContent side="right">
                  <p>{t("nav.logout")}</p>
                </TooltipContent>
              )}
            </Tooltip>
            {!collapsed && <ThemeSwitcher />}
          </div>
        </div>
      </TooltipProvider>
    </div>
  );
}
