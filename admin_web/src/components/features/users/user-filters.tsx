import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLES_WITH_ALL } from "@/lib/constants";

interface UserFiltersProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  roleFilter: string;
  onRoleFilterChange: (value: string) => void;
  departmentFilter: string;
  onDepartmentFilterChange: (value: string) => void;
  departments?: { id: number; name: string }[];
}

export function UserFilters({
  searchQuery,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  departmentFilter,
  onDepartmentFilterChange,
  departments = [],
}: UserFiltersProps) {
  const departmentOptions = [
    { value: "ALL", label: "Все отделы" },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];
  return (
    <Card>
      <CardHeader>
        <CardTitle>Фильтры</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-4">
          <SearchInput
            placeholder="Поиск по имени или email..."
            value={searchQuery}
            onChange={onSearchChange}
          />
          <Select
            value={roleFilter}
            onChange={(e) => onRoleFilterChange(e.target.value)}
            options={ROLES_WITH_ALL}
          />
          <Select
            value={departmentFilter}
            onChange={(e) => onDepartmentFilterChange(e.target.value)}
            options={departmentOptions}
          />
          <Button variant="outline">Сбросить</Button>
        </div>
      </CardContent>
    </Card>
  );
}
