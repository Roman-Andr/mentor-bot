import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SearchInput } from "@/components/ui/search-input";

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterDefinition {
  type: "search" | "select" | "reset";
  key?: string;
  value?: string;
  options?: FilterOption[];
  onChange?: (value: string) => void;
  placeholder?: string;
  onReset?: () => void;
  label?: string;
}

interface TableFiltersProps {
  filters: FilterDefinition[];
}

export function TableFilters({ filters }: TableFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {filters.map((filter, index) => {
        if (filter.type === "search") {
          return (
            <SearchInput
              key={index}
              placeholder={filter.placeholder}
              value={filter.value || ""}
              onChange={filter.onChange || (() => {})}
            />
          );
        }
        
        if (filter.type === "select" && filter.options) {
          return (
            <Select
              key={index}
              value={filter.value || ""}
              onChange={filter.onChange || (() => {})}
              options={filter.options}
            />
          );
        }
        
        if (filter.type === "reset") {
          return (
            <Button
              key={index}
              variant="outline"
              onClick={filter.onReset}
            >
              {filter.label || "Reset"}
            </Button>
          );
        }
        
        return null;
      })}
    </div>
  );
}

// Predefined filter builders
export const buildSearchFilter = (
  value: string,
  onChange: (value: string) => void,
  placeholder = "Search..."
): FilterDefinition => ({
  type: "search",
  value,
  onChange,
  placeholder,
});

export const buildSelectFilter = (
  key: string,
  value: string,
  onChange: (value: string) => void,
  options: FilterOption[]
): FilterDefinition => ({
  type: "select",
  key,
  value,
  onChange,
  options,
});

export const buildResetFilter = (
  onReset: () => void,
  label = "Reset"
): FilterDefinition => ({
  type: "reset",
  onReset,
  label,
});
