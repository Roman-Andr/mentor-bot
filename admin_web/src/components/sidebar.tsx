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
  BookOpen,
  Mail,
  BarChart3,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const navigation = [
  { name: "Дашборд", href: "/", icon: LayoutDashboard },
  { name: "Пользователи", href: "/users", icon: Users },
  { name: "Шаблоны", href: "/templates", icon: FileText },
  { name: "База знаний", href: "/knowledge", icon: BookOpen },
  { name: "Приглашения", href: "/invitations", icon: Mail },
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
          "flex flex-col h-screen bg-slate-900 text-white transition-all duration-300",
          collapsed ? "w-16" : "w-64",
        )}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800">
          {!collapsed && (
            <span className="text-lg font-semibold">Ментор-бот</span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>

        {!collapsed && user && (
          <div className="px-4 py-3 border-b border-slate-800">
            <div className="text-sm text-slate-400">Вошли как:</div>
            <div className="font-medium truncate">{user.email}</div>
          </div>
        )}

        <nav className="flex-1 py-4 space-y-1 px-2">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white",
                  collapsed && "justify-center",
                )}
                title={collapsed ? item.name : undefined}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button
            onClick={handleLogout}
            className={cn(
              "flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors",
              collapsed && "justify-center",
            )}
            title={collapsed ? "Выйти" : undefined}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span>Выйти</span>}
          </button>
        </div>
      </div>
    </>
  );
}
