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
    <div className="flex flex-col gap-2 w-full sm:flex-row sm:items-center sm:flex-wrap">
      <Select
        value={typeFilter}
        onChange={(value) => onTypeFilterChange(value as FeedbackType | "all")}
        options={typeOptions}
        className="w-full sm:w-auto"
      />
      <Select
        value={anonymityFilter}
        onChange={(value) => onAnonymityFilterChange(value as "all" | "anonymous" | "attributed")}
        options={anonymityOptions}
        className="w-full sm:w-auto"
      />
      <Button variant="outline" onClick={onResetFilters} className="w-full sm:w-auto">
        {t("common.clear")}
      </Button>
    </div>
  );
}
