import { Building2, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTranslations } from "@/hooks/use-translations";

type Tab = "users" | "departments";

interface UsersTabSwitcherProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}

export function UsersTabSwitcher({ activeTab, onTabChange }: UsersTabSwitcherProps) {
  const t = useTranslations();

  return (
    <div className="flex rounded-md border">
      <button
        className={cn(
          "flex cursor-pointer items-center gap-1.5 rounded-l-md px-3 py-1.5 text-sm font-medium transition-colors",
          activeTab === "users"
            ? "bg-primary text-primary-foreground"
            : "bg-background text-muted-foreground hover:bg-muted",
        )}
        onClick={() => onTabChange("users")}
      >
        <Users className="size-4" />
        {t("users.title")}
      </button>
      <button
        className={cn(
          "flex cursor-pointer items-center gap-1.5 rounded-r-md px-3 py-1.5 text-sm font-medium transition-colors",
          activeTab === "departments"
            ? "bg-primary text-primary-foreground"
            : "bg-background text-muted-foreground hover:bg-muted",
        )}
        onClick={() => onTabChange("departments")}
      >
        <Building2 className="size-4" />
        {t("departments.title")}
      </button>
    </div>
  );
}
