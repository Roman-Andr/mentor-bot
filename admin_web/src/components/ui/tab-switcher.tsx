import { cn } from "@/lib/utils";

interface TabItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface TabSwitcherProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (id: string) => void;
}

export function TabSwitcher({ tabs, activeTab, onTabChange }: TabSwitcherProps) {
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
              "flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium transition-colors",
              isFirst && "rounded-l-md",
              isLast && "rounded-r-md",
              activeTab === tab.id
                ? "bg-primary text-primary-foreground"
                : "bg-background text-muted-foreground hover:bg-muted",
            )}
            onClick={() => onTabChange(tab.id)}
          >
            {Icon && <Icon className="size-4" />}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
