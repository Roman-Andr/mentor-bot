"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { LanguageSwitcher } from "./language-switcher";
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
} from "lucide-react";

const iconMap = {
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
};

export function Sidebar() {
  const t = useTranslations("nav");
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();

  const navigation = [
    { name: t("dashboard"), href: "/", icon: "LayoutDashboard" },
    { name: t("users"), href: "/users", icon: "Users" },
    { name: t("templates"), href: "/templates", icon: "FileText" },
    { name: t("checklists"), href: "/checklists", icon: "ClipboardCheck" },
    { name: t("knowledgeBase"), href: "/knowledge", icon: "BookOpen" },
    { name: t("dialogues"), href: "/dialogues", icon: "MessageSquare" },
    { name: t("invitations"), href: "/invitations", icon: "Mail" },
    { name: t("escalations"), href: "/escalations", icon: "AlertTriangle" },
    { name: t("meetings"), href: "/meetings", icon: "CalendarCheck" },
    { name: t("analytics"), href: "/analytics", icon: "BarChart3" },
    { name: t("settings"), href: "/settings", icon: "Settings" },
  ];

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <>
      <div
        className={cn(
          "flex h-screen flex-col bg-slate-900 text-white transition-all duration-300",
          collapsed ? "w-16" : "w-64",
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-4">
          {!collapsed && <span className="text-lg font-semibold">{t("appName")}</span>}
          <div className="flex items-center gap-2">
            {!collapsed && <LanguageSwitcher />}
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="rounded-lg p-1.5 transition-colors hover:bg-slate-800"
            >
              {collapsed ? <ChevronRight className="size-5" /> : <ChevronLeft className="size-5" />}
            </button>
          </div>
        </div>

        {!collapsed && user && (
          <div className="border-b border-slate-800 px-4 py-3">
            <div className="text-sm text-slate-400">{t("loggedInAs")}:</div>
            <div className="truncate font-medium">{user.email}</div>
          </div>
        )}

        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            const IconComponent = iconMap[item.icon as keyof typeof iconMap];
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors",
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white",
                  collapsed && "justify-center",
                )}
                title={collapsed ? item.name : undefined}
              >
                {IconComponent && <IconComponent className="size-5 shrink-0" />}
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-800 p-4">
          <button
            onClick={handleLogout}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-slate-400 transition-colors hover:bg-slate-800 hover:text-white",
              collapsed && "justify-center",
            )}
            title={collapsed ? t("logout") : undefined}
          >
            <LogOut className="size-5 shrink-0" />
            {!collapsed && <span>{t("logout")}</span>}
          </button>
        </div>
      </div>
    </>
  );
}
