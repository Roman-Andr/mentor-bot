"use client";

import { cn } from "@/lib/utils";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface TabSwitcherProps {
  tabs: TabItem[];
  paramName?: string;
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
}

export function TabSwitcher({ tabs, paramName = "tab", activeTab: controlledActiveTab, onTabChange: controlledOnTabChange }: TabSwitcherProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const activeTab = controlledActiveTab ?? (searchParams.get(paramName) || tabs[0]?.id);

  const handleTabChange = (tabId: string) => {
    if (controlledOnTabChange) {
      controlledOnTabChange(tabId);
      return;
    }
    const params = new URLSearchParams(searchParams.toString());
    params.set(paramName, tabId);
    router.replace(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="flex rounded-md border">
      {tabs.map((tab, i) => {
        const isFirst = i === 0;
        const isLast = i === tabs.length - 1;
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            className={cn(
              "flex cursor-pointer items-center gap-1.5 px-3 py-1.5 text-sm font-medium transition-colors",
              isFirst && "rounded-l-md",
              isLast && "rounded-r-md",
              activeTab === tab.id
                ? "bg-primary text-primary-foreground"
                : "bg-background text-muted-foreground hover:bg-muted",
            )}
            onClick={() => handleTabChange(tab.id)}
          >
            {Icon && <Icon className="size-4" />}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
