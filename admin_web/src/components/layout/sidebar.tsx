"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
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
} from "lucide-react";

const navigation = [
  { name: "Дашборд", href: "/", icon: LayoutDashboard },
  { name: "Пользователи", href: "/users", icon: Users },
  { name: "Шаблоны", href: "/templates", icon: FileText },
  { name: "Чек-листы", href: "/checklists", icon: ClipboardCheck },
  { name: "База знаний", href: "/knowledge", icon: BookOpen },
  { name: "Приглашения", href: "/invitations", icon: Mail },
  { name: "Запросы", href: "/escalations", icon: AlertTriangle },
  { name: "Встречи", href: "/meetings", icon: CalendarCheck },
  { name: "Аналитика", href: "/analytics", icon: BarChart3 },
  { name: "Настройки", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();

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
          {!collapsed && <span className="text-lg font-semibold">Ментор-бот</span>}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="rounded-lg p-1.5 transition-colors hover:bg-slate-800"
          >
            {collapsed ? <ChevronRight className="size-5" /> : <ChevronLeft className="size-5" />}
          </button>
        </div>

        {!collapsed && user && (
          <div className="border-b border-slate-800 px-4 py-3">
            <div className="text-sm text-slate-400">Вошли как:</div>
            <div className="truncate font-medium">{user.email}</div>
          </div>
        )}

        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
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
                <item.icon className="size-5 shrink-0" />
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
            title={collapsed ? "Выйти" : undefined}
          >
            <LogOut className="size-5 shrink-0" />
            {!collapsed && <span>Выйти</span>}
          </button>
        </div>
      </div>
    </>
  );
}
