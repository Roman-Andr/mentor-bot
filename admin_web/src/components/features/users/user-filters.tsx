import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { ROLES_WITH_ALL } from "@/lib/constants";

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
  const t = useTranslations("users");
  const tCommon = useTranslations("common");

  const departmentOptions = [
    { value: "ALL", label: t("allDepartments") },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];
  return (
    <Card>
      <CardContent className="flex flex-wrap items-center gap-2 py-4">
        <SearchInput
          placeholder={t("searchByNameOrEmail")}
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
          {tCommon("reset")}
        </Button>
      </CardContent>
    </Card>
  );
}
