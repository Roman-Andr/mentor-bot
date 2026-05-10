import { useTranslations } from "@/shared/hooks/use-translations";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { DEPARTMENT_COLORS } from "@/shared/lib/constants";
import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

const FALLBACK_COLORS = [
  "bg-blue-500 dark:bg-blue-600",
  "bg-purple-500 dark:bg-purple-600",
  "bg-green-500 dark:bg-green-600",
  "bg-orange-500 dark:bg-orange-600",
  "bg-pink-500 dark:bg-pink-600",
  "bg-cyan-500 dark:bg-cyan-600",
  "bg-red-500 dark:bg-red-600",
];

interface DepartmentBreakdownProps {
  departments: Record<string, number>;
  href?: string;
}

export function DepartmentBreakdown({ departments, href }: DepartmentBreakdownProps) {
  const t = useTranslations();
  const departmentEntries = Object.entries(departments);
  const totalDeptCount = departmentEntries.reduce((sum, [, count]) => sum + count, 0);

  const card = (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle>{t("dashboard.byDepartment")}</CardTitle>
        {href && (
          <Link href={href}>
            <Button variant="ghost" size="sm" className="gap-1 text-xs">
              <ExternalLink className="size-3" />
              <span className="hidden sm:inline">{t("common.viewAll")}</span>
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {departmentEntries.length > 0 && totalDeptCount > 0 ? (
            departmentEntries.map(([dept, count], index) => {
              const color =
                DEPARTMENT_COLORS[dept] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
              return (
                <div key={dept} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`size-3 rounded-full ${color}`} />
                    <span className="text-sm">{dept}</span>
                  </div>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              );
            })
          ) : (
            <p className="py-4 text-center text-sm text-muted-foreground">{t("common.noData")}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return card;
}
