import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Plus } from "lucide-react";
import { CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface EntityPageHeaderProps<TItem> {
  title: string;
  description?: string;
  showSearch?: boolean;
  searchPlaceholder?: string;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  filters?: React.ReactNode;
  additionalActions?: React.ReactNode;
  createButtonLabel?: string;
  onCreateOpen: () => void;
}

export function EntityPageHeader<TItem>({
  title,
  description,
  showSearch = true,
  searchPlaceholder,
  searchQuery,
  onSearchChange,
  filters,
  additionalActions,
  createButtonLabel,
  onCreateOpen,
}: EntityPageHeaderProps<TItem>) {
  return (
    <CardHeader>
      <div className="flex items-center justify-between gap-4">
        <div>
          <CardTitle>{title}</CardTitle>
          {description && (
            <CardDescription className="mt-1">{description}</CardDescription>
          )}
        </div>
        <div className="flex items-center gap-2">
          {showSearch && (
            <SearchInput
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={onSearchChange}
            />
          )}
          {filters}
          {additionalActions}
          <Button onClick={onCreateOpen} className="gap-2">
            <Plus className="size-4" />
            {createButtonLabel}
          </Button>
        </div>
      </div>
    </CardHeader>
  );
}
