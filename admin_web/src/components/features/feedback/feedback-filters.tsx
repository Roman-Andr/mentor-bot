import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { useTranslations } from "@/hooks/use-translations";
import { getFeedbackTypeOptions, getAnonymityOptions } from "@/lib/constants";
import type { FeedbackType } from "@/types";

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
