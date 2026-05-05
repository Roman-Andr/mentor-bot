import { Button } from "@/shared/ui/button";
import { Select } from "@/shared/ui/select";
import { useTranslations } from "@/shared/hooks/use-translations";
import { getFeedbackTypeOptions, getAnonymityOptions } from "@/shared/lib/constants";
import type { FeedbackType } from "@/shared/types";

interface FeedbackFiltersProps {
  typeFilter: FeedbackType | "all";
  anonymityFilter: "all" | "anonymous" | "attributed";
  onTypeFilterChange: (value: FeedbackType | "all") => void;
  onAnonymityFilterChange: (value: "all" | "anonymous" | "attributed") => void;
  onResetFilters: () => void;
}

export function FeedbackFilters({
  typeFilter,
  anonymityFilter,
  onTypeFilterChange,
  onAnonymityFilterChange,
  onResetFilters,
}: FeedbackFiltersProps) {
  const t = useTranslations();

  const typeOptions = getFeedbackTypeOptions(t);
  const anonymityOptions = getAnonymityOptions(t);

  return (
    <div className="flex items-center gap-2">
      <Select
        value={typeFilter}
        onChange={(value) => onTypeFilterChange(value as FeedbackType | "all")}
        options={typeOptions}
      />
      <Select
        value={anonymityFilter}
        onChange={(value) => onAnonymityFilterChange(value as "all" | "anonymous" | "attributed")}
        options={anonymityOptions}
      />
      <Button variant="outline" onClick={onResetFilters}>
        {t("common.clear")}
      </Button>
    </div>
  );
}
