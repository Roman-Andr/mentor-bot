import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DEPARTMENT_COLORS } from "@/lib/constants";

const FALLBACK_COLORS = [
  "bg-blue-500",
  "bg-purple-500",
  "bg-green-500",
  "bg-orange-500",
  "bg-pink-500",
  "bg-cyan-500",
  "bg-red-500",
];

interface DepartmentBreakdownProps {
  departments: Record<string, number>;
}

export function DepartmentBreakdown({ departments }: DepartmentBreakdownProps) {
  const departmentEntries = Object.entries(departments);
  const totalDeptCount = departmentEntries.reduce((sum, [, count]) => sum + count, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>По отделам</CardTitle>
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
            <p className="text-muted-foreground py-4 text-center text-sm">Нет данных</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
