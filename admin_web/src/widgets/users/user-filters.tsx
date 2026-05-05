import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { SearchInput } from "@/shared/ui/search-input";
import { Select } from "@/shared/ui/select";
import { Card, CardContent } from "@/shared/ui/card";
import { ROLES_WITH_ALL } from "@/shared/lib/constants";

interface UserFiltersProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  roleFilter: string;
  onRoleFilterChange: (value: string) => void;
  departmentFilter: string;
  onDepartmentFilterChange: (value: string) => void;
  onReset: () => void;
  departments?: { id: number; name: string }[];
}

export function UserFilters({
  searchQuery,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  departmentFilter,
  onDepartmentFilterChange,
  onReset,
  departments = [],
}: UserFiltersProps) {
  const t = useTranslations();

  const departmentOptions = [
    { value: "ALL", label: t("users.allDepartments") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];
  return (
    <Card>
      <CardContent className="flex flex-wrap items-center gap-2 py-4">
        <SearchInput
          placeholder={t("users.searchByNameOrEmail")}
          value={searchQuery}
          onChange={onSearchChange}
        />
        <Select value={roleFilter} onChange={onRoleFilterChange} options={ROLES_WITH_ALL} />
        <Select
          value={departmentFilter}
          onChange={onDepartmentFilterChange}
          options={departmentOptions}
        />
        <Button variant="outline" onClick={onReset}>
          {t("common.reset")}
        </Button>
      </CardContent>
    </Card>
  );
}
